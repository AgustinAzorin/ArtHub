# 03_SPIKE_anclas.md

*artHUB — Fase 2. Versión 0.1, septiembre 2026. Spike de R-03.*

> **Estado: arnés construido, experimento sin correr.** Las secciones 2 y 3 están
> vacías a propósito. Un spike sin números no es un spike, es una spec sobre algo
> que todavía no sabés si funciona, que es exactamente lo que `PLANIFICAR_PROYECTO`
> prohíbe. Lo que sí existe ya es el instrumento, y construirlo forzó seis
> decisiones de diseño que están en la sección 4.

---

## 1. Pregunta que intenta responder

Sobre una obra real y un cambio real hecho por humanos: ¿cuántas anclas migran
bien, cuántas quedan huérfanas y **cuántas migran al lugar equivocado sin avisar**?

El tercer número es el único que decide. Un huérfano visible es un costo; una
migración silenciosa al pasaje equivocado es un hilo que miente y nadie se entera
nunca.

---

## 2. Qué se probó

`[PENDIENTE — correr el experimento]`

| | |
|---|---|
| Obra | `[COMPLETAR]` |
| Revisiones (A → A+k) | `[COMPLETAR]` |
| Comentario de edición | `[COMPLETAR]` |
| Bloques totales / cambiados / perdidos | `[COMPLETAR]` |
| Anclas generadas | `[COMPLETAR]` |
| Umbral de confianza | `[COMPLETAR]` |

| Resultado | n | % |
|---|---|---|
| migrada bien | | |
| **migrada mal (falso positivo)** | | |
| migrada mal por ambigüedad literal | | |
| huérfana evitable | | |
| huérfana correcta | | |
| migró en caso tocado | | |

Desvío de las migraciones malas: `≤5 chars ___ / 6–50 ___ / >50 ___`

**Criterio de fracaso** (de `02_RISKS §R-03`, corregido en §4.3 y §4.4 de este
archivo): falsos positivos con desvío mayor a 50 caracteres por encima del **1%**,
o huérfanas **evitables** por encima del **10%**.

### Prueba de humo del instrumento (no es el resultado)

Corrida sobre texto sintético con erratas fabricadas, sólo para verificar que el
arnés mide: 200 anclas, 60 bloques, 9 cambiados, 3 borrados, un párrafo insertado.
Salió 58% bien / 27% huérfana correcta / 1% huérfana evitable / 7,5% "mal" — y ese
7,5% resultó ser **entero de corrimientos de ≤2 caracteres, máximo 2**, o sea cero
mentiras. Esto no dice nada sobre R-03: el texto sintético usa un vocabulario de
veinte palabras, que es el peor caso posible para el selector de contexto y el
mejor posible para la alineación de bloques por hash. Es la calibración del
instrumento, no la medición.

---

## 3. Respuesta

`[PENDIENTE]` — funciona / no funciona / funciona con estas condiciones.

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

## 5. Cambio que este spike le exige a `01_PRODUCT_PRINCIPLES`

`02_RISKS` anticipó que haría falta y tenía razón. `P-05` prohíbe que un hilo
desaparezca en silencio, pero no dice nada del fallo peor, que es un ancla que no
desaparece: miente. Redacción propuesta, con el número a completar cuando corra el
experimento:

> **MUST** — Toda migración de ancla entre versiones registra una confianza
> explícita. Por debajo del umbral `[N]`, el ancla queda huérfana visible; nunca
> se migra "por las dudas". Ante empate entre dos candidatos, huérfana.
> **MUST NOT** — Migrar un ancla sin dejar registro de la versión de origen, de la
> confianza y del método (posición o concordancia difusa).

Va al registro de cambios de principios con fecha y motivo, no como excepción.

---

## 6. Cómo correrlo

```bash
pip install diff-match-patch

# calibrar el instrumento, sin red
python3 spike_anclas.py humo

# bajar dos revisiones reales separadas por 40 ediciones humanas
python3 spike_anclas.py traer --titulo "El almohadón de plumas" --saltos 40

# medir
python3 spike_anclas.py correr --a rev_A.txt --b rev_B.txt --n 200 \
        --umbral 0.75 --json resultado.json

# de paso, el sondeo de R-04 (02_RISKS §3): cinco obras candidatas
python3 spike_anclas.py sondeo "Obra 1" "Obra 2" "Obra 3" "Obra 4" "Obra 5"
```

Barrer `--umbral` entre 0.6 y 0.9 y `--semilla` en tres valores. Un umbral que se
elige mirando un solo número es un umbral inventado.

**Presupuesto:** 2–3 horas si el arnés no necesita tocarse; el resto del día que
`02_RISKS` reserva es para mirar los fallos a ojo, que es donde está el
aprendizaje real. Si la semana no da, este spike es el que se corre a la semana
que viene: `02_RISKS §Nota de secuencia` ya lo decidió y sigue siendo correcto.
