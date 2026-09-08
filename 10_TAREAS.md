# 10_TAREAS.md

*artHUB — Fase 10. Versión 0.1, septiembre 2026.*

> Este archivo no describe el sistema: describe **cómo se escribe una tarea** y
> cómo se ordenan entre sí. Es método, no producto. Ante conflicto con
> `01_PRODUCT_PRINCIPLES` o con cualquier spec del núcleo, pierde.
>
> Existe por una razón concreta. `PLANIFICAR_PROYECTO` Fase 10 dice que el modo
> de falla del desarrollo asistido por IA no es que el modelo invente, sino que
> **lea una spec que dejó de ser verdad hace tres semanas**. Una descripción de
> tarea que reexplica el invariante, el endpoint y la regla es exactamente eso,
> pero peor: es una segunda fuente de verdad que nadie mantiene.

---

## 0. La regla que gobierna todo el archivo

**La tarea apunta, la spec dice.**

La spec es durable: `06_MODELO_DOMINIO`, `07_API`, `08_RULES` viven en el repo,
se versionan con el código y se actualizan en el mismo commit que cambia el
comportamiento. La tarea es transitoria: existe mientras se hace y después se
tira.

Una tarea cita `R-020`, `I-AN-7`, `D-03`. No los transcribe. Si al escribir una
tarea aparece la tentación de copiar el contenido de una spec adentro, el
problema real es que esa spec no está donde el agente la puede leer, y eso se
arregla en el índice raíz (§6), no en la tarea.

---

## 1. Cómo se determina el tipo

Dos preguntas, en este orden. No hay una tercera.

**Pregunta 1 — ¿produce código?**

Si no, el tipo sale de qué la cierra:

| Cierra con | Tipo |
|---|---|
| Números y un criterio de fracaso | **E** — Experimento |
| Una línea escrita en una spec | **D** — Decisión |
| Nada: tiene cadencia, no final | **O** — Operación |

**Pregunta 2 — si produce código: ¿queda algo cuando la deshacés?**

Queda algo si toca el esquema, publica una URL, expone un contrato que alguien
puede empezar a consumir, o abre la puerta a que un tercero deje un dato adentro.

| Respuesta | Tipo |
|---|---|
| No queda nada; se rehace en una tarde | **R** — Construcción reversible |
| Queda | **I** — Construcción irreversible |

Es el mismo criterio de desempate de `02_RISKS §0`: gana el que no se puede
arreglar después.

**Caso de duda.** Si no está claro si una tarea es R o I, es I. El costo de
escribir tres campos de más es una hora; el costo de un contrato público mal
puesto es permanente.

---

## 2. Los cinco tipos

| Tipo | Cierra con | ¿Se delega a la IA? | Ejemplos en este repo |
|---|---|---|---|
| **E** Experimento | Números + criterio de fracaso | Parcial: el arnés sí, la lectura del resultado no | `R-01`, `R-02`, `R-03` |
| **D** Decisión | Una línea en una spec | No | Licencia de anotaciones, `I-CU-3`, umbral de la puerta social |
| **R** Reversible | Funciona en local | Sí | `09_SLICE_1 §5` pasos 1, 2, 6 |
| **I** Irreversible | Criterio observable + spec actualizada | Sí, con correa corta | `09_SLICE_1 §5` pasos 4, 5, 7 |
| **O** Operación | Cadencia sostenida | No | Paso 8 (sembrar anclas), paso 3 (verificación legal), obra de la semana |

---

## 3. Estructura por tipo

El formato es un impuesto proporcional al daño. Una plantilla única de seis
campos aplicada a todo se rellena por trámite en dos semanas y deja de decir
nada.

### E — Experimento

```
PREGUNTA BINARIA   — una sola, respondible con sí o no
PROCEDIMIENTO      — pasos, con lo que se mide en cada uno
NÚMEROS QUE SALEN  — la lista exacta, escrita antes de correr
CRITERIO DE FRACASO— umbral numérico, fijado antes de ver el resultado
QUÉ QUEDA RESTRINGIDO — qué decisión de diseño cierra cada resultado posible
```

El último campo es el que convierte un experimento en input de planificación en
vez de curiosidad. `03_SPIKE_anclas §4` ya lo hace: construir el arnés forzó seis
decisiones de diseño antes de tener un solo número.

El criterio de fracaso se escribe **antes**. Un umbral fijado después de ver el
resultado no es un umbral.

### D — Decisión

```
PREGUNTA           — qué hay que decidir
OPCIONES           — dos o tres, no un abanico
QUÉ SE ROMPE       — con cada opción, concretamente
QUIÉN DECIDE       — el operador, salvo excepción escrita
DÓNDE SE ESCRIBE   — archivo y sección exactos
```

El último campo es obligatorio. Sin él la decisión se toma, se olvida y se
vuelve a discutir en tres semanas. **Una D termina siempre en un commit de spec,
nunca en uno de código.**

Una D nunca se delega. La IA puede listar opciones y contras; elegir es del
operador, y varias de las D pendientes tienen consecuencias legales con su nombre
atrás.

### R — Construcción reversible

Tres líneas. Nada más.

```
ALCANCE       — una frase, sin "y"
ARCHIVOS      — los que puede tocar; nada fuera de la lista
LISTO CUANDO  — verificable mirando algo
```

### I — Construcción irreversible

