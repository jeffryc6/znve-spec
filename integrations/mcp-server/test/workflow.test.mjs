import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import * as os from 'node:os';
import { createHash } from 'node:crypto';
import { Workflow, WorkflowError, validate } from '../dist/workflow.js';

const sha = x => createHash('sha256').update(x).digest('hex');
const schemaDir = new URL('../../../schemas/', import.meta.url);
const specification = (argv = ['-e', 'process.exit(0)']) => ({
  id:'feature', revision:1, objective:'Regression is satisfied',
  allowed_files:['src/value.js'], required_files:['tests/value.mjs'],
  criteria:[{id:'regression',description:'The declared real check passes',required:true,check_id:'unit'}],
  checks:[{id:'unit',runner:'node',argv,timeout_ms:1000}], assumptions:[]
});

async function fixture(fn, spec = specification()) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(),'znve-workflow-'));
  const oldApproval = process.env.ZNVE_APPROVED_SPECS;
  const oldRunners = process.env.ZNVE_RUNNERS;
  try {
    await fs.mkdir(path.join(root,'src')); await fs.mkdir(path.join(root,'tests'));
    await fs.writeFile(path.join(root,'src/value.js'),'export const value=1;');
    await fs.writeFile(path.join(root,'tests/value.mjs'),'// test input');
    const raw = JSON.stringify(spec);
    await fs.writeFile(path.join(root,'spec.json'),raw);
    process.env.ZNVE_APPROVED_SPECS = sha(raw);
    process.env.ZNVE_RUNNERS = JSON.stringify({node:process.execPath});
    const io = {root,resolve:async (file,write=false) => {
      const absolute=path.resolve(root,file), rel=path.relative(root,absolute);
      if (rel.startsWith('..') || path.isAbsolute(rel)) throw new WorkflowError('OUTSIDE_WORKSPACE','outside');
      if (rel.split(path.sep).some(p=>['.env','.znve'].includes(p))) throw new WorkflowError('SECRET_DENIED','protected');
      return absolute;
    }};
    const workflow = new Workflow(io);
    await fn({root,workflow,io,spec,call:(operation,payload={})=>workflow.dispatch(operation,{spec_path:'spec.json',...payload})});
  } finally {
    if(oldApproval===undefined) delete process.env.ZNVE_APPROVED_SPECS; else process.env.ZNVE_APPROVED_SPECS=oldApproval;
    if(oldRunners===undefined) delete process.env.ZNVE_RUNNERS; else process.env.ZNVE_RUNNERS=oldRunners;
    await fs.rm(root,{recursive:true,force:true,maxRetries:5,retryDelay:50});
  }
}
const rejects = (fn,code) => assert.rejects(fn,e=>e.code===code);

test('structure is distinct from host approval; an empty gate cannot accept',()=>fixture(async ({call})=>{
  process.env.ZNVE_APPROVED_SPECS='';
  const result=await call('spec_validate'); assert.equal(result.structurally_valid,true); assert.equal(result.host_approved,false);
  assert.equal((await call('gate',{evidence_ids:[]})).accepted,false);
  await rejects(()=>call('verify',{check_id:'unit'}),'SPEC_NOT_APPROVED');
  await rejects(()=>call('claim',{owner:'worker',files:['src/value.js'],ttl_seconds:60}),'SPEC_NOT_APPROVED');
}));

test('preflight reports actual missing files and runners',()=>fixture(async ({root,call})=>{
  await fs.rm(path.join(root,'tests/value.mjs')); process.env.ZNVE_RUNNERS='{}';
  const r=await call('preflight'); assert.equal(r.ready,false); assert.deepEqual(r.missing_files,['tests/value.mjs']); assert.deepEqual(r.unavailable_runners,['node']);
  assert.equal(r.base_hashes['src/value.js'],sha('export const value=1;'));
  await rejects(()=>call('verify',{check_id:'unit'}),'NOT_FOUND');
}));

test('runner absent is explicit; no mock fallback',()=>fixture(async ({call})=>{
  process.env.ZNVE_RUNNERS='{}'; await rejects(()=>call('verify',{check_id:'unit'}),'EXECUTION_DISABLED');
}));

test('real passing process yields evidence; a new server can read it',()=>fixture(async ({call,io})=>{
  const r=await call('verify',{check_id:'unit'}); assert.equal(r.evidence.state,'passed'); assert.equal(r.evidence.exit_code,0);
  const other=new Workflow(io);
  const gate=await other.dispatch('gate',{spec_path:'spec.json',evidence_ids:[r.evidence.id]}); assert.equal(gate.accepted,true);
  validate(r.evidence,JSON.parse(await fs.readFile(new URL('evidence.schema.json',schemaDir),'utf8')));
}));

