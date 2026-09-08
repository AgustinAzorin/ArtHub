# 06_MODELO_DOMINIO.md

*artHUB — Fase 5. Versión 0.1, septiembre 2026.*

> **Estado: hereda la condición de `04_MVP` y `05_JOURNEYS`.** Sigue sin correr
> R-01, R-02 y R-03. Lo que este archivo agrega igual es lo mismo que agregó la
> Fase 4: los invariantes son gratis de escribir hoy e imposibles de retrofitear.
> Pero hay una diferencia de grado que conviene decir de frente: **§8 marca cuatro
> campos cuyo valor concreto depende del resultado de R-03 y que no se pueden
> fijar acá.** Escribir el resto no es adelantarse; escribir esos cuatro sí lo
> sería.
>
> Alcance: **sólo las entidades que toca el MVP** de `04_MVP` + las dos que agregó
> `05_JOURNEYS §5`. Colecciones, relaciones tipadas, grupos, obra propia, capas y
> notas privadas **no tienen entidad acá**, ni siquiera "por las dudas". Lo único
> que se reserva son campos discriminadores dentro de entidades que sí existen, y
> están justificados uno por uno en §7.

---

## 0. Mapa

```
Obra ──1:N── Edicion ──1:N── VersionTexto ──1:N── Bloque
                                                    │
                            IdentidadBloque ────────┘   (id estable, transversal a versiones)
                                                    │
                                              Ancla ─┴── 1:1 ── Hilo ──1:N── Mensaje
                                                                  │           │
                                                            Suscripcion    Cuenta
                                                                  └───────────┘

Borrador ──(se consume)──> Ancla + Mensaje + Cuenta
```

Doce entidades, de las cuales cinco son de catálogo (`Obra`, `Edicion`,
`VersionTexto`, `Bloque`, `IdentidadBloque`), tres son el ágora (`Ancla`, `Hilo`,
`Mensaje`), y cuatro son plomería (`Cuenta`, `EnlaceMagico`, `Borrador`,
`Suscripcion`). Si en la Fase 6 aparece una decimotercera, es señal de que el MVP
creció.

---

## 1. Obra

**Purpose** — La cosa de la que se habla, independiente de cualquier texto
concreto. *La metamorfosis* es una `Obra`; la traducción de Borges es una
`Edicion`. Existe para que un hilo anclado a "la obra entera" y las futuras
relaciones tipadas tengan a qué apuntar sin depender de una traducción.

**Invariants**

- I-OB-1 — Ninguna `Obra` es visible públicamente sin `verificacion_dominio_publico` completa (`00_CONSTRAINTS §4`). No hay estado intermedio "publicada pero sin verificar".
- I-OB-2 — `autor_nombre` y `autor_muerte` son inmutables después de publicar; corregirlos exige rehacer la verificación, porque son exactamente los datos de los que depende.
- I-OB-3 — Tiene al menos una `Edicion` con al menos una `VersionTexto` publicada, o no está publicada.

**Fields**

| Campo | Tipo | Null | Nota |
|---|---|---|---|
| `id` | uuid | no | |
| `titulo` | text | no | |
| `autor_nombre` | text | no | Derecho moral: siempre presente (`P-04`, `00_CONSTRAINTS §4`) |
| `autor_muerte` | date | sí | Null sólo para anónimo/colectivo; entonces la verificación explica por qué |
| `wikidata_qid` | text | sí | Identificador canónico del concepto. Sin dependencia en runtime |
| `verificacion` | jsonb | no | `{fuente, quien, cuando, razonamiento, plazo_aplicado}` |
| `estado` | enum | no | `borrador \| publicada \| retirada` |
| `creada_en` | timestamptz | no | |

**Lifecycle** — `borrador → publicada → retirada`. `retirada` no borra: la obra
deja de servirse, sus anclas y hilos siguen existiendo y la URL responde 410 con
el motivo. Nunca se vuelve de `retirada` a `publicada` sin verificación nueva.

**Permissions** — Crear, publicar y retirar: sólo operador. Leer: todos, sin
cuenta.

**Events** — `obra.publicada`, `obra.retirada`.

---

## 2. Edicion

