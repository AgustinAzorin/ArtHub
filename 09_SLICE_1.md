# 09_SLICE_1.md

*artHUB — Fase 7. Versión 0.1, septiembre 2026.*

> **Estado: primera fase que cuesta caro tirar.** Las fases 3 a 6 se escribieron
> antes de correr R-01, R-02 y R-03 y cada archivo lo dijo en su encabezado; el
> costo de haberse equivocado era una tarde de reescritura. Acá deja de serlo: un
> esquema con una obra ingerida, un deploy y diez hilos sembrados no se tira en
> una tarde, y sobre todo no se tira de la cabeza del que lo construyó.
>
> Además, escribir código es literalmente el modo de falla que describe `R-01`:
> es agradable, es medible, da sensación de avance, y no ejercita el músculo que
> el proyecto necesita. Este archivo no resuelve eso —no lo puede resolver un
> archivo—. Lo único que hace es **cortar el slice para que no pueda convertirse
> en el proyecto entero** y poner los dos experimentos de cero horas como puerta
> del slice 2 (§7).

---

## 0. Por qué el corte cae entre leer y escribir

El MVP tiene dos mitades: la de lectura (J-01, más el índice de hilos de
`05_JOURNEYS §3`) y la de escritura (J-02 y J-03). El slice 1 es la primera, y
no por ser "más fácil": por tres razones que salieron de cruzar los pendientes
declarados en `06_MODELO_DOMINIO §8` y `08_RULES §9` contra los dos recorridos.

**Primera: todos los pendientes bloqueantes caen del lado de escribir.**

| Pendiente | Lo desbloquea | ¿Bloquea el slice 1? | ¿Bloquea el slice 2? |
|---|---|---|---|
| `tope_caracteres` (R-005) | Los párrafos reales de las obras | No: no hay selección de usuario | Sí |
| Longitud de prefijo/sufijo (R-001) | Barrido de `03_SPIKE §6` | No, con la salvedad de §4 D-08 | Sí, y ahí se cierra la ventana |
| `umbral_confianza` (R-030) | El mismo barrido | No: el migrador no está en la v1 | No |
| Correo en bandeja de entrada (R-041) | La prueba del primer día | No: el slice 1 no manda un solo correo | Sí, duro: sin correo no hay J-03 |
| Baja de cuenta (I-CU-3) | Decisión de producto | No: no hay cuentas de terceros | Sí, antes del primer usuario |
| Licencia de las anotaciones | Decisión de producto | No: no hay anotaciones de terceros | Sí, antes del primer usuario |

No es casualidad y conviene decirlo con todas las letras: **todo lo que está sin
decidir tiene que ver con que una persona que no es el operador deje algo
adentro.** Mientras nadie deje nada, no hay nada irreversible. El día que entra
el primer usuario, seis pendientes se vuelven deuda con terceros.

**Segunda: el slice 1 es la única parte del MVP que tiene una diferencia real.**
`04_MVP §5` reconoce una sola cosa que Hypothes.is sobre Wikisource no tiene: la
página del pasaje como unidad indexable. Eso es exactamente J-01. Si esa página
no funciona —si no es indexable, si no carga rápido, si la transición pasaje →
visor se siente mal—, el slice 2 no importa: se estaría construyendo la parte que
ya existe gratis en otro lado.

**Tercera, y la que más pesa: el slice 1 sirve igual si `R-02` sale mal.** Una
biblioteca de tres obras con texto canónico versionado y anotación del operador
es exactamente la salida prevista en `00_CONSTRAINTS §3` para el escenario de
fracaso social. El slice 2 no sobrevive a ese escenario; el slice 1 sí. Es la
única forma de construir ahora sin apostar el resultado de un experimento que no
corrió.

---

## 1. Slice 1 es

> La URL pública de un pasaje, servida en HTML, con su hilo completo y el ida y
> vuelta al visor de la obra, sobre una obra real ingerida a mano.