test('nonzero process cannot close a criterion',()=>fixture(async ({call})=>{
  const r=await call('verify',{check_id:'unit'}); assert.equal(r.evidence.state,'failed'); assert.equal(r.evidence.exit_code,7);
  assert.equal((await call('gate',{evidence_ids:[r.evidence.id]})).accepted,false);
},specification(['-e','process.exit(7)'])));

test('timeout is a failed execution, not success',()=>fixture(async ({call})=>{
  const r=await call('verify',{check_id:'unit'}); assert.equal(r.evidence.state,'failed'); assert.equal(r.evidence.timed_out,true);
},specification(['-e','setInterval(()=>{},100)'])));

test('raw output and inherited credentials never enter evidence',()=>fixture(async ({call,root})=>{
  process.env.ZNVE_TEST_API_KEY='CANARY-MUST-NOT-PASS';
  try {
    const r=await call('verify',{check_id:'unit'});
    assert.equal(r.evidence.state,'passed'); assert.ok(r.evidence.output_bytes>0);
    assert.ok(!JSON.stringify(r).includes('CANARY-OUTPUT'));
    const stored=await fs.readFile(path.join(root,'.znve/state',`evidence-${r.evidence.id}.json`),'utf8');
    assert.ok(!stored.includes('CANARY-OUTPUT')); assert.ok(!stored.includes('CANARY-MUST-NOT-PASS'));
  } finally {delete process.env.ZNVE_TEST_API_KEY;}
},specification(['-e','if(process.env.ZNVE_TEST_API_KEY)process.exit(9); console.log("CANARY-OUTPUT")'])));

test('output overflow fails with bounded captured data',()=>fixture(async ({call})=>{
  const r=await call('verify',{check_id:'unit'}); assert.equal(r.evidence.state,'failed'); assert.equal(r.evidence.output_limited,true);
},specification(['-e','process.stdout.write("x".repeat(100000))'])));

test('code edit invalidates evidence and checkpoint',()=>fixture(async ({call,root})=>{
  const r=await call('verify',{check_id:'unit'});
  const cp=await call('checkpoint',{pending:['Review integration'],evidence_ids:[r.evidence.id]});
  assert.equal((await call('resume',{checkpoint_id:cp.checkpoint.id})).validity,'current');
  await fs.writeFile(path.join(root,'src/value.js'),'changed');
  assert.equal((await call('gate',{evidence_ids:[r.evidence.id]})).accepted,false);
  const resumed=await call('resume',{checkpoint_id:cp.checkpoint.id}); assert.equal(resumed.validity,'stale'); assert.equal(resumed.evidence[0].validity,'stale');
}));

test('spec edit invalidates approval and old evidence',()=>fixture(async ({root,call,spec})=>{
  const r=await call('verify',{check_id:'unit'});
  spec.revision=2; await fs.writeFile(path.join(root,'spec.json'),JSON.stringify(spec));
  assert.equal((await call('gate',{evidence_ids:[r.evidence.id]})).accepted,false);
  await rejects(()=>call('verify',{check_id:'unit'}),'SPEC_NOT_APPROVED');
}));

test('changes during a check yield stale evidence',()=>fixture(async ({call})=>{
  const r=await call('verify',{check_id:'unit'}); assert.equal(r.evidence.validity,'stale');
  assert.equal((await call('gate',{evidence_ids:[r.evidence.id]})).accepted,false);
},specification(['-e','require("fs").writeFileSync("src/value.js","changed during check")'])));

test('unresolved material assumption blocks acceptance even with green checks',()=>{
  const spec=specification(); spec.assumptions=[{id:'a',statement:'Remote format exists',origin:'inferred',evidence:'none',source:'hypothesis',material:true}];
  return fixture(async ({call})=>{const r=await call('verify',{check_id:'unit'});const gate=await call('gate',{evidence_ids:[r.evidence.id]});assert.equal(gate.accepted,false);assert.deepEqual(gate.unresolved_assumptions,['a']);},spec);
});

test('claims serialize across server instances and reject overlap',()=>fixture(async ({call,io})=>{
  const other=new Workflow(io);
  const results=await Promise.allSettled([call('claim',{owner:'a',files:['src/value.js'],ttl_seconds:60}),other.dispatch('claim',{spec_path:'spec.json',owner:'b',files:['src/value.js'],ttl_seconds:60})]);
  assert.equal(results.filter(r=>r.status==='fulfilled').length,1);
  assert.ok(['BUSY','CONFLICT'].includes(results.find(r=>r.status==='rejected').reason.code));
}));