**Purpose** — Una manifestación concreta de la obra: una traducción, una edición
de origen, y más adelante una grabación de LibriVox. Es el nivel donde vive el
problema de las traducciones (§6.1 del concepto). En la v1 hay **una `Edicion` por
`Obra`** y aun así la entidad existe, porque meterla después obliga a reescribir
la clave de todas las anclas.

**Invariants**

- I-ED-1 — `(obra_id, idioma, clave)` es único.
- I-ED-2 — Exactamente una `Edicion` por `(obra_id, idioma)` tiene `es_default = true`. Es una decisión de producto, no de catálogo (§6.1).
- I-ED-3 — `fuente_url` y `licencia_origen` son obligatorias. Una edición sin procedencia registrada no es publicable.

**Fields** — `id`, `obra_id`, `idioma` (bcp47), `clave` (slug: `wikisource-es`,
`trad-borges`), `traductor` (null), `fuente_url`, `licencia_origen`,
`es_default` (bool), `estado`.

**Lifecycle** — Igual que `Obra`, y depende de ella: retirar la obra retira sus
ediciones.

**Permissions** — Sólo operador escribe.

**Events** — `edicion.default_cambiado` (importa: mueve el tráfico entre silos).

---

## 3. VersionTexto

**Purpose** — El texto canónico inmutable. Es la unidad de "no se edita en el
lugar" de `P-05`. Corregir una errata crea una versión nueva y dispara la
migración de anclas.

**Invariants**

- I-VT-1 — **Inmutable después de `publicada`.** Ninguna operación del sistema, ni de moderación, ni del operador, edita el contenido de una versión publicada. Esto es lo que hace que los offsets signifiquen algo.
- I-VT-2 — `numero` es monotónico creciente dentro de la edición, sin huecos.
- I-VT-3 — Exactamente una versión por edición tiene `es_actual = true`, y es la de `numero` máximo entre las publicadas.
- I-VT-4 — Todo el texto está normalizado con `normalizacion_id` registrado. Dos versiones de la misma edición normalizadas con reglas distintas hacen incomparables sus hashes de bloque, o sea, rompen el reanclaje sin avisar. **Cambiar las reglas de normalización es un evento de esquema, no un deploy.**
- I-VT-5 — Publicar una versión con `numero > 1` requiere una `MigracionAncla` (§9) terminada para todas las anclas de la edición. No hay estado "publicada a medias".

**Fields** — `id`, `edicion_id`, `numero` (int), `normalizacion_id` (text, versión
del normalizador), `hash_contenido`, `es_actual`, `publicada_en`,
`comentario_cambio` (text, para el aviso de huérfano visible).

**Lifecycle** — `preparada → publicada → superada`. Nunca `borrada`: una versión
superada sigue siendo el referente de las anclas huérfanas que muestran su cita
original.

**Permissions** — Sólo operador.

**Events** — `version.publicada` → dispara migración.

---

## 4. IdentidadBloque y Bloque

Son dos entidades y separarlas es el hallazgo de `03_SPIKE §4.2` convertido en
esquema. Fusionarlas es el error caro.

### 4.1 IdentidadBloque

**Purpose** — El identificador estructural **estable** al que apunta el nivel
superior de un ancla. Vive a nivel de `Edicion`, no de `VersionTexto`, y sobrevive
a todas las versiones.

**Invariants**

- I-IB-1 — Se asigna una vez y **nunca se reusa**, ni siquiera si el bloque se borra en una versión posterior.
- I-IB-2 — **No se deriva de la posición.** Ni `p-0001`, ni `capitulo-3-parrafo-14`. Contador opaco por edición. La excepción son los ids derivados de la estructura propia de la obra (`acto-1/escena-2/verso-15`), que son estables por definición y se usan cuando existen.
- I-IB-3 — Su transporte entre versiones es por alineación de bloques, nunca por índice.

**Fields** — `id`, `edicion_id`, `ref_canonica` (text, null: `II.4.15` cuando la
obra tiene sistema de citación), `creada_en_version`.

### 4.2 Bloque

**Purpose** — El contenido concreto de una identidad en una versión concreta.

**Invariants**

