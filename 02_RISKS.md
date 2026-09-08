# 02_RISKS.md

*artHUB — Fase 1. Versión 0.1, septiembre 2026.*

> Un riesgo sin experimento es una excusa. Los tres de arriba tienen fecha de esta semana.
> **Prerrequisito bloqueante:** las probabilidades de este archivo son estimaciones hasta que se completen las horas reales de `00_CONSTRAINTS §1`. Eso lo resuelve el experimento de R-01, que por eso va primero.

---

## 0. Cómo se ordenó

`prob × daño`, ambos en escala 1–3.

- **Probabilidad** — 3: pasa salvo que se haga algo. 2: pasa si sale mal. 1: pasa sólo si se acumulan varias cosas.
- **Daño** — 3: mata el proyecto o destruye lo acumulado. 2: recorta alcance o quema meses. 1: molesta.

El empate se rompe por **reversibilidad**: gana el que no se puede arreglar después.

---

## 1. Inventario

| ID | Riesgo | Tipo | P | D | Score |
|---|---|---|---|---|---|
| **R-01** | El operador construye en vez de anfitrionar. El código avanza, el ágora no abre nunca o abre sin él adentro. | Personal | 3 | 3 | **9** |
| **R-02** | Sala vacía: nadie escribe anclado, o escribe una vez y nadie le responde a nadie. | Demanda | 3 | 3 | **9** |
| **R-03** | El reanclaje tiene tasa inaceptable de huérfanos —o peor, de migraciones silenciosas al lugar equivocado— sobre texto real. | Técnico | 2 | 3 | **6** |
| **R-04** | El pipeline de ingesta se come el presupuesto de construcción entero y después pide mantenimiento perpetuo. | Técnico | 3 | 2 | 6 |
| R-05 | Agotamiento estacional: finales + trabajo dejan al ágora sin anfitrión varias semanas seguidas, justo cuando hay veinte personas mirando. | Personal | 3 | 2 | 6 |
| R-06 | El onboarding por importación de subrayados (el arma principal contra la sala vacía) no aplica al público real: pocos Kindle, subrayados en papel o en ningún lado. | Demanda | 3 | 2 | 6 |
| R-07 | Moderación unipersonal: política, agresión y spam en un espacio abierto en español. | Personal | 2 | 2 | 4 |
| R-08 | Aulas bloqueadas por el tema menores; se cae el único canal que no depende de la constancia del anfitrión. | Demanda | 2 | 2 | 4 |
| R-09 | Fuga a lo privado: la conversación buena ocurre en grupos cerrados, no hay páginas públicas, no hay descubrimiento. | Demanda | 2 | 2 | 4 |
| R-10 | Dispersión: se abren formatos (audio, cine) antes de que haya conversación. | Personal | 2 | 2 | 4 |
| R-11 | Churn de autores: publican obra propia, no reciben nada, se van. | Demanda | 3 | 1 | 3 |
| R-12 | Responsabilidad legal personal: contenido de terceros con una persona física identificable como responsable, correo y proceso de bajada publicados. | Legal | 1 | 3 | 3 |
| R-13 | Suplantación: alguien sube texto ajeno como propio. | Legal | 1 | 2 | 2 |
| R-14 | Silo por traducción: seis comunidades hablando del mismo *Quijote* sin cruzarse. | Técnico | 2 | 1 | 2 |
| R-15 | El costo supera el techo mensual. | Económico | 1 | 2 | 2 |
| R-16 | Queda en herramienta académica: trescientos estudiantes de Letras y nadie más. | Demanda | 2 | 1 | 2 |

---

## 2. Top 3, con experimento de esta semana

### R-01 — Preferencia revelada por construir sobre anfitrionar

**Por qué está primero.** Todo el diseño depende de una persona que esté presente todos los días durante meses en un lugar casi vacío. Esa persona es un desarrollador de 19 años con trabajo full stack y una ingeniería en curso, y el trabajo de anfitrión no se parece en nada al que le da placer. El modo de falla no es abandonar: es pasar seis meses puliendo el parser TEI, que es agradable, medible y da la sensación de avanzar, y llegar al lanzamiento sin haber ejercido nunca el músculo que el proyecto necesita. `00_CONSTRAINTS §1` ya escribió la regla correcta —la presencia se reserva primero—, pero una regla escrita no es evidencia de que se pueda cumplir.

