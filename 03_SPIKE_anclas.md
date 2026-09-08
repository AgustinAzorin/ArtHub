# 03_SPIKE_anclas.md

*artHUB — Fase 2. Versión 0.1, septiembre 2026. Spike de R-03.*

> **Estado: corrido contra Wikisource real.** `spike_anclas.py` (los ocho
> bloques de la tarea de construcción: verdad de campo, bloques e
> identificadores, anclas, reanclaje, clasificación de seis categorías, CLI de
> cuatro subcomandos, salida JSON+tabla, barrido de umbral×semilla y barrido
> de contexto×semilla) corrió `humo` (calibración, sin red — sigue dando
> 60/9/3/1 bloques exacto), `traer` contra `es.wikisource.org`,
> `correr --barrido` y `correr --barrido-contexto` sobre una obra real de
> Horacio Quiroga con dos revisiones separadas por edición humana real. Los
> números de §2 y la respuesta de §3 son de esa corrida, no simulados. Los
> datos de origen (`rev_A.txt`, `rev_B.txt`, `rev_meta.json`) y la salida
> completa (`resultado.json`, `barrido_resultado.json`,
> `barrido_contexto.json`) quedan en `spikes/r03/` para auditar cualquier
> fila de la tabla contra el texto real. Construir el arnés forzó las seis
> decisiones de diseño de la sección 4; correrlo forzó una séptima, en §4.7.
>
> Dos notas operativas para quien corra esto de nuevo: (1) la política de red
> de este entorno ya no bloquea `es.wikisource.org` como bloqueaba cuando se
> escribió esta nota por primera vez, pero la API pública de Wikimedia
> devuelve 429 con frecuencia bajo el proxy compartido de este entorno —
> `traer` no reintenta solo, hay que reintentar a mano con backoff (varios
> minutos de espera, no segundos); (2) `traer` asume que **la última
> revisión de la página tiene el texto completo**, y para la obra elegida no
> es cierto: desde 2023 la página raíz quedó como stub post-transclusión de
> ProofreadPage (`<pages index=.../>`) sin texto inline. Hubo que fijar a
> mano la revisión B en la última con contenido real (ver `spikes/r03/`); si
> se vuelve a correr `traer` tal cual sobre una obra migrada a ProofreadPage,
> baja un B vacío sin avisar.

---

## 1. Pregunta que intenta responder

Sobre una obra real y un cambio real hecho por humanos: ¿cuántas anclas migran
bien, cuántas quedan huérfanas y **cuántas migran al lugar equivocado sin avisar**?

El tercer número es el único que decide. Un huérfano visible es un costo; una
migración silenciosa al pasaje equivocado es un hilo que miente y nadie se entera
nunca.

---

## 2. Qué se probó

Obra real, historial de revisiones real de `es.wikisource.org`, sin errata
inventada (§4.1 lo exige). `rev_A.txt`/`rev_B.txt`/`rev_meta.json` completos
en `spikes/r03/`.

| | |
|---|---|
| Obra | *El almohadón de pluma*, Horacio Quiroga (`es.wikisource.org`) |
| Revisiones (A → A+k) | 615269 (2013-11-13) → 1343145 (2023-07-25), 18 ediciones humanas reales entre medio |
| Comentario de edición | Ninguna de las dos revisiones frontera tiene comentario propio; el tramo incluye, entre otras, la 1116093 ("Error ortográfico, pesos en vez de pasos") y dos reversiones de vandalismo |
| Bloques totales / cambiados / perdidos | 32 / 3 / 1 |
| Anclas generadas | 200 |
| Umbral de confianza (corrida principal; barrido completo abajo) | 0.75 |