- I-BL-1 — `(version_id, identidad_id)` es único.
- I-BL-2 — `hash` cubre el texto normalizado del bloque. Es lo que acota el reanclaje: si el hash no cambió, ninguna ancla del bloque se toca (§6 del concepto).
- I-BL-3 — `orden` es un campo propio, denso y recalculable por versión. **Es el campo que permite el índice de hilos "en el orden en que aparecen en el texto" (`05_JOURNEYS §3`) sin que el id estructural cargue con la posición.** Sin este campo separado, I-IB-2 y el índice de hilos son incompatibles, y ese conflicto es lo que este archivo existe para no descubrir en la Fase 7.
- I-BL-4 — `tipo` viene del subconjunto mínimo de TEI y es cerrado en la v1: `parrafo | verso | encabezado | acotacion`. Ampliarlo es una decisión registrada.

**Fields** — `id`, `version_id`, `identidad_id`, `orden` (int), `tipo` (enum),
`texto` (text), `hash` (text), `offset_global` (int, denormalizado para el visor).

**Permissions** — Escritura sólo por la ingesta. Lectura pública.

---

## 5. Ancla

**Purpose** — La unidad del proyecto (`P-01`). Un lugar preciso de un texto
concreto, con redundancia suficiente para sobrevivir a que ese texto cambie.

**Invariants** — Son los más importantes del archivo.

- I-AN-1 — **Inmutable en su contenido selector.** Un ancla nunca se re-apunta. Cuando cambia la versión, se crea un ancla nueva ligada a la anterior por `derivada_de`, y la vieja queda como registro histórico. Editar el rango en el lugar destruye la trazabilidad que `P-05` exige y hace imposible auditar una migración mala.
- I-AN-2 — Los tres selectores son **obligatorios y se persisten juntos al crear**: posición (`bloque_inicio + offset_inicio`, `bloque_fin + offset_fin`), cita (`texto_citado`), contexto (`prefijo`, `sufijo`). Un ancla con dos selectores no se guarda: falla la escritura.
- I-AN-3 — **Cruza bloques en el esquema, no en la interfaz** (`05_JOURNEYS §4`). `bloque_fin` puede ser distinto de `bloque_inicio` desde el día uno; la v1 recorta la selección al primer bloque en el cliente **y valida esa restricción también en el servidor**, porque una restricción de interfaz que el API no sostiene no es una restricción.
- I-AN-4 — `bloque_inicio.orden ≤ bloque_fin.orden`, y si son iguales, `offset_inicio < offset_fin`. Rango vacío prohibido.
- I-AN-5 — `1 ≤ (fin − inicio) ≤ tope_caracteres`. El tope se fija mirando los párrafos reales de las tres obras elegidas (`05_JOURNEYS §4`), no a ojo, pero el invariante existe desde ya.
- I-AN-6 — El ancla apunta a `(obra, edicion, version, identidad_bloque, offset)`. Los cinco, siempre. Guardar sólo los tres primeros es el modelo frágil que §6 del concepto descarta.
- I-AN-7 — **`estado = huerfana` es un estado normal, no un error.** Toda consulta que renderice anclas maneja el caso; ninguna lo filtra por defecto. `estado = huerfana` implica posición nula (`bloque_inicio_id`, `offset_inicio`, `bloque_fin_id`, `offset_fin`): el ancla ya no apunta a un bloque vigente. Los tres selectores textuales (`texto_citado`, `prefijo`, `sufijo`) siguen siendo `NOT NULL` siempre, huérfana incluida: son lo único que le queda al ancla para mostrarse (corrección de `09_SLICE_1 §8`).
- I-AN-8 — `confianza_migracion` y `metodo_migracion` son obligatorios en toda ancla con `derivada_de` no nulo. Ancla migrada sin registro de confianza y método = escritura rechazada (`03_SPIKE §5`).

**Fields**

