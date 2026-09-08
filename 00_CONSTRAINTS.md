# 00_CONSTRAINTS.md

*artHUB — Fase 0. Versión 0.1, septiembre 2026.*

> Las restricciones son input del diseño. Si un plan no entra acá, el que está mal es el plan.
> Todo lo marcado `[COMPLETAR]` es un dato que sólo tiene el operador. Mientras esté vacío, cualquier estimación de las fases 2 a 7 es ficción.

---

## 1. Tiempo del operador

Hay **dos presupuestos distintos** que compiten por las mismas horas, y confundirlos es el modo de falla típico de este proyecto:

| Presupuesto | Qué incluye | Horas/semana |
|---|---|---|
| Construcción | código, ingesta, specs, deploy | `[COMPLETAR]` |
| Presencia | leer la obra de la semana, abrir hilos, responder, moderar | `[COMPLETAR]` |

**Cómo medirlo (no estimarlo):** registrar una semana lectiva normal, con facultad y trabajo funcionando. Dos semanas es mejor que una. Una estimación optimista acá se propaga a todo el resto del plan.

**Regla derivada — la presencia se reserva primero.** Si una semana no alcanza para las dos cosas, se corta código, nunca presencia. Código atrasado se recupera; una semana sin anfitrión en un ágora de veinte personas no se recupera, porque el que entró y no encontró a nadie no vuelve.

**Consecuencia de sizing:** toda estimación de fases posteriores se hace contra horas de construcción, no contra tiempo de calendario. Un slice de "40 horas" con 6 horas semanales son siete semanas, no un mes.

**Riesgo estructural conocido:** el pipeline de ingesta TEI (sección 6 del concepto) es la tarea que más horas de construcción consume *y* la que más mantenimiento perpetuo genera. Es la primera candidata a recorte cuando el número de arriba resulte más chico de lo deseado.

---

## 2. Dinero

- **Techo mensual:** `[COMPLETAR]` USD/mes. Escribir el número que se puede pagar doce meses seguidos sin discutirlo con nadie, no el máximo tolerable un mes.
- **Piso conocido de la v1 (sólo texto):** dominio ~1 USD/mes, VPS chico con Postgres ~5–10, backups fuera del VPS ~1–2, correo transaccional en capa gratuita, TLS 0. Orden de magnitud: **10–15 USD/mes**.
- **Costos de una sola vez a presupuestar aparte:** generación de embeddings para alineación de traducciones (§6.1) y cualquier reproceso masivo del corpus.
- **Regla del costo marginal:** agregar una obra tiene que costar ≈0. Cualquier función cuyo costo crezca con los usuarios (archivos pesados, transcodificación, embeddings recalculados por versión, búsqueda vectorial gestionada) requiere una decisión explícita y registrada, no aparece de hecho.
- **No hay ingresos y no se buscan** (riesgo 9 del concepto). Si el costo supera el techo, se recorta alcance. Esa es la única palanca.

---

## 3. Fecha de muerte y de reevaluación

Dos puertas separadas, porque fallan por motivos distintos.

**Puerta técnica — cierra sola.** Si al final de la Fase 2 el spike de anclas (versionado + reanclaje difuso sobre una obra real, con una errata corregida de verdad) no funciona, el proyecto no arranca en esta forma. Fecha límite sugerida: **6 semanas desde hoy**. `[CONFIRMAR]`

**Puerta social — la que cuesta cerrar.** Métrica única: *hilos con más de tres respuestas por semana*, sostenido durante un mes, con al menos la mitad fuera de la obra destacada. Umbral y plazo: `[COMPLETAR]` (ej. 5 hilos/semana a los 6 meses del primer usuario público).

Si la puerta social no se cumple, hay dos salidas legítimas y ninguna es "seguir igual un poco más": reducir a biblioteca personal con anotación (que sigue siendo útil y cuesta nada de operar) o cerrar según la sección 5.

**Reevaluación:** trimestral, con fecha en el calendario. La fecha se escribe hoy y se le dice a otra persona, porque el sesgo por defecto de un proyecto propio es sostenerlo después de muerto.

---

## 4. Restricciones legales (condicionan el producto, no son trámite)

*Nada de esto es asesoramiento legal. Los plazos y la figura del responsable conviene confirmarlos antes de publicar la primera obra.*

- **Jurisdicción declarada:** Argentina, Ley 11.723. Plazo general: 70 años desde el 1 de enero siguiente a la muerte del autor. Fotografía y obra cinematográfica tienen plazos propios y distintos: **verificar antes de tocar esos formatos** (afecta a la etapa 3 y 4 de la hoja de ruta, no a la v1).
- **Verificación por obra, con evidencia registrada** (autor, fecha de muerte, fuente consultada, quién verificó, cuándo). Sin ese registro, la obra no se publica. Es una restricción de proceso: cada obra cuesta minutos de verificación, y eso limita la velocidad de la biblioteca más que el parser.
- **Derecho moral:** perpetuo e irrenunciable. Atribución siempre, integridad del texto siempre, incluso en obra de dominio público.
- **Licencia de las anotaciones:** decidido. Los comentarios y los hilos de los usuarios se publican bajo **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/deed.es), enlazada desde los términos. Ver `08_RULES §6` (R-048) y `TERMINOS.md`.
- **Datos personales (Ley 25.326):** se recolecta correo y seudónimo, nada más. Minimizar no es una preferencia estética, es lo que hace que una brecha sea un mal día y no un problema legal.
- **Menores — decisión pendiente y bloqueante para el canal aulas.** El canon escolar argentino es el mejor material disponible, pero un aula secundaria significa datos de menores, consentimiento de tutores y un régimen distinto. Propuesta: **edad mínima declarada y aulas sólo de nivel terciario/universitario en la v1**, y el nivel medio recién con el marco resuelto. `[CONFIRMAR]`
- **Responsable:** una persona física identificable, con correo de contacto y proceso de bajada publicados desde el día uno. El riesgo de la sección 12.5 del concepto es personal, no societario.
- **Obra propia de usuarios:** selector de licencia obligatorio, cuarentena antes de publicar, bajada rápida ante reclamo.

---

## 5. Qué pasa con los datos si el proyecto se abandona

Compromiso escrito en los términos desde el día uno, no cuando llegue el momento:

- **Export por usuario siempre disponible**, sin pedirlo por correo: diario de lectura completo en Markdown + JSON, con enlaces a las anclas.
- **Volcado público mensual** de obras, anclas, colecciones, relaciones y anotaciones públicas, bajo licencia abierta. Si el sitio muere, el corpus sobrevive.
- **Preaviso de cierre de 60 días**, volcado final e intento explícito de traspaso a quien quiera continuarlo.
- Las obras propias de los autores se les devuelven; no se retiene nada.

Esto también es defensa, no sólo higiene: nadie razonable invierte tres años de anotaciones en un sitio operado por una persona sola que no dijo qué pasa si se cansa.

---

## 6. Restricciones ya aceptadas que no se rediscuten en cada fase

- Operador único. Todo lo que requiera un equipo está fuera de alcance por definición.
- Sin modelo de ingresos. Es una restricción de diseño: obliga a que operar sea barato.
- No se alojan archivos pesados.
- No se integran catálogos con licencia (Spotify y similares).
- Biblioteca inicial **en español y elegida por facilidad de parseo**, no por prestigio. El modelo es multilingüe; el catálogo del primer año, no.
- v1 es sólo texto.

---

## 7. Registro

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial | Fase 0 |
| 2026-09-09 | §4: licencia de las anotaciones decidida — CC BY-SA 4.0 | D de licencia |