test('apply enforces scope, base hash and live claim; old evidence becomes stale',()=>fixture(async ({call,root})=>{
  const ev=await call('verify',{check_id:'unit'});
  await rejects(()=>call('claim',{owner:'a',files:['outside.js'],ttl_seconds:60}),'OUT_OF_SCOPE');
  const {claim}=await call('claim',{owner:'a',files:['src/value.js'],ttl_seconds:60});
  await rejects(()=>call('apply',{claim_id:claim.id,file:'src/value.js',expected_hash:'missing',content:'wrong'}),'CONFLICT');
  await rejects(()=>call('apply',{claim_id:claim.id,file:'tests/value.mjs',expected_hash:'missing',content:'wrong'}),'OUT_OF_SCOPE');
  const old=await fs.readFile(path.join(root,'src/value.js'));
  const r=await call('apply',{claim_id:claim.id,file:'src/value.js',expected_hash:sha(old),content:'new value'});
  assert.equal(r.hash,sha('new value')); assert.equal(await fs.readFile(path.join(root,'src/value.js'),'utf8'),'new value');
  assert.equal((await call('gate',{evidence_ids:[ev.evidence.id]})).accepted,false);
}));

test('expired reservation cannot write',()=>fixture(async ({call,root})=>{
  const {claim}=await call('claim',{owner:'a',files:['src/value.js'],ttl_seconds:60});
  const file=path.join(root,'.znve/state',`claim-${claim.id}.json`); claim.expires_at=0; await fs.writeFile(file,JSON.stringify(claim));
  await rejects(()=>call('apply',{claim_id:claim.id,file:'src/value.js',expected_hash:'missing',content:'bad'}),'CONFLICT');
}));

test('new file apply cannot overwrite existing content',()=>fixture(async ({root,call})=>{
  await fs.rm(path.join(root,'src/value.js'));
  const {claim}=await call('claim',{owner:'a',files:['src/value.js'],ttl_seconds:60});
  await call('apply',{claim_id:claim.id,file:'src/value.js',expected_hash:'missing',content:'created'});
  await rejects(()=>call('apply',{claim_id:claim.id,file:'src/value.js',expected_hash:'missing',content:'overwrite'}),'CONFLICT');
}));

test('strict schemas reject unknown payload fields and missing checks',()=>fixture(async ({call,root,spec})=>{
  await rejects(()=>call('gate',{evidence_ids:[],accepted:true}),'BAD_ARGUMENT');
  spec.criteria[0].check_id='absent'; await fs.writeFile(path.join(root,'spec.json'),JSON.stringify(spec));
  await rejects(()=>call('spec_validate'),'BAD_ARGUMENT');
}));

for (const kind of ['duplicate-check','no-required','self-scope','traversal','absolute','secret','aliased-input','unknown-field']) {
  test(`spec rejects ${kind}`,()=>fixture(async ({spec,root,call})=>{
    if(kind==='duplicate-check') spec.checks.push({...spec.checks[0]});
    if(kind==='no-required') spec.criteria[0].required=false;
    if(kind==='self-scope') spec.allowed_files.push('spec.json');
    if(kind==='traversal') spec.allowed_files.push('../out.js');
    if(kind==='absolute') spec.allowed_files.push(path.join(root,'absolute.js'));
    if(kind==='secret') spec.required_files.push('.env');
    if(kind==='aliased-input') spec.required_files.push('src/value.js');
    if(kind==='unknown-field') spec.approved=true;
    await fs.writeFile(path.join(root,'spec.json'),JSON.stringify(spec));
    await assert.rejects(()=>call('spec_validate'));
  }));
}

test('stall detector distinguishes repetition from declared new evidence',()=>fixture(async ({workflow})=>{
  const events=Array.from({length:3},()=>({action:'search missing test',new_evidence:false}));
  assert.equal((await workflow.dispatch('stall_detect',{events,window:3})).stalled,true);
  events[2].new_evidence=true; assert.equal((await workflow.dispatch('stall_detect',{events,window:3})).stalled,false);
}));

test('missing evidence cannot be supplied as a success string',()=>fixture(async ({call})=>{
  await assert.rejects(()=>call('gate',{evidence_ids:['fake-success']}));
  await rejects(()=>call('gate',{evidence_ids:['../../outside']}),'BAD_ARGUMENT');
}));

test('internal state junction is rejected',async t=>fixture(async ({root,call})=>{
  const outside=await fs.mkdtemp(path.join(os.tmpdir(),'znve-outside-'));
  try {
    try {await fs.symlink(outside,path.join(root,'.znve'),process.platform==='win32'?'junction':'dir');}
    catch(e){if(['EPERM','EACCES'].includes(e.code)){t.skip('symlink privilege unavailable');return;}throw e;}
    await rejects(()=>call('checkpoint',{pending:[],evidence_ids:[]}),'OUTSIDE_WORKSPACE');
    assert.deepEqual(await fs.readdir(outside),[]);
  } finally {await fs.rm(outside,{recursive:true,force:true});}
}));