| Campo | Tipo | Null | Nota |
|---|---|---|---|
| `id` | uuid | no | |
| `slug` | text | no | Opaco, único, inmutable, sin información de posición adentro; asignado una vez y no se reusa (`09_SLICE_1 D-06`, `R-047`). URL pública: `/pasaje/<slug>` |
| `version_id` | uuid | no | Denormalizado desde el bloque: se consulta en cada render |
| `bloque_inicio_id` / `offset_inicio` | uuid / int | sí | `NULL` si `estado = huerfana` (`09_SLICE_1 §8`) |
| `bloque_fin_id` / `offset_fin` | uuid / int | sí | Iguales al inicio en la v1; `NULL` si `estado = huerfana` |
| `texto_citado` | text | no | Selector de cita |
| `prefijo` / `sufijo` | text | no | Selector de contexto; longitud fija y registrada |
| `longitud_contexto` | int | no | Longitud de `prefijo`/`sufijo` usada al crear esta ancla, registrada por fila para poder re-derivar sin invalidar lo viejo (`09_SLICE_1 D-08`) |
| `alcance` | enum | no | `rango \| bloque \| obra`. En la v1 sólo se crea `rango` desde la interfaz; los otros existen en el modelo (`05_JOURNEYS`, errores de J-02) |
| `estado` | enum | no | `viva \| huerfana \| retirada` |
| `derivada_de` | uuid | sí | Ancla de la versión anterior |
| `confianza_migracion` | numeric | sí | Obligatoria si `derivada_de` |
| `metodo_migracion` | enum | sí | `posicion \| difusa \| manual` |
| `creada_por` | uuid | sí | Null = sembrada por ingesta |
| `creada_en` | timestamptz | no | Las fechas se guardan bien desde hoy: es lo único que el diario de lectura futuro necesita del pasado |

**Lifecycle** — `viva → huerfana` (migración sin confianza suficiente) o
`viva → viva'` (nueva ancla derivada). `retirada` sólo por moderación del hilo, y
aun así el ancla se muestra con aviso, no desaparece (`P-05`, `05_JOURNEYS J-03`).

**Permissions** — Crear: cualquier cuenta, y también un borrador anónimo en
tránsito (§11). Cambiar estado: sólo el sistema de migración y la moderación.
**Nadie edita un ancla, nunca.**

**Events** — `ancla.creada`, `ancla.huerfanizada`, `ancla.migrada`.

---

## 6. Hilo

**Purpose** — La conversación colgada de un ancla. En la v1, **uno por ancla**.

**Invariants**

- I-HI-1 — `ancla_id` es único: relación 1:1. La agrupación de selecciones solapadas está fuera de la v1 (`04_MVP`), así que dos subrayados parecidos dan dos hilos gemelos y eso es tolerado a propósito. La 1:1 es lo que hace barato levantarla después: agrupar es agregar una entidad `Debate` por encima, no partir esta.
- I-HI-2 — No existe hilo sin ancla (`P-01` MUST NOT).
- I-HI-3 — `respuestas_count` es densidad agregada por pasaje, permitida por la excepción explícita de `P-03`. **No existe ningún contador equivalente por `Cuenta`.** Si alguna vez se necesita uno, es un cambio de principio con fecha, no un campo.
- I-HI-4 — Tiene al menos un `Mensaje`. Un hilo se crea con su primer mensaje en la misma transacción o no se crea.

**Fields** — `id`, `ancla_id` (unique), `estado` (`abierto | cerrado | retirado`),
`respuestas_count` (int), `creado_en`, `ultimo_mensaje_en`.

**Lifecycle** — `abierto → retirado` (moderación de conducta, `P-07`). `retirado`
muestra un aviso en el lugar del hilo y deja el ancla viva.

**Permissions** — Crear: cuenta o borrador. Retirar: operador. Leer: todos, sin
cuenta, indexable (`P-02` MUST).

**Events** — `hilo.creado`, `hilo.retirado`.

---

## 7. Mensaje

**Purpose** — Prosa dentro de un hilo. El primero abre, los demás responden.

**Invariants**

- I-ME-1 — `orden` estrictamente creciente por hilo. Sin anidamiento: la v1 es lineal.
- I-ME-2 — El primer mensaje del hilo no se puede retirar dejando el hilo en pie: retirar el primero retira el hilo.
- I-ME-3 — El texto es plano con un subconjunto mínimo de marcado. Sin HTML de usuario.
- I-ME-4 — Editable por su autor durante una ventana corta; después, inmutable. Un hilo cuya primera intervención cambia de sentido tres días después rompe las respuestas que le contestaron.
- I-ME-5 — `retirado` conserva la fila y muestra el hueco. Nada desaparece en silencio (`P-05`, extendido a moderación por `05_JOURNEYS J-03`).

**Fields** — `id`, `hilo_id`, `cuenta_id`, `orden` (int), `texto`, `tipo`
(enum `publico`; el discriminador nace con un solo valor y admite `nota_privada` y
`subrayado` sin migración — `05_JOURNEYS §4`), `estado`, `creado_en`,
`editado_en` (null).