**Pregunta binaria.** ¿Existen horas de presencia sostenibles todas las semanas, y hay antecedente propio de sostener algo así más allá del entusiasmo inicial?

**Experimento (esta semana, 0 horas de construcción):**

1. **Semana medida.** Registrar una semana lectiva normal en dos columnas separadas, construcción y presencia, con el reloj y no con la memoria. Sale el `[COMPLETAR]` de `00_CONSTRAINTS §1`.
2. **Tasa base personal.** Listar los proyectos propios de los últimos tres años, cuántas semanas de actividad sostenida tuvo cada uno y qué lo terminó. El promedio de esa lista es la predicción por defecto de artHUB. No hay motivo para creer que este va a ser distinto sin un cambio explícito en cómo se opera.

**Criterio de fracaso.** Menos de ~5 horas semanales de presencia sostenibles, o una tasa base menor a ocho semanas, significa que este diseño no es para este operador tal como está. La salida no es cerrar: es arrancar por la versión reducida que ya está prevista en `00_CONSTRAINTS §3` —biblioteca personal con anotación, que cuesta casi nada operar y no exige anfitrión— y abrir el ágora recién si aparece gente sola.

**Qué queda decidido.** El número de horas de presencia dimensiona todas las fases siguientes. Si es chico, R-04 se recorta antes de empezar (ingesta degradada, prosa del XIX y nada más).

---

### R-02 — Sala vacía: la conversación anclada no arranca

**Por qué.** Es el riesgo que el documento de concepto identifica bien y para el que propone respuestas de diseño (cadencia, destacado, importación de subrayados, aulas), todas sin verificar. La pregunta no es si va a haber poca gente al principio —va a haber— sino si la conversación anclada asincrónica es una forma de estar juntos que la gente adopta cuando se la ofrecen, o una que suena bien y nadie usa.

**Pregunta binaria.** Con veinte personas invitadas a mano y el anfitrión empujando, ¿aparecen hilos con más de tres respuestas colgados de pasajes concretos?

**Experimento (esta semana, 0 horas de construcción): el ágora de cartón.**

1. Elegir un cuento corto de dominio público en español, 30–40 minutos de lectura. *El almohadón de plumas* de Quiroga sirve: dominio público en Argentina, corto, y tiene pasajes que se discuten solos.
2. Montarlo donde ya se puede comentar sobre el texto: Hypothes.is sobre la página de Wikisource, o un Google Doc con comentarios habilitados. Nada de código.
3. Invitar por privado, uno por uno, a 15–20 personas que lean: compañeros de facultad, del trabajo, amigos. Nada de posteo masivo — el experimento mide el techo, no el piso, y el techo se mide en las mejores condiciones posibles.
4. Consigna: leelo esta semana y dejá al menos un comentario colgado de un pasaje. El anfitrión abre el primer hilo y responde a todos, todos los días. Eso también es parte del experimento: son cinco días de ejercer el rol.
5. En la misma invitación, preguntar a cada uno dónde guarda lo que subraya cuando lee. Eso testea R-06 sin costo extra.

**Números que salen.** Cuántos abren, cuántos leen completo, cuántos dejan ≥1 comentario anclado, **cuántos responden al comentario de otro** —el único que importa— y cuántos hilos terminan la semana con más de tres respuestas.

**Criterio de fracaso.** Menos de dos hilos con más de tres respuestas. Si con veinte invitados personales, un texto de cuarenta minutos y un anfitrión empujando la conversación no se sostiene, ninguna función de la v1 la va a fabricar.

**Lo incómodo del experimento, dicho de frente.** Hypothes.is sobre Wikisource es más o menos el 60% de artHUB, ya construido, gratis y funcionando. Si el experimento sale bien, hay que responder qué agrega artHUB además de mejor tipografía: la respuesta candidata son las colecciones, el texto canónico versionado y la obra propia, y conviene que quede escrita antes de la Fase 3. Si sale bien *y* la gente prefiere seguir ahí, el proyecto correcto podría ser mucho más chico.

---

### R-03 — El reanclaje no sobrevive a un cambio real de texto

**Por qué.** Es el único riesgo técnico irreversible: entra en el esquema o no entra nunca. Pero conviene bajarle el dramatismo con el que lo trata el concepto —Hypothes.is corre selectores redundantes en producción hace una década, no es territorio inexplorado— y subirle precisión: lo que hay que medir no es si funciona, sino con qué tasa falla y **cómo** falla.