```
ALCANCE          — una frase, sin "y"
SPECS            — por ID, con orden de prioridad si pueden chocar
FUERA DE ALCANCE — explícito, con nombre y apellido
ARCHIVOS         — los que puede tocar; prohibido refactorizar fuera
LISTO CUANDO     — criterio observable
SPEC A ACTUALIZAR— cuál, si el comportamiento cambió
```

**El campo que más rinde no es `SPECS`, es `FUERA DE ALCANCE`.** Sin él el modelo
hace el trabajo bien y de paso reorganiza dos archivos vecinos. Es la misma
disciplina de `04_MVP §3` y `09_SLICE_1 §3`, bajada al nivel de la tarea.

**Señal de corte mal hecho:** si el `FUERA DE ALCANCE` de una tarea se va a diez
ítems, la tarea está mal cortada. Se parte en dos antes de escribirla mejor.

### O — Operación

No lleva `LISTO CUANDO`, porque no termina.

```
CADENCIA          — cada cuánto
HORAS RESERVADAS  — por semana, del presupuesto de presencia
QUÉ CUENTA COMO HECHO — el criterio de una vuelta, no del total
HASTA CUÁNDO      — o qué la reemplaza
```

Sembrar diez anclas no es un entregable de software: son varias semanas de leer.
Ponerlo en una tabla de horas de construcción junto a "esquema + migración" es un
error de categoría, y es el error que `R-01` predice.

---

## 4. Ejemplo: el paso 5 del slice 1

Tipo **I**: publica una URL y fija la forma canónica del pasaje.

```
ALCANCE: /pasaje/<slug> renderizado en servidor.
SPECS: 07_API §1 (contrato), §9.2 (SSR); 06_MODELO_DOMINIO §5;
       08_RULES R-026; 09_SLICE_1 D-03, D-06, I-AN-7.
       Ante conflicto: 08_RULES > 07_API > 06_MODELO_DOMINIO.
FUERA: ningún endpoint de escritura. Sin JS. Sin CSS más allá de
       legibilidad. No tocar el normalizador ni la ingesta.
ARCHIVOS: rutas de pasaje, plantilla, consulta. Nada más.
LISTO CUANDO: la página carga con JavaScript desactivado, muestra cita
       con prefijo y sufijo atenuados, obra, autor y el hilo completo;
       el estado huérfana renderiza aunque el slice no pueda producir uno.
SPEC A ACTUALIZAR: 07_API §1 si la URL canónica queda en slug.
```

Trece líneas. Todo el detalle vive en los archivos citados, donde se mantiene una
sola vez.

Comparar con el paso 1 del mismo slice, que es **R**:

```
ALCANCE: esquema y migración 001 corriendo en Postgres local.
ARCHIVOS: migraciones/001_esquema_slice1.sql
LISTO CUANDO: la migración corre limpia sobre una base vacía y los
       invariantes de la Fase 5 están como constraints y triggers.
```

---

## 5. Cómo los tipos estructuran el plan

El orden de dependencia entre tipos no es negociable.

**E → D → I.** Un experimento produce el número que cierra una decisión, y la
decisión cierra la ventana de una tarea irreversible. `D-08` es el caso exacto:
prefijo y sufijo quedaron en 32 caracteres provisionales, el valor real lo fija
`R-03`, y la ventana para re-derivar se cierra el día del primer usuario.
Escribir la I antes de correr la E es apostar.

**R no depende de nada, y por eso es peligrosa.** Es agradable, es medible, da
sensación de avance y se puede hacer entera sin haber corrido una sola E. Eso es
literalmente el enunciado de `R-01`.

**O compite por horas con R e I, no con E ni D.** Un plan que suma sólo horas de
construcción está mal presupuestado. Y cuando una semana no alcanza para las dos
cosas, `00_CONSTRAINTS §1` ya fijó qué se corta: se corta R o I, nunca O.

**Consecuencia visible hoy.** De las seis tareas de la puerta del slice 2
(`09_SLICE_1 §7`), cuatro cuestan cero horas de construcción: dos E y dos D.
Siguen postergadas porque ninguna tarea de tipo R las bloquea. Tipar las tareas
hace visible ese patrón; no lo corrige.

---

## 6. Lo que este archivo le exige al repo

| Falta | Por qué bloquea |
|---|---|
| Índice raíz `CLAUDE.md` / `AGENTS.md` con el orden de prioridad entre specs | Sin él, el campo `SPECS` de cada tarea I tiene que declarar la prioridad a mano cada vez, y ante contradicción el agente sigue la spec que leyó último. `PLANIFICAR_PROYECTO` Fase 10 ya lo pedía. |
| Las cinco correcciones de `09_SLICE_1 §8` aplicadas a las specs anteriores | Mientras no estén, hay contradicciones conocidas entre `07_API` y `06_MODELO_DOMINIO`, y ninguna tarea puede citarlas sin ambigüedad. |

---

## 7. Reglas para el agente

Las de `PLANIFICAR_PROYECTO`, sin cambios, más una:

1. No inventar comportamiento de producto: si falta, preguntar.
2. Ante specs en conflicto, seguir el orden de prioridad declarado.
3. No refactorizar fuera del alcance del slice ni de la lista `ARCHIVOS`.
4. Cada cambio de comportamiento actualiza la spec correspondiente, en el mismo
   commit.
5. **Una tarea sin tipo no se empieza.** Si no se puede tipar con las dos
   preguntas de §1, está mal cortada.

---

## 8. Registro

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial | Fase 10, escrita con `R-01`, `R-02` y `R-03` todavía sin correr |