| Resultado | n | % |
|---|---|---|
| migrada bien | 140 | 70.0% |
| **migrada mal (falso positivo)** | 6 | 3.0% |
| &nbsp;&nbsp;de las cuales, sobre texto inexistente en B | 6 | 3.0% |
| migrada mal por ambigüedad literal | 0 | 0.0% |
| huérfana evitable | 0 | 0.0% |
| huérfana correcta | 19 | 9.5% |
| migró en caso tocado | 35 | 17.5% |

Desvío de las migraciones malas: `≤5 chars 0 / 6–50 0 / >50 6`. Anclas que
cruzan bloques: 24.

**Criterio de fracaso** (de `02_RISKS §R-03`, corregido en §4.3 y §4.4 de este
archivo): falsos positivos con desvío mayor a 50 caracteres por encima del **1%**,
o huérfanas **evitables** por encima del **10%**.

Criterio de fracaso — FP con desvío >50: 3.0% (umbral ≤1.0%) -> **NO CUMPLE**.
Criterio de fracaso — huérfanas evitables: 0.0% (umbral ≤10.0%) -> CUMPLE.

Leído literal, el criterio reprueba. §4.7 mira los seis casos uno por uno —es
el "resto del día" que este spike reserva para mirar los fallos a ojo— y
encuentra que los seis son la misma clase de falla, y no es la que el
criterio fue escrito para atrapar.

### Barrido `--umbral` × `--semilla` (§6, tres semillas por umbral)

| umbral | media %FP desvío>50 | media %huérfanas evitables |
|---|---|---|
| 0.6 | 4.17% | 0.0% |
| 0.7 | 3.5% | 0.17% |
| 0.75 | 3.17% | 0.17% |
| 0.8 | 3.17% | 0.17% |
| 0.9 | 3.17% | 0.83% |

Ningún umbral entre 0.6 y 0.9 hace pasar el criterio de FP tal como está
escrito: el 3%±1 es estable en toda la banda, no es ruido de una corrida. Las
huérfanas evitables sí responden al umbral, y se mantienen bajas (≤0.83% de
media) en todo el rango. Detalle por celda en `spikes/r03/barrido_resultado.json`.

El barrido descarta 0.6 (más FP: 4.17% de media contra 3.17%) y descarta 0.9
(más huérfanas evitables: 0.83% contra 0.17%). Entre 0.75 y 0.8 el barrido
**no puede decidir**: las celdas son idénticas, semilla por semilla, no sólo
en la media —`fp_desvio_mayor_50_pct` y `huerfanas_evitables_pct` dan el
mismo número en las tres semillas para ambos umbrales (ver
`spikes/r03/barrido_resultado.json`, claves `umbral=0.75_semilla=*` vs.
`umbral=0.8_semilla=*`)—. Elegir 0.80 sobre 0.75 no es, entonces, un
resultado de este barrido: es una decisión de criterio, en la dirección que
`P-05` pide (ante empate de evidencia, más margen contra la migración
silenciosa, no menos), registrada como tal en `08_RULES` R-030 y
`01_PRODUCT_PRINCIPLES` P-05.

### Barrido `--contexto` × `--semilla` (R-001, §4.4)

La longitud de prefijo/sufijo es la palanca contra la **ambigüedad
literal** (§4.4), no contra el %FP: el %FP en esta obra está dominado por el
artefacto de §4.7 (correcciones ortográficas que la cita atraviesa), que no
tiene nada que ver con cuánto contexto se agrega alrededor de la cita. Por
eso la lectura de esta tabla es `migrada_mal_ambiguedad` y `huérfanas
evitables`; el %FP se deja de referencia y no se usa para decidir R-001.

Corrida sobre *El almohadón de pluma* (la misma obra y el mismo par de
revisiones de §2), `n=200`, `umbral=0.80` fijo (el valor ya decidido por
R-030), `--contexto` en 16/32/64/128, tres semillas por celda:

| contexto | media %migrada_mal_ambiguedad | media %huérfanas evitables | media %FP (referencia, §4.7) |
|---|---|---|---|
| 16 | 0.0% | 0.17% | 3.17% |
| 32 | 0.0% | 0.17% | 3.17% |
| 64 | 0.0% | 1.0% | 3.17% |
| 128 | 0.0% | 3.67% | 3.0% |

Detalle por celda (12 corridas) en `spikes/r03/barrido_contexto.json`.

`migrada_mal_ambiguedad` da 0.0% en las cuatro longitudes: esta obra, en
esta ventana de revisiones, no tiene un caso de ambigüedad literal que 16
caracteres de contexto ya no resuelvan. Lo que sí responde a `--contexto`
son las huérfanas evitables, y en la dirección contraria a la esperada:
suben con más contexto (0.17% en 16/32, hasta 3.67% en 128) en vez de
bajar. Más contexto no es gratis: agrandar prefijo+cita+sufijo hace más
improbable que la ventana completa siga coincidiendo con `ratio ≥ umbral`
después de una edición cercana, así que el reanclaje difuso pierde
candidatos que con menos contexto encontraba. `umbral_confianza` (R-030) ya
está fijado sobre el patrón completo (prefijo+cita+sufijo): un contexto más
largo compite con ese mismo umbral por el mismo motivo que §4.7 describe
para la cita sola.

**Lo que esta corrida no puede decidir por sí sola:** con `migrada_mal_ambiguedad`
en 0.0% en las cuatro celdas, esta obra no ofrece evidencia para *subir*
`--contexto` por encima de 32 — y sí ofrece evidencia en contra, en las
huérfanas evitables. Para ver la ambigüedad literal responder a `--contexto`
hace falta una obra con fragmentos repetidos dentro de la ventana de
revisiones tocada, que ésta no tiene en cantidad. El valor de R-001 queda
sin fijar acá a propósito (decisión de criterio del operador, no de este
barrido).

### Prueba de humo del instrumento (no es el resultado)

Corrida sobre texto sintético con erratas fabricadas, sólo para verificar que el
arnés mide: 200 anclas, 60 bloques (9 cambiados, 3 borrados), un párrafo
insertado, umbral 0.75.

| Resultado | n | % |
|---|---|---|
| migrada bien | 125 | 62.5% |
| **migrada mal (falso positivo)** | 19 | 9.5% |
| &nbsp;&nbsp;de las cuales, sobre texto inexistente en B | 12 | 6.0% |
| migrada mal por ambigüedad literal | 1 | 0.5% |
| &nbsp;&nbsp;de las cuales, sobre texto inexistente en B | 0 | 0.0% |
| huérfana evitable | 0 | 0.0% |
| huérfana correcta | 23 | 11.5% |
| migró en caso tocado | 32 | 16.0% |

Desvío de las migraciones malas: `≤5 chars 5 / 6–50 3 / >50 12`. Anclas que
cruzan bloques: 35.

Criterio de fracaso — FP con desvío >50: 6.0% (umbral ≤1.0%) -> **NO CUMPLE**.
Criterio de fracaso — huérfanas evitables: 0.0% (umbral ≤10.0%) -> CUMPLE.

Esto no dice nada sobre R-03: el texto sintético usa un vocabulario de veinte
palabras, que es el peor caso posible para el selector de contexto y el mejor
posible para la alineación de bloques por hash. Es la calibración del
instrumento, no la medición.

---

## 3. Respuesta

**Funciona, con una condición sobre cómo se mide, no sobre el mecanismo.**

Sobre la única obra real corrida: cero migraciones a un pasaje semánticamente
distinto (0/200), cero huérfanas evitables, y los seis casos que el criterio
numérico cuenta como falso positivo son, los seis, la misma anomalía de
medición descrita en §4.7 —no seis fallas del reanclaje, una falla del
harness contando la misma clase de caso seis veces sobre una obra de sólo 32
bloques—. El criterio de `02_RISKS`, aplicado literal, dice NO CUMPLE en
punto y en el barrido entero; mirado el detalle, dice que en esta corrida el
reanclaje difuso hizo exactamente lo que tenía que hacer incluso en el caso
que el criterio estaba diseñado para atrapar.