**Pregunta binaria.** Sobre una obra real y un cambio real, ¿cuántas anclas migran bien, cuántas quedan huérfanas y cuántas migran al lugar equivocado sin avisar?

**Experimento (2–3 días de horas de construcción, código feo en `/spikes`):**

1. No inventar la errata. Wikisource publica el historial de revisiones con diffs reales: agarrar una obra con muchas revisiones y tomar la versión A y la versión A+k, que son correcciones que hicieron humanos de verdad.
2. Normalizar ambas igual que las normalizaría la ingesta (Unicode, espacios, saltos).
3. Generar ~200 anclas sobre A, cargadas a propósito de casos difíciles: una sola palabra; media frase; fragmentos que se repiten en la obra ("dijo", "la casa"); fragmentos a caballo de dos párrafos; y una cuota alta dentro de los bloques que efectivamente cambiaron, que es donde se juega el asunto.
4. Reanclar sobre A+k: hash por bloque, posición primero, y concordancia difusa con prefijo y sufijo cuando la posición falla.
5. Contar tres cosas: % migradas con confianza alta, % huérfanas, **% migradas mal**.

**Criterio de fracaso — corregido por `03_SPIKE_anclas.md §4.3, §4.4 y §4.7` tras
correr el spike; la versión de arriba fue la que se escribió antes de construir
el arnés y no sobrevivió a la primera corrida real.**

No todo huérfano cuenta como falla, y no todo "migró mal" cuenta como falso
positivo:

- **Huérfano no es lo mismo que falla (§4.3).** Si el pasaje fue borrado o
  reescrito, quedar huérfana es la respuesta correcta y es lo que `P-05`
  exige. Sólo cuenta contra el criterio la huérfana **evitable**: el texto
  seguía existiendo en la versión nueva y el reanclaje no lo encontró. El
  10% se mide sobre huérfanas evitables, no sobre huérfanas totales.
- **"Migró mal" necesita distancia, no un booleano (§4.4).** Una migración
  desviada un puñado de caracteres no es la falla que este criterio existe
  para atrapar; una desviada varios cientos, sí. El 1% se mide sobre falsos
  positivos con desvío grande (el arnés usa >50 caracteres, con histograma
  completo para auditar el corte), no sobre cualquier desvío distinto de
  cero. Aparte, y sin contar contra el 1%: una migración que cae sobre
  **otra ocurrencia literal idéntica** de la misma cita es ambigüedad del
  texto, no un bug del mecanismo — se mide aparte (`migrada_mal_ambiguedad`)
  y se corrige con más contexto (`R-001`), no con mejor concordancia.
- **La verdad de campo tiene que tolerar una edición de bajo costo dentro de
  la cita (§4.7).** Contar "existió en B" carácter a carácter cuenta como
  falso positivo una migración que aterrizó exactamente donde correspondía,
  si la cita atraviesa el carácter mismo que una corrección humana cambió
  (una mayúscula, una grafía antigua). Sin este ajuste, cualquier obra cuyas
  ediciones reales sean mayoritariamente ortográficas infla el %FP con el
  mismo artefacto de medición, no importa qué tan bien migre el mecanismo.

**El porcentaje se cuenta sobre bloques tocados, no sobre anclas.** Las ~200
anclas de una corrida se generan solapadas sobre los mismos bloques
cambiados (`generate_anchors` carga a propósito la mitad de las estrategias
sobre bloques "tocados": editados o borrados); no son 200 eventos
independientes, son ~200 ventanas sobre el mismo puñado de correcciones. En
una obra de 32 bloques con sólo 3 cambiados, seis anclas solapadas sobre una
sola corrección de un carácter (el caso real de `03_SPIKE §4.7`) ya valen
3% del total — el umbral del 1% es **inalcanzable por construcción** en una
obra de ese tamaño: hace falta una sola corrección tocada por más de dos
anclas para superarlo, y con ~200 anclas sobre ~3 bloques cambiados eso es
casi seguro, migre bien o mal el mecanismo. El número que hay que mirar no
es "% de las 200 anclas", es cuántos **bloques** (o cuántas correcciones
distintas) produjeron al menos un falso positivo con desvío grande, sobre el
total de bloques tocados — el criterio numérico original medía la unidad
equivocada.