Una frase, sin "y" que agregue alcance. Cubre J-01 pasos 1 a 5. No cubre el paso
6, que es entrar a J-02.

---

## 2. Slice 1 incluye

1. **El esquema** (`migraciones/001_esquema_slice1.sql`): catálogo y ágora, con
   los invariantes de la Fase 5 escritos como constraints y triggers, no como
   comentarios.
2. **Ingesta manual**: un comando que toma un `.txt` ya limpiado a mano, lo
   normaliza según D-07, corta bloques, asigna identidades opacas, hashea, crea
   la versión 1 y la publica. Sin parser TEI, sin conversor de Wikisource, sin
   nada automático (`R-04`).
3. **El visor**: `GET /api/v1/obras/{id}/texto` devolviendo bloques, y
   `/obra/<slug>` renderizado en el servidor desde esos bloques (R-026).
4. **La página del pasaje**: `/pasaje/<slug>` renderizada en el servidor, con
   cita, prefijo y sufijo atenuados, obra, autor y el hilo completo. Incluye el
   render del estado `huerfana` (`I-AN-7`, `05_JOURNEYS J-01` errores), aunque el
   slice 1 no pueda producir uno.
5. **El índice de hilos**: `/obra/<slug>/hilos`, ordenado por
   `(bloque.orden, offset_inicio)` y por nada más (R-020).

Más una cosa que no es software y es parte del entregable: **diez anclas con su
hilo, escritas por el operador leyendo la obra.** No generadas, no de relleno. Es
la parte del slice que se parece al trabajo que mide `R-01`, y es la única
oportunidad de ejercerlo que este slice ofrece.

---

## 3. Slice 1 NO incluye

Con nombre y apellido, misma disciplina que `04_MVP`:

- **Ningún endpoint de escritura.** Ni uno. `POST /borradores`, `POST /anclas`,
  `POST /hilos/{id}/mensajes`, todo el §2 y §3 de `07_API`: fuera.
- Cuentas de usuario, enlace mágico, borrador, sesión, cookie `sid`. La única
  fila de `cuenta` es la del operador, insertada a mano.
- Correo. Ningún tipo, ni el mágico ni el de respuesta. `SPF`/`DKIM`/`DMARC` son
  puerta del slice 2 (§7), no tarea del slice 1.
- Suscripciones, notificaciones, `respuestas_count` actualizado por trigger de
  aplicación (en el slice 1 lo escribe la siembra).
- Migrador, `MigracionAncla`, publicación de una versión 2.
- `GET /api/v1/config`: los cuatro valores que expone son del slice 2. Meterlo
  ahora es exponer un contrato para nadie.
- `GET /cuenta/export`, `DELETE /cuenta`.
- Design system, componentes, tokens, tipografía elegida. La Fase 7 dice que las
  reglas de diseño se extraen **después** del slice, de algo que ya existe.
- Moderación, panel, cualquier pantalla propia del operador (`05_JOURNEYS §0`).

**Y una restricción que es prueba, no gusto: el slice 1 funciona sin
JavaScript.** No es minimalismo. Si J-01 necesita JS para renderizar el hilo, la
apuesta de indexabilidad de `07_API §9.2` —la única diferencia que el MVP tiene—
ya está comprometida, y es mejor enterarse ahora que a los seis meses mirando
Search Console. La selección de texto necesita JS y es del slice 2.

---

## 4. Decisiones de arquitectura

La Fase 7 exige que estén escritas, no supuestas.

**D-01 — Monolito modular, un proceso, un Postgres.** Es el default de la guía y
no hay razón escrita para lo contrario. Los microservicios acá serían un
impuesto.

**D-02 — Cinco módulos con frontera explícita:** `catalogo` (obra, edición,
versión, identidad, bloque, ingesta, normalización), `anclas` (creación y
derivación de selectores, y algún día la migración), `agora` (hilo, mensaje),
`cuentas`, `correo`. **Regla de frontera: `agora` no consulta tablas de
`catalogo`; pide por id a `anclas`.** Es la frontera que hace que el migrador —el
código más peligroso del proyecto, y el que se va a escribir con más presión y
menos tiempo— no tenga que tocar el ágora. En el slice 1 `cuentas` y `correo` son
carpetas casi vacías, y está bien: la frontera se dibuja cuando no cuesta nada.

