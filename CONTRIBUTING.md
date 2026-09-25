# Contribuyendo a ZNVE (Proceso RFC)

Agradecemos las contribuciones de la comunidad. Para garantizar que ZNVE mantenga su rigor técnico y no se convierta en un repositorio disperso de prompts, toda mejora, adaptación a nuevos runtimes o ajuste conceptual debe tramitarse mediante una **RFC (Request for Comments)**.

## 🔄 El Ciclo de Vida de una RFC

1. **Bifurcar (Fork):** Clona el repositorio `znve-spec`.
2. **Crear Rama:** Crea una rama con el formato `rfc/nombre-de-propuesta`.
3. **Redactar Propuesta:** Copia `rfcs/0000-template.md` a `rfcs/XXXX-nombre-propuesta.md` (utiliza el siguiente número correlativo disponible).
4. **Abrir Pull Request:** Publica el PR con la etiqueta `RFC: Draft`.
5. **Revisión y Discusión:** La comunidad y los mantenedores evaluarán si la propuesta cumple con el principio de *Cero Ruido* y mínima huella.
6. **Aprobación / Fusión:** Una vez consensuada, el mantenedor principal fusionará el RFC y se incorporará a la siguiente versión semántica (SemVer) de la especificación.

## ⚖️ Criterios de Aceptación
- No debe añadir fricción innecesaria ni dependencias parásitas.
- Debe incluir un arnés o prueba atómica que valide la propuesta.
- Debe mantener el balance entre velocidad de desarrollo y disciplina arquitectónica.