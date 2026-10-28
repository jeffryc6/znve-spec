# Workflows compatibles

- Greenfield/In-flight: forensic → spec → execute --spec → verify.
- Hotfix: triage solo lectura → spec acotada → parche → regresión real → verify.
- Upgrade: breaking changes → spec del adaptador → implementación → paridad real.
- Legacy: forensic → harness intacto → spec → shadow run → conmutación autorizada.
- Hardening: audit solo lectura → spec → remediación → verify.

Los diez comandos previos siguen disponibles. Publicación, despliegue y acciones externas requieren su autorización propia. Git no revierte bases de datos ni llamadas externas.