Eso no valida el mecanismo entero: es **una** obra, **una** ventana de 18
ediciones, mayoría correcciones ortográficas y una reversión de vandalismo —
el caso fácil que la pregunta de §1 llama "corrección real", no el caso
adversarial (reescritura de un párrafo entero, reordenamiento de oraciones)
que también hay que ver antes de comprometer el esquema. Con eso dicho, no
hay nada en esta corrida que empuje a rediseñar el mecanismo antes de escribir
el esquema, que era la pregunta binaria real. **Condición:** antes de fijar
el `umbral_confianza` en producción, correr §4.7 sobre al menos una obra con
revisiones que reescriban prosa (no sólo erratas) — el criterio corregido
(§4.7) todavía no se probó contra ese caso, que es justamente donde un falso
positivo *de verdad* —ancla que aterriza en un pasaje que un lector no
reconocería como el mismo— sería más probable.

`umbral_confianza = 0.80` (ver §4.7 y `08_RULES` R-030): el barrido descarta
0.6 (más FP) y 0.9 (más huérfanas evitables), pero entre 0.75 y 0.8 no
decide nada —las celdas son idénticas semilla por semilla, no sólo en la
media—. 0.80 es una elección de criterio dentro del rango que el barrido
valida, en la dirección que `P-05` pide (más margen contra la migración
silenciosa ante evidencia empatada), no un resultado que el barrido produzca
por sí solo.

---

## 4. Qué queda restringido en el diseño

Estas seis salieron de construir el instrumento, no de correrlo. Valen aunque el
experimento todavía no exista.

### 4.1 Sin verdad de campo no hay experimento

`02_RISKS` pide contar "% migradas mal" sin decir contra qué. No hay contra qué:
hace falta un mapa carácter a carácter de A → B, derivado del diff, que diga dónde
cayó realmente cada carácter preservado. Sin ese mapa sólo se puede contar cuántas
anclas migraron, no cuántas migraron bien, que es la pregunta entera. El arnés lo
construye con `diff_main` **sin `cleanupSemantic`**: la limpieza semántica agrupa
ediciones para que un humano las lea mejor y al hacerlo destruye la
correspondencia carácter a carácter.

### 4.2 Los identificadores estructurales no pueden derivarse de la posición

Este es el hallazgo que más caro sale si no se toma ahora. La sección 6 del
concepto dice que el ancla de dos niveles gana estabilidad porque el identificador
estructural sobrevive a los cambios tipográficos. Es cierto **sólo si el
identificador es estable**. Si el id de un bloque se calcula por posición al
ingerir (`p-0001`, `capitulo-3-parrafo-14`), insertar un párrafo en el capítulo 3
corre todos los ids de ahí para abajo y el "nivel estable" del ancla se rompe
entero, con un daño mucho peor que el que el mecanismo venía a evitar.

**Restricción:** el identificador estructural se asigna **una vez, en la primera
versión, y se transporta a las versiones siguientes por alineación de bloques**.
Un bloque nuevo recibe un id nuevo que nunca se reusa. Los ids derivados de la
estructura propia de la obra (acto, escena, verso, versículo) son la excepción
buena, porque son estables por definición, y ésa es una razón más de peso para
conservar TEI que la que da §6.1.

### 4.3 Huérfana no es sinónimo de falla

El criterio "huérfanos por encima del 10%" mete en la misma bolsa dos cosas
opuestas. Si el pasaje fue borrado o reescrito, dejar el ancla huérfana **es la
respuesta correcta** y es literalmente lo que `P-05` exige. Sólo cuenta como falla
la huérfana **evitable**: el texto seguía existiendo en B y el reanclaje no lo
encontró. En la prueba de humo, 27% de las anclas quedaron huérfanas de forma
correcta: con la métrica original ese número solo habría "reprobado" el mecanismo
por hacer bien su trabajo.