**Permissions** — Crear: cualquier cuenta (la lectura como llave no está en la v1;
recorte legítimo sobre `P-02`). Editar: autor, dentro de la ventana. Retirar:
autor u operador.

**Events** — `mensaje.publicado` → dispara notificaciones (§10).

---

## 8. Lo que este archivo NO puede fijar todavía

Cuatro valores, y ninguno se inventa acá:

| Valor | Lo fija | Mientras tanto |
|---|---|---|
| `umbral_confianza` de migración | El barrido de `--umbral` de `03_SPIKE §6` | El campo existe y es NOT NULL en toda ancla migrada; el número, no |
| Longitud de `prefijo`/`sufijo` | El mismo spike: es la palanca contra la ambigüedad literal (`03_SPIKE §4.4`) | Longitud fija y registrada en la fila, para poder cambiarla sin invalidar lo viejo |
| `tope_caracteres` por selección | Los párrafos reales de las tres obras | Invariante escrito, valor pendiente |
| Reglas de `normalizacion_id` | La ingesta manual de las primeras obras | Se versiona desde la primera obra, aunque haya una sola regla |

Y una decisión de la Fase 6, no de ésta: si `R-03` da falsos positivos
irrecuperables, `04_MVP §6` obliga a anclas **sólo a nivel de bloque, sin offset**.
En ese escenario los campos `offset_*` quedan en el esquema con valor `null`
permitido y la interfaz deja de producirlos. Vale la pena notar que ese cambio es
barato **precisamente porque el ancla es de dos niveles**: se apaga uno.

---

## 9. MigracionAncla

**Purpose** — El registro auditable de qué pasó cuando cambió una versión. No es
log: es dominio, porque `P-05` exige poder responder "por qué este hilo dice que
el pasaje cambió".

**Invariants**

- I-MI-1 — Una fila por ancla por migración, incluidas las que quedaron huérfanas y las que no se tocaron.
- I-MI-2 — Inmutable.
- I-MI-3 — Ante empate entre dos candidatos: huérfana. Nunca "por las dudas" (`03_SPIKE §5`).

**Fields** — `id`, `version_origen`, `version_destino`, `ancla_origen`,
`ancla_destino` (null si huérfana), `confianza`, `metodo`, `resultado`
(`migrada | huerfana | intacta`), `corrida_en`.

**Nota de alcance:** el **migrador no se construye en la v1** (`04_MVP`), pero la
tabla nace igual. Cuesta una migración de esquema ahora y una reescritura después.

---

## 10. Cuenta, EnlaceMagico, Borrador, Suscripcion

### Cuenta

**Invariants**

- I-CU-1 — `correo` único, `seudonimo` único, ambos obligatorios. **No hay campo de nombre real ni de contraseña**, y no es un olvido: es `00_CONSTRAINTS §4` (minimización, Ley 25.326) y `05_JOURNEYS §4`.
- I-CU-2 — Ningún total acumulable en el perfil (`P-03` MUST NOT). Lo que se muestra se calcula listando, no contando.
- I-CU-3 — Baja: el export está siempre disponible y la baja anonimiza la cuenta dejando los mensajes con autoría neutra, o los retira, a elección de la persona. Se decide en los términos antes del primer usuario, no después.

**Fields** — `id`, `correo`, `seudonimo`, `estado` (`activa | suspendida |
anonimizada`), `creada_en`.

### EnlaceMagico

- I-EM-1 — Un solo uso, TTL 30 minutos, invalidado al usarse (`05_JOURNEYS J-02`).
- I-EM-2 — Se guarda el hash del token, nunca el token.
- I-EM-3 — Puede llevar un `borrador_id` adjunto: es lo que hace que el borrador sobreviva al viaje por correo.

### Borrador

**Purpose** — La pieza que permite escribir antes de registrarse. Es dominio y no
caché: sin él, J-02 se invierte y se pierde el visitante que `P-02` protege.

- I-BO-1 — Guarda la selección completa (los tres selectores ya resueltos) y el texto, del lado del servidor.
- I-BO-2 — TTL propio; se limpia solo; nunca es visible públicamente.
- I-BO-3 — Al consumirse crea `Ancla + Hilo + Mensaje + Cuenta` en **una transacción**. Un borrador consumido a medias que deja un ancla sin hilo viola I-HI-4.

