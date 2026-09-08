# 01_PRODUCT_PRINCIPLES.md

*artHUB — Fase 0. Versión 0.1, septiembre 2026.*

> **Autoridad máxima de producto.** Cuando dos specs se contradigan, gana este archivo. Cuando la IA proponga una función, se valida contra este archivo.
> Un principio no se esquiva con una excepción: o se cumple, o se cambia el principio con fecha y motivo escritos en el registro del final, o se descarta la función.

---

## P-01 — Toda conversación nace en un ancla

**WHY** — Es la tesis entera. Sin ancla, artHUB es un foro literario más, y los foros literarios ya existen y son gratis.
**MUST** — Todo hilo, nota, marca y colección referencia al menos un ancla `(obra, edición, versión, identificador estructural, rango)`.
**MUST NOT** — Existir un tablón, una categoría general, un "off-topic" o un hilo sin obra.
**EXAMPLE** — "¿Kafka era un escritor religioso?" no va a un foro de Kafka: cuelga del ancla de obra completa, o de una colección de pasajes de varias obras.

---

## P-02 — Leer nunca se bloquea; escribir requiere haber leído ese pasaje

**WHY** — El mejor visitante que tiene el proyecto llega desde un buscador a un pasaje suelto. Pedirle veinte páginas antes de dejarlo hablar es perderlo. Pero sin ninguna llave, el ágora se llena de gente que opina sobre lo que no leyó.
**MUST** — Todo hilo público es legible sin cuenta y sin progreso. Se puede escribir en el pasaje al que se llegó, siempre. Los spoilers se avisan con un intersticial que el lector puede atravesar.
**MUST NOT** — Muro de pago, registro previo para leer, cuotas, excepciones por rol, o bloqueo de escritura en el pasaje de llegada.
**EXAMPLE** — Alguien cae en el ancla "insecto monstruoso" desde Google: puede preguntar ahí mismo. Para comentar el resto del capítulo 1, tiene que leerlo.

---

## P-03 — No hay números públicos de reputación ni de popularidad

**WHY** — Un puntaje convierte el debate en competencia de aplausos, se gamea, y es lo que haría rentable subir texto ajeno. La ausencia de premio es la mejor defensa antifraude que tiene el proyecto.
**MUST** — El orden lo da la proximidad al ancla, el seguimiento de personas y la curaduría firmada. El perfil muestra registro (obras leídas, notas, hilos, colecciones), no totales acumulables.
**MUST NOT** — Votos, karma, likes, "mejor respuesta", rankings, portada de lo más comentado, porcentaje de lectura visible, contadores por persona.
**EXCEPCIÓN EXPLÍCITA** — La densidad agregada por pasaje ("38 hilos, 12 notas") es información de navegación sobre la obra, no puntaje de una persona. Es la única forma de número permitida.
**EXAMPLE** — Dos lecturas opuestas del mismo verso conviven sin que una quede arriba. La disparatada muere por falta de lectores, no por votos negativos.

---

## P-04 — La obra y su conversación viven en el mismo lugar, o no entran

**WHY** — Discutir acá algo que se consume allá es exactamente el problema que artHUB existe para resolver. Además, depender de términos ajenos que pueden revocar el acceso ensucia el marco legal limpio, que es el mayor activo defensivo.
**MUST** — Sólo dominio público verificado con evidencia registrada, y obra propia con licencia explícita del autor.
**MUST NOT** — Integrar catálogos con licencia, embeber reproductores de terceros como sustrato de discusión, alojar nada cuya disponibilidad dependa de un contrato revocable.
**EXAMPLE** — Un audiolibro de LibriVox entra aunque el archivo se sirva desde archive.org: la licencia es libre y nadie puede retirarlo. Un álbum de Spotify no entra, aunque sea técnicamente fácil.

---

## P-05 — Ninguna conversación se pierde por un cambio en el texto

**WHY** — Es el único riesgo técnico que no se puede arreglar después. Una errata corregida que huerfaniza mil hilos destruye lo único que el proyecto acumula. `03_SPIKE_anclas.md` (R-03) agregó un hallazgo peor que huerfanizar: un ancla que migra al pasaje equivocado no desaparece, miente, y nadie se entera nunca.
**MUST** — Anclas inmutables y versionadas, tres selectores redundantes (posición, cita, contexto), texto canónico propio, reanclaje acotado por bloque, y **huérfano visible** cuando el reanclaje no tiene confianza suficiente. Toda migración de ancla entre versiones registra una confianza explícita; por debajo del umbral **0.80** (`08_RULES` R-030, fijado por el barrido de `03_SPIKE_anclas.md §2`/§6), el ancla queda huérfana visible, nunca se migra "por las dudas"; ante empate entre dos candidatos, huérfana.
**MUST NOT** — Editar texto publicado en el lugar, renderizar desde el archivo de origen, borrar o mover un ancla sin dejar registro, hacer desaparecer un hilo en silencio. Migrar un ancla sin dejar registro de la versión de origen, de la confianza y del método (posición o concordancia difusa).
**EXAMPLE** — Se corrige una errata del capítulo 5: se publica una versión nueva, se reanclan sólo las anclas de los bloques que cambiaron, y las que no migran quedan mostrando su cita original con un aviso.