### 4.4 "Migró mal" necesita distancia, no un booleano

Una migración desviada dos caracteres es un subrayado torcido que nadie nota. Una
desviada cuatrocientos es un hilo colgado del pasaje equivocado. El umbral del 1%
sólo tiene sentido aplicado a la segunda. El arnés reporta un histograma de
desvío y separa además el caso en que el ancla cayó sobre **otra ocurrencia
literal idéntica** de la misma cita: eso no es un bug del algoritmo sino
ambigüedad del texto, se mide aparte y se arregla distinto (más contexto, no mejor
concordancia).

### 4.5 Las anclas a caballo de dos bloques no entran en el modelo

Un ancla se define como `(identificador estructural, offset dentro del bloque)`.
Una selección que empieza en un párrafo y termina en el siguiente no tiene un
único bloque, y la gente subraya así todo el tiempo. El arnés las representa con
una ventana de dos bloques, que funciona pero es un parche.

**Decisión que la Fase 5 tiene que tomar explícitamente:** o el ancla guarda
`(bloque_inicio, offset)` + `(bloque_fin, offset)`, o se prohíbe cruzar bloques en
la interfaz. Lo segundo es más barato y probablemente peor.

### 4.6 Dos trampas de la librería, anotadas para que no se paguen dos veces

- `Diff_Timeout = 0`. Por defecto el diff se corta a un segundo y devuelve un
  resultado degradado. Sobre una novela entera eso hace que la verdad de campo
  mienta sin avisar.
- `Match_MaxBits = 0`. El puerto Python hereda el límite de 32 caracteres del
  bitap de JavaScript y **lanza excepción** con patrones más largos. Como el
  patrón acá es prefijo + cita + sufijo, se pasa de 32 siempre.

---

### 4.7 "Existió en B" no puede ser literal cuando la cita cruza la corrección misma

Los seis falsos positivos de §2 (umbral 0.75, semilla 1) son, los seis, la
misma ancla en distintos recortes. El bloque 22 de la obra cambió así entre A
(2013) y B (2023) — corrección de mayúscula y de una grafía antigua, en algún
punto de las 18 revisiones intermedias que no altera el tamaño del texto lo
suficiente como para aislarla por tamaño de revisión sin bisecar a mano:

```
A: Jordán se acercó rápidamente Y se dobló a su vez. [...] a ambos lados dél hueco [...]
B: Jordán se acercó rápidamente y se dobló a su vez. [...] a ambos lados del hueco [...]
```

Seis anclas generadas sobre A tienen su cita a caballo exactamente de la
`Y`→`y` o la `dél`→`del`. `_existio_en_b` (§4.1) es carácter a carácter: si
uno solo de los caracteres citados no sobrevive igual, la ancla entera cuenta
como "no existió en B", sin importar que sean 59 caracteres iguales y 1
distinto. El reanclaje difuso, mientras tanto, encontró la ubicación correcta
las seis veces —se verificó a mano contra `rev_B.txt`: el texto que devuelve
`match_main` es exactamente el pasaje corregido, en el lugar que corresponde,
no otro— con confianza ≥0.98. La clasificación las cuenta como falso
positivo "sobre texto inexistente en B" porque nunca calcula un desvío: no
hay `true_start_b` con el que compararlas, así que van directo al bucket
`>50` sin haber medido ninguna distancia real.

Esto es distinto de la ambigüedad literal de §4.4 (que sí tiene detección
propia): ahí el texto citado existe igual en dos lugares de B y el algoritmo
no puede saber cuál. Acá el texto citado **no existe igual en ningún lugar**,
porque el ancla lo citó a través del carácter mismo que una corrección
humana cambió — y el reanclaje difuso, que existe justamente para tolerar
esto, lo tolera bien. Es el caso opuesto de §4.3 (huérfana no es lo mismo que
falla): acá "no existió literal" tampoco es lo mismo que "migró mal".

