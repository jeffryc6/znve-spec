<p align="right">
  <a href="https://translate.google.com/translate?sl=es&tl=en&u=https://github.com/jeffryc6/znve-spec/blob/main/case-studies/02-legacy-monolith-rescue/README.md">
    <img src="https://img.shields.io/badge/Translate_to-English-blue?style=flat-square&logo=googletranslate" alt="Translate to English">
  </a>
</p>

# Caso de Estudio 02: Rescate de Monolito Crítico sin Pruebas Unitarias

## Contexto y Dominio
Un sistema en producción gobernado por un archivo único de más de 2.000 líneas que ejecuta tareas críticas de negocio (sincronización, facturación o cálculo de cuotas). El archivo contenía funciones duplicadas y código aparentemente contradictorio que subsistía gracias al orden de evaluación del intérprete.

## El Riesgo
Cualquier intento convencional de "limpieza de código" asistido por IA rompía comportamientos emergentes no documentados de los cuales dependía la operación diaria de la empresa.

## Aplicación del Protocolo ZNVE (5 Fases)
1. **Fase 1 (Ingesta Pasiva):** La IA analizó el archivo en modo estrictamente de solo lectura, mapeando 14 efectos secundarios y 3 dependencias globales ocultas.
2. **Fase 2 (Reporte Forense):** Se documentó el contrato implícito del módulo y se explicaron las contradicciones funcionales como equilibrios accidentales del negocio.
3. **Fase 3 (Arnés Golden Master):** Se construyó una suite de pruebas de caja negra en un directorio aislado (`/tests/characterization/`). Se inyectaron 250 combinaciones de entradas reales y casos límite contra el código original intacto, congelando las salidas en snapshots inmutables.
4. **Fase 4 (Ejecución en Sombra):** Se diseñó el nuevo módulo desacoplado satisfaciendo el nuevo DTO. Se ejecutó una prueba dual inyectando las mismas entradas a ambos módulos: paridad funcional confirmada al 100% bit a bit.
5. **Fase 5 (Strangler Fig):** El módulo original fue reemplazado de manera gradual en producción con cero tiempo de inactividad y cero regresiones.

## Métricas de Impacto
- **Tiempo de inactividad (Downtime):** 0 segundos.
- **Regresiones en producción:** 0%.
- **Deuda técnica:** Reducción del 65% en líneas de código y erradicación total de variables globales.