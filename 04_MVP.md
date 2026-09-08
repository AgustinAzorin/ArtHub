# 04_MVP.md

*artHUB — Fase 3. Versión 0.1, septiembre 2026.*

> **Estado: provisional y condicionado.** Este archivo se escribió antes de que
> corrieran los experimentos de R-01, R-02 y R-03. El checklist de
> `PLANIFICAR_PROYECTO` pide que el mecanismo central haya sobrevivido a un
> prototipo con datos reales *antes* de esta fase, y todavía no sobrevivió. Sirve
> para tener el recorte discutido y por escrito; no para empezar a construir.
> La sección 6 dice qué lo cambia.

---

## V1 ES

> Un visor de lectura de obras cortas de dominio público en español donde
> subrayar un pasaje abre una conversación pública anclada a ese punto exacto.

Una frase, sin "y", un solo recorrido: alguien llega a la URL de un pasaje, lee,
subraya, escribe, otro le responde.

---

## V1 INCLUYE

1. **Biblioteca fija de 3 a 5 obras cortas**, ingeridas a mano, una por una, con
   verificación de dominio público registrada según `00_CONSTRAINTS §4`. Sin
   pipeline. Tres es el piso, no una cifra tímida: con una sola obra la métrica de
   `P-09` (proporción de hilos fuera de la destacada) no se puede ni calcular.
2. **Visor de lectura pura**: texto canónico propio, inmutable, versionado, sin
   marcas encima. Modo estudio no existe todavía.
3. **Anclas de subrayado con los tres selectores** (posición, cita, contexto)
   persistidas desde el primer día, con el esquema `(obra, edición, versión,
   identificador estructural, rango)` completo.
4. **Un hilo por ancla, con respuestas en prosa y URL pública propia**, legible
   sin cuenta e indexable. Es la unidad del sitio.
5. **Cuenta con seudónimo y correo**, requerida sólo para escribir.

---

## V1 NO INCLUYE

Con nombre y apellido, porque es la lista que impide rellenar huecos:

**Del núcleo técnico**

- El **migrador de anclas entre versiones**. El esquema entra; el trabajo de
  reanclaje no. Si en la v1 nunca se publica una versión 2 de un texto, el
  migrador no corre nunca. Lo irreversible es el esquema, no el código que lo usa.
- Pipeline de ingesta TEI, conversor de Wikisource, cualquier automatización de
  carga. Cinco obras a mano son una tarde; el parser son meses (`R-04`).
- Alineación de traducciones, embeddings, edición por defecto por idioma.
- Endpoint de anotación W3C, importación de anotaciones de Hypothes.is,
  importación de aristas de Perseus o ToposText.
- Búsqueda, asistida o no.

**Del producto**

- Colecciones. **Ver la objeción de la sección 5: esto duele y no es gratis.**
- Relaciones tipadas y grafo, ni siquiera las dos tablas.
- Capas del aparato crítico (histórica, filológica, comunitaria) y el estado
  visible de las notas.
- Lectura como llave, progreso de lectura, marcado de capítulo. La v1 deja
  escribir en cualquier pasaje: es un superconjunto de lo que `P-02` obliga y no
  viola ningún MUST NOT, así que es un recorte legítimo, no una excepción.
- Notas privadas, diario de lectura, exportación en Markdown.
- Importación de subrayados de Kindle. Es el arma principal del concepto contra la
  sala vacía y aun así queda afuera, porque `R-06` todavía no sabe si el público
  real tiene esos subrayados. El experimento de `R-02` lo pregunta gratis.
- Publicación de obra propia. Es media v1 sola: cuarentena, selector de licencia,
  cotejo antifraude, proceso de bajada (`R-13`).
- Grupos, círculos privados, aulas, cursos.
- Seguir personas, feed contextual, perfiles con registro.
- Obra destacada de la semana **como función de software**: es un enlace en la
  portada, editado a mano.
- Agrupación de selecciones solapadas en un mismo bloque de debate, agregado de
  densidad en el margen, intersticial de spoiler.
- Tarjetas embebibles para compartir.
- App móvil, audio, cine, imagen, 3D.
- Herramientas de moderación. Se modera con acceso a la base y una regla escrita.

---

## V1 ESTÁ LISTO CUANDO

> Una persona que no es el operador llega desde un enlace a la URL de un pasaje,
> lee la obra completa en el visor, subraya otro pasaje, abre un hilo y recibe la
> respuesta de un tercero, sin que el operador toque la base de datos ni el
> servidor en el medio.

Observable, con fecha, y falla de forma visible. No incluye "que se vea lindo".

---

## 5. La objeción que este recorte deja abierta

Hay que decirla acá y no descubrirla en la Fase 5.

`02_RISKS §R-02` señala que Hypothes.is sobre Wikisource es más o menos el 60% de
artHUB, ya construido y gratis, y que la respuesta candidata a "qué agrega
artHUB" son **las colecciones, el texto canónico versionado y la obra propia**.
Este MVP recorta dos de las tres. Lo que queda en pie como diferencia real es el
texto canónico versionado, que es invisible para el usuario hasta el día que se
corrige una errata, y la página del pasaje como unidad indexable, que es una
apuesta de SEO a meses.

O sea: **el MVP tal como está escrito es, para un usuario, un Hypothes.is con
mejor tipografía.** Eso no lo invalida —su propósito no es ganarle a nadie sino
convertir al operador en anfitrión de un lugar propio—, pero obliga a dos cosas:

- Si el experimento de `R-02` sale bien **y la gente prefiere quedarse en
  Hypothes.is**, no se construye este MVP: se construye algo más chico, o se
  opera el ágora ahí mismo mientras tanto.
- Si se construye, la primera función después de la v1 son las colecciones, sin
  discusión. Es la única del concepto que ninguna herramienta existente tiene.

---

## 6. Qué cambia este archivo

| Resultado | Efecto |
|---|---|
| `R-01`: menos de ~5 h/semana de presencia sostenibles | Este MVP no se construye. Se arranca por la biblioteca personal con anotación de `00_CONSTRAINTS §3`, que no necesita hilos ni cuentas. |
| `R-02`: menos de dos hilos con más de tres respuestas | Este MVP no se construye. Ninguna función de acá fabrica una conversación que no existió con veinte invitados personales. |
| `R-02` sale bien pero la gente se queda en Hypothes.is | Se rediseña el alcance alrededor de colecciones, no de lectura. |
| `R-03`: falsos positivos irrecuperables | Cambia el ítem 3: anclas sólo a nivel de bloque estructural, sin offset, hasta que haya un mecanismo que funcione. Es peor producto, pero no miente. |
| Horas de construcción de `00_CONSTRAINTS §1` | Dimensiona los cinco ítems. Un slice de 40 horas con 6 h/semana son siete semanas. |

---

## 7. Registro

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial, condicionada | Fase 3 escrita antes de la Fase 2 |
| 2026-09-09 | Sin cambios: revisado contra `09_SLICE_1 §8`, el slice 1 es subconjunto estricto y no agrega alcance | Corrección de `09_SLICE_1 §8` |