**Restricción que esto le agrega al diseño:** contar falsos positivos exige
una verdad de campo que tolere una edición de bajo costo dentro de la cita,
no sólo identidad carácter a carácter. La opción más barata sin inventar una
tercera categoría ad hoc: cuando `_existio_en_b` da `False`, repetir el
chequeo sobre la ventana `prefijo+cita+sufijo` completa (no sólo la cita)
contra el ratio de `difflib` — si esa ventana tiene un candidato en B con
ratio ≥ `umbral_confianza` **en la posición que predijo el reanclaje**, no es
`migrada_mal_fp`: es una clase nueva, "migró sobre una corrección menor",
simétrica a `migrada_mal_ambiguedad`. No se implementó en `spike_anclas.py`
en esta corrida —cambiar la verdad de campo a mitad del experimento invalida
la comparación contra la calibración de humo (§2)— pero cualquier corrida
futura de R-03 la necesita: sin ella, toda obra cuya diferencia A→A+k sea
mayoritariamente ortográfica infla el %FP con el mismo artefacto, no importa
qué tan bien migre el mecanismo.

## 5. Cambio que este spike le exige a `01_PRODUCT_PRINCIPLES`

`02_RISKS` anticipó que haría falta y tenía razón. `P-05` prohíbe que un hilo
desaparezca en silencio, pero no dice nada del fallo peor, que es un ancla que no
desaparece: miente. Redacción, con el número que fija el barrido de §2:

> **MUST** — Toda migración de ancla entre versiones registra una confianza
> explícita. Por debajo del umbral **0.80**, el ancla queda huérfana visible; nunca
> se migra "por las dudas". Ante empate entre dos candidatos, huérfana.
> **MUST NOT** — Migrar un ancla sin dejar registro de la versión de origen, de la
> confianza y del método (posición o concordancia difusa).

Va al registro de cambios de principios con fecha y motivo, no como excepción
— aplicado en `01_PRODUCT_PRINCIPLES` en este mismo commit.

---

## 6. Cómo correrlo

```bash
pip install diff-match-patch

# calibrar el instrumento, sin red
python3 spike_anclas.py humo

# bajar dos revisiones reales separadas por N ediciones humanas
# (el título es "El almohadón de pluma", singular: buscar con
# list=search antes de asumirlo, Wikisource no siempre coincide
# con el título de portada)
python3 spike_anclas.py traer --titulo "El almohadón de pluma" --saltos 20

# medir
python3 spike_anclas.py correr --a rev_A.txt --b rev_B.txt --n 200 \
        --umbral 0.75 --json resultado.json

# de paso, el sondeo de R-04 (02_RISKS §3): cinco obras candidatas
python3 spike_anclas.py sondeo "Obra 1" "Obra 2" "Obra 3" "Obra 4" "Obra 5"
```

Si la página elegida migró a transclusión ProofreadPage en algún punto de su
historial (§ nota operativa al principio de este archivo), `traer` baja un B
vacío sin error: verificar a mano que `rev_B.txt` tiene contenido real antes
de correr `correr`, o revisar la lista de revisiones por tamaño (`prop=revisions`
con `rvprop=size`) y elegir el revid más nuevo que no sea un stub.

Barrer `--umbral` entre 0.6 y 0.9 y `--semilla` en tres valores. Un umbral que se
elige mirando un solo número es un umbral inventado.

**Presupuesto:** 2–3 horas si el arnés no necesita tocarse; el resto del día que
`02_RISKS` reserva es para mirar los fallos a ojo, que es donde está el
aprendizaje real. Si la semana no da, este spike es el que se corre a la semana
que viene: `02_RISKS §Nota de secuencia` ya lo decidió y sigue siendo correcto.