**D-03 — SSR para `/pasaje` y `/obra`, sin excepción.** Ya lo forzó
`07_API §9.2`. La API de `07_API §1` existe para el visor y para clientes
futuros; las dos páginas que importan no la consumen desde el navegador.

**D-04 — El esquema es la spec, y no lo genera un ORM.** Los invariantes de la
Fase 5 viven en constraints y triggers del motor. Un ORM que "sincroniza modelos"
los pisa en el primer `makemigrations`. Migraciones SQL a mano, numeradas,
versionadas junto al código (`PLANIFICAR_PROYECTO` Fase 10). Se puede usar una
librería de acceso a datos; no una que sea dueña del esquema.

**D-05 — Sin build de front.** HTML servido, un archivo CSS. Empieza a haber
build cuando haya algo que buildear, que es el slice 2.

**D-06 — El ancla lleva un `slug` corto y opaco para la URL pública, y esto es un
cambio a la Fase 5.** `/pasaje/<uuid>` es la unidad que se comparte por WhatsApp
y que indexa Google: un UUID de 36 caracteres es hostil para las dos cosas.
Diez caracteres base32 generados al crear, únicos, inmutables, sin ninguna
información de posición adentro (misma disciplina que `I-IB-2`). Es una columna y
un índice. Va al registro de `06_MODELO_DOMINIO`, no queda como detalle de
implementación (§8).

**D-07 — Normalización `norm-2026-09-a`, escrita antes de la primera obra
(`I-VT-4`, R-027).** Reglas, cerradas: NFC; `\r\n` → `\n`; espacios finales de
línea eliminados; tres o más saltos consecutivos colapsados a dos; espacios
horizontales repetidos colapsados a uno. **No se tocan comillas, guiones,
acentos, mayúsculas ni ortografía de época**: eso es integridad de la obra
(derecho moral, `00_CONSTRAINTS §4`), no formato. Cambiar esta lista es un
`normalizacion_id` nuevo, no un deploy.

**D-08 — Prefijo y sufijo: 32 caracteres provisionales, registrados por fila.**
El valor real lo fija `R-03` y no corrió. La columna `longitud_contexto` guarda
el valor usado en cada ancla, así que re-derivar los selectores de contexto de
las anclas sembradas es un script de veinte líneas mientras las anclas sean todas
del operador. **Esa ventana se cierra el día del primer usuario**, y por eso el
barrido de `--umbral` es puerta del slice 2 y no del 1.

---

## 5. Orden de trabajo

En horas de construcción, no en semanas: la conversión a calendario depende del
`[COMPLETAR]` de `00_CONSTRAINTS §1`, que sigue sin medirse. Con 6 h/semana esto
es un trimestre; con 12, seis semanas. Ese número importa más que todo lo demás
de esta sección.

| # | Paso | Horas | Depende de |
|---|---|---|---|
| 1 | Esquema + migración 001 corriendo en Postgres local | 4 | — |
| 2 | Normalizador D-07 + ingesta a bloques + hash + publicar v1 | 8 | 1 |
| 3 | Elegir 3 obras, verificar dominio público y registrar la evidencia | 3 | — |
| 4 | `GET /obras/{id}/texto` + `/obra/<slug>` SSR | 6 | 2 |
| 5 | `/pasaje/<slug>` SSR, incluido el render de huérfana | 6 | 4 |
| 6 | Índice de hilos por obra | 2 | 5 |
| 7 | Deploy: VPS, Postgres, dominio, TLS, backup fuera del VPS | 6 | 4 |
| 8 | Sembrar 10 anclas con hilo, leyendo | 4 | 5, 7 |