---

## P-06 — La máquina dice dónde se discutió; lo que se dijo se lee

**WHY** — Un resumen automático de las interpretaciones desplaza a la lectura de los hilos, igual que un extracto desplaza al artículo, y vacía lo único que artHUB tiene.
**MUST** — La IA se usa para buscar, encontrar, alinear traducciones como sugerencia y detectar duplicados.
**MUST NOT** — Resumir hilos, generar notas críticas, producir interpretaciones, ni publicar como contenido ningún texto interpretativo generado por máquina.
**EXAMPLE** — "Mostrame las discusiones sobre la relación padre-hijo en esta obra" es válido. "Resumime qué se dijo" no existe como función.

---

## P-07 — Se modera conducta, no sentido

**WHY** — Una persona sola no puede ejercer ni legitimar una autoridad editorial sobre el significado de las obras, y si lo intenta genera resentimiento y no escala.
**MUST** — Las capas histórica y filológica exigen fuente y llevan estado visible (con fuente / en disputa / sin fuente); cualquiera puede marcar una nota como disputada dejando su argumento. La capa comunitaria no tiene árbitro.
**MUST NOT** — Borrar una lectura por considerarla equivocada, designar una nota canónica por pasaje, arbitrar quién tiene razón sobre el sentido de un texto. Sí se borra el ataque personal y el spam.
**EXAMPLE** — Una nota histórica sin fuente no se elimina: se muestra marcada como tal y el lector decide.

---

## P-08 — Lo que produce la gente es de la gente

**WHY** — Quien anota lo hace gratis y por amor a la obra. Convertir ese trabajo en producto vacía la comunidad que lo construyó y rompe la promesa que sostiene todo lo demás.
**MUST** — Export completo y permanente del diario de lectura; licencia abierta de las anotaciones fijada antes del primer usuario; volcados públicos periódicos del grafo; atribución siempre; el autor conserva sus derechos sobre su obra.
**MUST NOT** — Vender datos, licenciar el grafo a terceros, retener el archivo de nadie, encerrar contenido detrás de una cuenta.
**EXAMPLE** — Alguien se va a Obsidian con todo su diario en Markdown y con los enlaces a las anclas funcionando. Está previsto, no tolerado.

---

## P-09 — La biblioteca siempre está abierta; el destacado es curaduría, no permiso

**WHY** — Si toda la conversación ocurre en la obra de la semana, el proyecto muere el día que el anfitrión se cansa.
**MUST** — Cualquiera abre un hilo sobre cualquier obra de la biblioteca en cualquier momento. La proporción de hilos fuera del destacado se mide y se mira crecer.
**MUST NOT** — Restringir, priorizar en la interfaz ni condicionar la apertura de hilos según la obra destacada.
**EXAMPLE** — La obra de la semana es *La metamorfosis* y alguien abre un hilo sobre *Los siete locos*: aparece igual, con el mismo peso, en el pasaje que corresponde.

---

## Tensiones conocidas

No son bugs; son el precio de los principios y hay que reconocerlas cuando aparezcan:

- **P-03 vs. descubrimiento.** Sin popularidad, encontrar lo bueno depende de la proximidad al ancla, del seguimiento y de la curaduría. Si eso falla, la tentación va a ser agregar un número. La respuesta es mejorar las colecciones, no ceder.
- **P-04 vs. hoja de ruta de audio y cine.** Los archivos pesados se sirven desde afuera. La línea no es dónde están los bytes: es que la licencia sea libre e irrevocable.
- **P-02 vs. aulas.** El docente ve el progreso de su grupo. Es dentro de un curso con miembros que aceptaron, no una métrica pública: no viola P-03.
- **P-09 vs. arranque en frío.** Los primeros meses el destacado va a ser casi toda la actividad. Es esperable; lo que no es esperable es que siga siéndolo en el mes seis.

---

## Registro de cambios de principios

| Fecha | Principio | Cambio | Motivo |
|---|---|---|---|
| 2026-09 | — | Versión inicial | Fase 0 |
| 2026-09-08 | P-05 | + MUST sobre confianza explícita de migración (umbral `0.80`) y + MUST NOT sobre migrar sin registro de confianza/método | `03_SPIKE_anclas.md §5`, redacción anticipada por `02_RISKS §R-03`, número fijado por la corrida real del spike |