### Suscripcion

**Purpose** — A quién se le avisa. Es el único mecanismo de retorno de la v1
(`05_JOURNEYS J-03`), así que es entidad, no un booleano en `Cuenta`.

- I-SU-1 — Se crea automáticamente al abrir un hilo o al responder en él.
- I-SU-2 — Baja **por hilo**, con enlace de un clic en cada correo, sin login.
- I-SU-3 — Un mensaje nuevo genera **un correo por suscriptor distinto del autor**. No hay digest, no hay agrupación, no hay otro tipo de aviso (`05_JOURNEYS §5`).
- I-SU-4 — Entrega registrada. El correo es infraestructura crítica: si cae en spam, no hay sitio. Se verifica contra Gmail y Outlook el primer día.

---

## 11. Eventos del dominio

Lista cerrada de la v1. Se emiten para desacoplar el correo del request, y para
poder calcular las métricas de `00_CONSTRAINTS §3` sin instrumentar a mano.

| Evento | Consumidor v1 |
|---|---|
| `obra.publicada` | — (métrica de catálogo) |
| `version.publicada` | Migrador (fuera de v1; el evento existe) |
| `ancla.creada` | Índice de hilos |
| `ancla.huerfanizada` | Render del aviso |
| `hilo.creado` | Índice de hilos; métrica "hilos fuera de la destacada" (`P-09`) |
| `mensaje.publicado` | Correo a suscriptores; `respuestas_count`; métrica de latencia de respuesta (J-03) |

La métrica que gobierna la puerta social —*hilos con más de tres respuestas por
semana, la mitad fuera de la destacada*— se responde con `hilo` + `obra` + fecha.
No hace falta analítica.

---

## 12. Tres cosas que este archivo destapó y que hay que decidir

Ninguna es un detalle de implementación.

1. **`Bloque.orden` vs. I-IB-2 (§4.2).** El índice de hilos ordenado por posición y los ids estructurales no derivados de la posición son requisitos que se pisan, y sólo dejan de pisarse si el orden es un campo aparte, recalculado por versión. Está resuelto arriba, pero conviene saber que es la única solución: cualquier intento de leer el orden del identificador reintroduce el bug de `03_SPIKE §4.2`.

2. **Cierre transaccional de `Borrador` (I-BO-3).** Cuatro entidades en una transacción es la operación más compleja de la v1 y la que más se rompe bajo error parcial (correo entregado, enlace usado, transacción fallida). Merece los primeros tests de la Fase 8.

3. **La baja de cuenta (I-CU-3) no está decidida y es bloqueante para los términos.** `00_CONSTRAINTS §5` promete export permanente pero no dice qué pasa con los mensajes de alguien que se va: si se retiran, los hilos donde participó quedan agujereados; si se quedan con autoría neutra, la persona no controla su prosa. Hay que elegir **antes del primer usuario**, igual que la licencia de las anotaciones, y por el mismo motivo: después exige permiso individual.

---

## 13. Qué sigue

Fase 6: contratos (`API.md`) de los endpoints que tocan J-01, J-02 y J-03, y
`RULES.md` con las reglas `R-xxx` derivadas de los invariantes de acá. La primera
candidata es la regla de cierre del borrador, y la segunda la de "ante empate,
huérfana".

**Recordatorio incómodo, por última vez:** las fases 3, 4 y 5 están escritas y
`02_RISKS` sigue sin un solo número. El próximo movimiento sensato no es la Fase 6;
es la semana medida de R-01, el ágora de cartón de R-02 y correr
`spike_anclas.py`. Cuatro archivos de spec sin un experimento corrido es
exactamente el antipatrón que la guía nombra en su primera fila.

---

## 14. Registro

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial | Fase 5, escrita antes de la Fase 2 igual que 04 y 05 |
| 2026-09-09 | §5: + `Ancla.slug` y `Ancla.longitud_contexto`; precisión de que `estado = huerfana` implica posición nula y los tres selectores textuales siguen `NOT NULL` siempre | Correcciones de `09_SLICE_1 §8` (D-06, D-08; la corrección de posición nula está citada ahí como "§3" pero es de Ancla, §5) |