Aproximadamente **39 horas**. El paso 3 no depende de nada y conviene hacerlo
primero: es el único que puede descubrir que una obra elegida no es publicable, y
descubrirlo después del paso 2 tira el paso 2.

El paso 7 está adentro a propósito, aunque un slice pueda terminar en `localhost`.
El piso de 10–15 USD/mes de `00_CONSTRAINTS §2` es una estimación sin verificar, y
éste es el momento barato de convertirla en un número real: si el hosting sale el
triple, cambia la Fase 9 entera y es mejor saberlo ahora.

---

## 6. El slice 1 está listo cuando

> Una persona que no es el operador abre en su teléfono un enlace a
> `/pasaje/<slug>`, entiende de qué obra es sin scrollear, toca "leer la obra",
> el visor abre **en ese pasaje**, vuelve al hilo, y todo eso ocurre sin cuenta y
> con JavaScript desactivado. La obra tiene su verificación de dominio público
> registrada. El índice lista los diez pasajes en el orden del texto. Ninguno de
> los diez hilos lo escribió un script.

No incluye que se vea lindo, y eso no es una concesión: es lo que la Fase 7 pide
explícitamente. Las reglas de diseño se extraen después, de esto.

---

## 7. La puerta del slice 2

El slice 2 (J-02, J-03, cuentas, correo) **no se empieza** hasta que estén las
seis cosas de abajo. Cinco son las que la tabla de §0 marcó como bloqueantes; la
sexta es la que hace que valga la pena.

| # | Requisito | Costo en horas de construcción |
|---|---|---|
| 1 | `R-01`: semana medida en dos columnas + tasa base de proyectos propios | 0 |
| 2 | `R-02`: ágora de cartón corrida, con los cinco números | 0 |
| 3 | `R-03`: `spike_anclas.py` corrido, con barrido de umbral | 2–3 |
| 4 | Licencia de las anotaciones, decidida y escrita | 0 |
| 5 | Baja de cuenta (`I-CU-3`), decidida y escrita | 0 |
| 6 | R-041: los tres correos llegan a bandeja en Gmail y Outlook | 2 |

Cuatro de seis cuestan cero horas de código. Ése es el argumento entero de este
archivo, y es el mismo que `02_RISKS`, `04_MVP`, `05_JOURNEYS`, `06_MODELO_DOMINIO`
y `07_API` vienen escribiendo en su encabezado hace seis archivos: la parte más
barata del proyecto sigue sin hacerse, y no la destraba ninguna decisión técnica.
La diferencia es que ahora hay un lugar concreto donde la falta de esos números
detiene el trabajo en vez de sólo advertirlo.

Si `R-02` falla, no se tira nada de lo construido: se sigue por la biblioteca
personal con anotación (`00_CONSTRAINTS §3`), que es este mismo slice más un
comando de siembra.

---

## 8. Qué le exige este archivo a los anteriores

| Archivo | Cambio |
|---|---|
| `06_MODELO_DOMINIO §5` | **+** `Ancla.slug` (opaco, único, inmutable, sin posición adentro) y `Ancla.longitud_contexto`. Al registro con fecha y motivo (D-06, D-08). |
| `06_MODELO_DOMINIO §3` | Se precisa: `estado = huerfana` implica posición nula; los tres selectores textuales siguen siendo NOT NULL siempre. Es lo que ya decía `07_API §1`, ahora en el esquema. |
| `07_API §1` | La URL canónica del pasaje es `/pasaje/<slug>`, no `<ancla_id>`. `GET /api/v1/anclas/{id}` acepta las dos formas o sólo el slug; se decide al escribirlo. |
| `08_RULES` | **+ R-047**: el slug de un ancla se asigna una vez y no se reusa jamás, ni siquiera si el ancla queda retirada. Mismo motivo que R-028. |
| `04_MVP` | Nada. El slice 1 es un subconjunto estricto; no agrega alcance. |

---

## 9. Registro

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial | Fase 7, escrita con `R-01`, `R-02` y `R-03` todavía sin correr |