**Criterio de fracaso, redactado:** más del 1% de las **correcciones
tocadas** (no de las anclas) produce al menos una migración con desvío
grande sobre una cita que sobrevivió (más allá de una edición de bajo costo,
§4.7), o más del 10% de las anclas quedan **huérfanas evitables**. Cualquiera
de las dos condiciones significa que el reanclaje no alcanza y hay que
rediseñar antes de escribir una línea de esquema.

**Hallazgo que este experimento va a forzar a P-05.** El principio prohíbe que un hilo desaparezca en silencio, pero no dice nada del fallo peor: un ancla que migra al pasaje equivocado no desaparece, miente, y nadie se entera nunca. `P-05` necesita un MUST sobre falsos positivos —umbral de confianza explícito, y ante la duda huérfano visible antes que migración— y este spike es el que da el número para fijarlo.

**Salida:** `03_SPIKE_anclas.md` con el formato de la Fase 2.

---

### Nota de secuencia

Los tres no compiten por las mismas horas, y eso es deliberado. R-01 y R-02 cuestan cero horas de construcción y corren en paralelo toda la semana; R-03 es el único que consume el presupuesto de código. Si la semana no da para los tres, el que se corre es R-03: responde la pregunta menos importante de las tres y es el único que se puede responder igual de bien dentro de un mes.

---

## 3. Vigilado, sin experimento propio todavía

**R-04 — El pipeline se come todo.** No necesita experimento de riesgo porque la decisión ya está tomada en `00_CONSTRAINTS §1` y §6 (ingesta que degrada, biblioteca elegida por facilidad de parseo). Lo que sí conviene es un sondeo de una tarde, junto con el spike de R-03: bajar cinco obras candidatas de Wikisource —dos novelas del XIX, un libro de cuentos, una obra de teatro y una de verso—, correr el conversor más tonto posible y contar cuántas quedan usables con menos de una hora de trabajo manual cada una. El resultado no cambia el rumbo, cambia el catálogo del primer año, y convierte "prosa primero" de intuición en número.

**R-05, R-07.** Se mitigan por diseño, no por experimento: hibernación anunciada con fecha en épocas de finales (un ágora que avisa que su anfitrión vuelve el 15 no pierde a nadie; una que se apaga sin decir nada, sí), y reglas cortas escritas antes del primer usuario.

---

## 4. Correcciones al inventario del documento de concepto

La sección 12 de `artHUB.md` tiene doce entradas y es un buen ensayo, pero no es un inventario de riesgos: no tiene probabilidad, no tiene daño, no tiene experimento, y varias entradas no son riesgos.

- **No son riesgos, son tareas con fecha.** "Nombre" (12.12) es una decisión pendiente. "Concentración de la contribución" (12.10) es una constante de todas las comunidades de este tipo, no algo que pueda salir distinto; el riesgo real es no cuidar a esas treinta personas, y eso es una práctica operativa.
- **Sobrevalorado.** "Sostenibilidad económica" (12.9) figura casi al final pero ocupa el párrafo más largo del documento. Con v1 sólo texto, el piso son 10–15 USD/mes y el recurso escaso es el tiempo del operador, no la plata. Acá baja a R-15.
- **Mal calificado.** "Anclas rotas" (12.3) está bien identificado como irreversible pero no es el riesgo técnico más probable, sino el más caro si sale mal. El más probable es el pipeline: no mata el proyecto, se come los meses.
- **Lo que falta, y es lo más importante.** No hay un solo riesgo escrito en primera persona. "Dependencia del anfitrión" (12.4) está redactada como si el anfitrión fuera otra persona que podría cansarse. Es el único riesgo del inventario que no se mitiga con diseño, y por eso encabeza este archivo.

---

## 5. Revisión

Este archivo se revisa al cerrar la Fase 2 y después en cada reevaluación trimestral de `00_CONSTRAINTS §3`. Un riesgo que sobrevive dos revisiones sin experimento se baja de rango o se elimina: si nadie lo va a testear, no está gobernando ninguna decisión.

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial | Fase 1 |
| 2026-09-08 | R-03: criterio de fracaso reescrito (huérfana evitable, no cualquier huérfana; desvío grande, no cualquier desvío; verdad de campo tolerante a edición de bajo costo; el % se cuenta sobre correcciones/bloques tocados, no sobre anclas) | Correr `03_SPIKE_anclas.md` §4.3, §4.4 y §4.7 mostró que el criterio original medía la unidad equivocada y era inalcanzable por construcción en una obra chica |
