# 07_API.md

*artHUB — Fase 6. Versión 0.1, septiembre 2026.*

> **Estado: hereda la condición de `04_MVP`, `05_JOURNEYS` y `06_MODELO_DOMINIO`, y la agrava.**
> `06_MODELO_DOMINIO §13` dice que el próximo movimiento sensato no es esta fase.
> Sigue teniendo razón. Lo que este archivo puede reclamar como valor es más chico
> que lo que reclamaron las fases 4 y 5: los journeys destaparon huecos de producto
> y los invariantes son irretrofiteables, pero un contrato HTTP es reescribible en
> una tarde y no tiene ningún usuario que lo consuma. **Se escribe entendiendo que
> es el archivo más barato de tirar de los siete.**
>
> Aun así hay tres cosas que sólo aparecen al escribir los endpoints y están en §9:
> el orden en que se resuelven los selectores, quién es dueño de la URL canónica
> del pasaje, y que la transacción de `I-BO-3` no cabe en un solo request.

Alcance: sólo los endpoints que tocan J-01, J-02 y J-03. Nada más entra.

---

## 0. Convenciones

- **Base:** `/api/v1`. Las URLs de página (`/pasaje/<id>`, `/obra/<slug>`) son del servidor de HTML, no de este contrato; §9.2 explica por qué importa la distinción.
- **Auth:** cookie de sesión `sid`, `HttpOnly`, `Secure`, `SameSite=Lax`, larga (90 días, renovada al usarse). No hay bearer tokens, no hay contraseñas (`05_JOURNEYS §4`).
- **Lectura sin cuenta, siempre** (`P-02` MUST). Ningún `GET` de este archivo devuelve 401.
- **Errores:** `application/problem+json` (RFC 9457) con `type`, `title`, `status`, `detail`, `code`. `code` es estable y testeable; `detail` es prosa y puede cambiar.
- **Cache:** los `GET` de texto canónico son inmutables por `(edicion, version)` → `Cache-Control: public, max-age=31536000, immutable` + `ETag`. Los `GET` de hilos, `max-age=0, must-revalidate`.
- **Rate limit:** por IP en todos los `POST` anónimos. Es la única defensa antispam de la v1 junto con el ida y vuelta por correo (`04_MVP`: no hay herramientas de moderación).
- **Sin paginación donde no hace falta:** con 3 a 5 obras y pocos hilos, paginar mensajes es complejidad sin caso. Se pagina sólo el índice de hilos por obra, y por cursor, para no reescribirlo después.

---

## 1. Lectura pública

### `GET /api/v1/obras`

La biblioteca. Sin parámetros.

**200**
```json
{ "obras": [ { "id": "uuid", "titulo": "…", "autor_nombre": "…",
               "edicion_default": { "id": "uuid", "idioma": "es", "clave": "wikisource-es" },
               "version_actual": 1 } ] }
```
Sólo `estado = publicada` (`I-OB-1`). El destacado de la semana **no está acá**: es un enlace editado a mano en la portada (`04_MVP`).

### `GET /api/v1/obras/{obra_id}`

Metadata + ediciones + versión actual. Incluye `verificacion.fuente` y `licencia_origen`, que son públicos por `I-ED-3` y `00_CONSTRAINTS §4`.

- **404** `obra_no_encontrada`
- **410** `obra_retirada` — con `motivo`. No es 404: `06_MODELO_DOMINIO §1` lo exige explícitamente.

### `GET /api/v1/obras/{obra_id}/texto`

El visor. Query: `edicion` (default: la `es_default`), `version` (default: la `es_actual`).

**200**
```json
{ "edicion_id": "uuid", "version_id": "uuid", "numero": 1,
  "normalizacion_id": "norm-2026-09-a",
  "bloques": [ { "identidad_id": "uuid", "orden": 1, "tipo": "parrafo",
                 "ref_canonica": null, "offset_global": 0, "texto": "…" } ] }
```

**Se devuelven bloques, no un string.** El cliente no puede reconstruir un ancla sin saber en qué bloque cayó la selección, y calcular eso a partir de HTML renderizado reintroduce exactamente la fragilidad que `§6` del concepto elimina. El `texto` de cada bloque es el texto normalizado, carácter a carácter idéntico al que la ingesta hasheó (`I-BL-2`); si el cliente lo transforma para mostrarlo, los offsets mienten.

Obras cortas (30–40 minutos de lectura): una sola respuesta, sin paginación.

### `GET /api/v1/obras/{obra_id}/hilos`

El índice de hilos de `05_JOURNEYS §3`. Query: `edicion`, `version`, `cursor`, `limite` (default 50, techo 200).

Orden: `Bloque.orden`, luego `offset_inicio`. **Nunca por actividad ni por `respuestas_count`** — el orden lo da el texto (`P-03`, y `I-BL-3` es el campo que lo permite sin romper `I-IB-2`).

**200**
```json
{ "items": [ { "ancla_id": "uuid", "bloque_orden": 12, "ref_canonica": null,
               "texto_citado": "…", "estado_ancla": "viva",
               "respuestas_count": 3, "ultimo_mensaje_en": "…" } ],
  "cursor_siguiente": "…" }
```

`respuestas_count` viaja porque es densidad agregada por pasaje, la única forma de número permitida (`I-HI-3`, excepción explícita de `P-03`). No existe ningún endpoint que devuelva totales por cuenta, y agregarlo es un cambio de principio con fecha, no un endpoint.

Las anclas `huerfana` **se incluyen** (`I-AN-7`: ninguna consulta las filtra por defecto).

### `GET /api/v1/anclas/{slug}`

La unidad del sitio. Es lo que consume la página del pasaje de J-01. La URL canónica del pasaje es `/pasaje/<slug>` (`09_SLICE_1 D-06`), no `/pasaje/<ancla_id>`, y este endpoint acepta únicamente el `slug` del ancla: es la forma decidida por el operador, no una opción entre dos.

**200**
```json
{ "ancla": { "id": "uuid", "estado": "viva", "alcance": "rango",
             "texto_citado": "…", "prefijo": "…", "sufijo": "…",
             "bloque_inicio": { "identidad_id": "uuid", "orden": 12, "ref_canonica": null },
             "offset_inicio": 140, "offset_fin": 168,
             "version_id": "uuid", "aviso_version": null },
  "obra": { "id": "uuid", "titulo": "…", "autor_nombre": "…" },
  "hilo": { "id": "uuid", "estado": "abierto", "respuestas_count": 3,
            "mensajes": [ { "id": "uuid", "orden": 1, "seudonimo": "…",
                            "texto": "…", "creado_en": "…", "editado_en": null,
                            "estado": "publicado" } ] } }
```

- `prefijo` y `sufijo` no son sólo selectores de reanclaje: acá se usan **como producto**, para que la página no parezca un tuit (`05_JOURNEYS J-01`, segundo punto de fuga). Ya están en el esquema; el contrato los expone.
- Ancla huérfana → `estado: "huerfana"`, `aviso_version` con `comentario_cambio` de la versión superada, y `bloque_inicio: null`. **200, no 404.** La v1 no la va a producir, pero el contrato la contempla porque el esquema la permite desde el día uno (`05_JOURNEYS J-01`, errores).
- Mensaje retirado → la fila viaja con `estado: "retirado"` y sin `texto` (`I-ME-5`: se muestra el hueco).
- Hilo retirado → `hilo.estado: "retirado"`, `mensajes: []`, el ancla sigue viva (`I-HI-...`, `05_JOURNEYS J-03`).
- **404** `ancla_no_encontrada`.

Este endpoint no requiere cuenta, no setea cookies y es indexable. Si algún día devuelve 401 en algún camino, se rompió `P-02`.

---

## 2. Escritura: crear un hilo (J-02)

El recorrido es **borrador → correo → consumo**, y son tres requests, no uno. §9.3 explica por qué no se puede colapsar.

### `POST /api/v1/borradores`

Anónimo. Es el paso 3 de J-02: envía **antes** de que se le pida nada.

**Request**
```json
{ "version_id": "uuid",
  "seleccion": { "bloque_inicio_id": "uuid", "offset_inicio": 140,
                 "bloque_fin_id": "uuid", "offset_fin": 168 },
  "texto": "prosa del primer mensaje" }
```

El cliente manda **posición**; el servidor deriva `texto_citado`, `prefijo` y `sufijo` del texto canónico y los persiste resueltos (`I-BO-1`). Ver §9.1: que el cliente no mande la cita no es un detalle de diseño, es la única forma de que los tres selectores sean consistentes entre sí.

**Validación** (todo también en servidor, `I-AN-3`):

| Regla | Falla |
|---|---|
| Rango no vacío (`I-AN-4`) | 422 `seleccion_vacia` |
| `bloque_fin_id == bloque_inicio_id` en la v1 | 422 `seleccion_cruza_bloques` |
| Largo ≤ `tope_caracteres` (`I-AN-5`) | 422 `seleccion_demasiado_larga` |
| Bloques pertenecen a `version_id` | 422 `seleccion_invalida` |
| Offsets dentro del bloque | 422 `seleccion_invalida` |
| `texto` no vacío, ≤ 8000 chars | 422 `mensaje_vacio` / `mensaje_demasiado_largo` |

**201** `{ "borrador_id": "uuid", "expira_en": "…" }`

`tope_caracteres` está `[PENDIENTE]` (`06_MODELO_DOMINIO §8`). Mientras tanto el endpoint devuelve el valor vigente en `GET /api/v1/config`, para que la interfaz no lo tenga hardcodeado y el día que se fije sea un cambio de una fila.

### `POST /api/v1/auth/enlace`

Paso 4: recién acá se pide correo.

**Request** `{ "correo": "…", "seudonimo": "…", "borrador_id": "uuid" }`

- `seudonimo` obligatorio si el correo no tiene cuenta, ignorado si la tiene.
- **202 siempre**, aunque el correo ya exista, no exista o sea de una cuenta suspendida. Un 409 "ese correo ya tiene cuenta" convierte el endpoint en un oráculo de quién está registrado, y con seudónimos eso es exactamente lo que `00_CONSTRAINTS §4` (minimización) evita.
- **409** `seudonimo_ocupado` es la única excepción, y es inevitable: `seudonimo` es único (`I-CU-1`) y hay que poder elegir otro sin perder el borrador. Se devuelve **antes** de mandar el correo.
- **422** `correo_invalido`. **429** con `Retry-After`.
- **410** `borrador_vencido` — con el texto del borrador en el cuerpo, para que la interfaz lo reponga en el editor. Perder la prosa acá es perder a la persona.

### `POST /api/v1/auth/sesion`

Paso 6: el enlace del correo. `{ "token": "…" }`

Efectos, **en una sola transacción** (`I-BO-3`):
1. Valida el token (hash, un solo uso, TTL 30 min — `I-EM-1`, `I-EM-2`).
2. Crea `Cuenta` si no existe.
3. Si el enlace lleva `borrador_id` vigente: crea `Ancla + Hilo + Mensaje` y consume el borrador.
4. Crea `Suscripcion` al hilo (`I-SU-1`).
5. Setea `sid`.

**200** `{ "cuenta": { "seudonimo": "…" }, "ancla_id": "uuid" }` → la interfaz redirige a `/pasaje/{ancla_id}`.

- **401** `enlace_invalido` — token desconocido, ya usado o vencido. Un solo código para los tres: distinguirlos le dice a un atacante cuál acertó.
- **409** `borrador_ya_consumido` — reintento del mismo enlace después de éxito. Devuelve el `ancla_id` existente en vez de fallar seco, porque el caso real es "toqué el enlace dos veces desde el correo".
- **410** `borrador_vencido` — el enlace vale igual: se crea la cuenta y se inicia sesión, pero sin hilo. Se responde con el texto del borrador. La cuenta es lo caro de conseguir; no se tira por un TTL.

**Idempotencia:** la da el token, que es de un solo uso. No hace falta `Idempotency-Key` acá. Sí en §3.

### `POST /api/v1/anclas`

El mismo J-02 con sesión ya iniciada: colapsa borrador y consumo en un request. Mismo cuerpo que `POST /borradores`, misma validación, crea `Ancla + Hilo + Mensaje + Suscripcion` en una transacción.

- **201** `{ "ancla_id": "uuid", "hilo_id": "uuid" }`
- **401** `sesion_requerida`
- Header `Idempotency-Key` obligatorio: el doble clic sobre "enviar" produce dos hilos gemelos sin él, y `04_MVP` ya tolera hilos gemelos por selecciones parecidas — no hace falta agregarlos por reintento.

---

## 3. Escritura: responder (J-03)

### `POST /api/v1/hilos/{hilo_id}/mensajes`

`{ "texto": "…" }`, header `Idempotency-Key` obligatorio.

- **201** `{ "mensaje_id": "uuid", "orden": 4 }`; emite `mensaje.publicado`, incrementa `respuestas_count`, crea la `Suscripcion` del que responde (`I-SU-1`), encola un correo por suscriptor distinto del autor (`I-SU-3`).
- **401** `sesion_requerida` — la interfaz manda al recorrido de §2 conservando el borrador.
- **403** `hilo_cerrado` / `hilo_retirado`.
- **404** `hilo_no_encontrado`.
- Cualquier cuenta responde cualquier hilo: la lectura como llave no está en la v1 (`04_MVP`, recorte legítimo sobre `P-02`).

### `PATCH /api/v1/mensajes/{mensaje_id}`

`{ "texto": "…" }`. Sólo el autor, sólo dentro de la ventana de edición (`I-ME-4`).

- **200** con `editado_en` seteado. **403** `no_es_autor` / **409** `ventana_de_edicion_cerrada`.
- La ventana está en `GET /config`. Un valor, no una constante repartida por el código.

### `DELETE /api/v1/mensajes/{mensaje_id}`

Retira, no borra (`I-ME-5`). Si es el primero del hilo, retira el hilo (`I-ME-2`) y **deja el ancla viva** (`P-05` extendido).

- **204**. **403** `no_es_autor`.

### `POST /api/v1/suscripciones/baja`

`{ "token": "…" }` — el enlace de un clic de cada correo, **sin login** (`I-SU-2`). Token por `(cuenta, hilo)`, no vence. **204** siempre que el token sea válido, incluso si ya estaba dado de baja.

---

## 4. Cuenta

### `GET /api/v1/cuenta/export`

Export completo, siempre disponible, sin pedirlo por correo (`00_CONSTRAINTS §5`, `P-08`). Devuelve JSON + Markdown en un zip: mensajes, anclas creadas, citas, fechas, y la URL de cada ancla. Con sesión. **200**, `Content-Disposition: attachment`.

En la v1 no hay diario de lectura ni notas privadas, así que el export es chico. Existe igual porque la promesa es del día uno, no de cuando haya algo que exportar.

### `DELETE /api/v1/cuenta`

Decidido (`I-CU-3`, `06_MODELO_DOMINIO §10`): la baja **anonimiza, no retira**. Con sesión.

**Qué se borra:** `correo`, todas las sesiones activas (se invalida `sid` en todo dispositivo) y las preferencias asociadas a la cuenta.

**Qué queda:** los mensajes que la cuenta escribió permanecen en sus hilos, con `seudonimo` reemplazado por un seudónimo neutro estable generado por el sistema; `estado` de la cuenta pasa a `anonimizada`. Los hilos no se agujerean (`P-05`).

**204.**

### `GET /api/v1/config`

Público. Devuelve `tope_caracteres`, `ventana_edicion_segundos`, `longitud_prefijo`, `longitud_sufijo`, `ttl_borrador_segundos`. Existe para que los cuatro valores pendientes de `06_MODELO_DOMINIO §8` vivan en un lugar y no en el cliente.

---

## 5. Lo que este contrato deliberadamente no tiene

Con nombre y apellido, misma disciplina que `04_MVP`:

- `GET /buscar` — no hay búsqueda, asistida ni no.
- `GET /cuentas/{id}` — no hay perfiles públicos. Y si algún día hay, no devuelve totales (`I-CU-2`).
- `GET /feed`, `GET /novedades`, `GET /destacado` — el destacado es un enlace HTML editado a mano.
- `POST /anclas/{id}/migrar`, cualquier endpoint de versiones — el migrador no está en la v1 (`04_MVP`), y publicar una versión es una operación de ingesta manual, no de API.
- `POST /obras` — la ingesta es manual y fuera del producto (`05_JOURNEYS §0`). Si aparece un endpoint de carga, el MVP creció.
- Cualquier endpoint de moderación — se modera con acceso a la base.
- `POST /auth/login`, recuperación de contraseña — no hay contraseñas.
- Endpoint de anotación W3C. Está en la hoja de ruta, no en la v1.
- Anidamiento de mensajes, reacciones, votos, "mejor respuesta" (`P-03` MUST NOT).

---

## 6. Auth y permisos, en una tabla

| Endpoint | Sin cuenta | Con cuenta | Operador |
|---|---|---|---|
| Todos los `GET` de §1 | sí | sí | sí |
| `POST /borradores` | sí | sí | sí |
| `POST /auth/*` | sí | sí | sí |
| `POST /anclas` | no | sí | sí |
| `POST /hilos/{id}/mensajes` | no | sí | sí |
| `PATCH`/`DELETE` de mensaje propio | no | sí (ventana) | sí |
| Retirar hilo ajeno | no | no | sí, fuera de la API |

El operador **no tiene endpoints propios** (`05_JOURNEYS §0`: recorre J-02 y J-03 sin pantallas propias). Lo que hace de más lo hace contra la base.

---

## 7. Errores: catálogo cerrado

`seleccion_vacia`, `seleccion_cruza_bloques`, `seleccion_demasiado_larga`, `seleccion_invalida`, `mensaje_vacio`, `mensaje_demasiado_largo`, `correo_invalido`, `seudonimo_ocupado`, `enlace_invalido`, `borrador_vencido`, `borrador_ya_consumido`, `sesion_requerida`, `no_es_autor`, `ventana_de_edicion_cerrada`, `hilo_cerrado`, `hilo_retirado`, `hilo_no_encontrado`, `ancla_no_encontrada`, `obra_no_encontrada`, `obra_retirada`, `limite_de_tasa`.

Cada uno se nombra desde un test de la Fase 8. Un código sin test es un código que nadie sabe si se emite.

---

## 8. Correo: no es un endpoint pero es parte del contrato

`I-SU-4` lo llama infraestructura crítica y `05_JOURNEYS J-02` dice que si los correos caen en spam no hay sitio. Tres tipos, y sólo tres:

| Tipo | Disparador | Contenido |
|---|---|---|
| Enlace mágico | `POST /auth/enlace` | Token de 30 min, enlace único |
| Respuesta a hilo | `mensaje.publicado` | Cita + fragmento de la respuesta + enlace al pasaje + baja de un clic |
| Enlace de reingreso | `POST /auth/enlace` sin borrador | Igual al primero |

No hay digest, no hay "novedades", no hay nada más (`I-SU-3`, `05_JOURNEYS §5`).

**Prueba del primer día, no del día del lanzamiento:** los tres tipos llegan a bandeja de entrada en Gmail y Outlook, con SPF, DKIM y DMARC configurados. Si eso no se cumple, no se sigue construyendo: J-03 entero cuelga de ahí.

---

## 9. Tres cosas que aparecieron al escribir este archivo

Son la justificación de haberlo escrito, y ninguna es un detalle de implementación.

### 9.1 Los selectores los resuelve el servidor, no el cliente

Si el cliente manda `texto_citado`, `prefijo` y `sufijo` junto con la posición, los tres selectores pueden ser **inconsistentes entre sí** desde el momento de creación: basta una versión vieja en caché, una normalización distinta en el navegador o un cliente malicioso. Y un ancla cuyos selectores no coinciden con el texto canónico es exactamente el fallo que `03_SPIKE §4.4` llama "mentir": no falla al crearse, falla silenciosamente el día de la primera migración, meses después.

**Regla:** el cliente manda posición sobre un `version_id` explícito; el servidor deriva cita y contexto del texto que él mismo hasheó, o rechaza. `I-AN-2` dice que los tres son obligatorios; este archivo agrega **quién los produce**, que es lo que hace que la obligación signifique algo.

Consecuencia menor y buena: la longitud de prefijo y sufijo (pendiente de `R-03`) se cambia en el servidor sin tocar clientes.

### 9.2 La URL canónica del pasaje es de HTML, no de la API

`P-02` exige que el hilo sea legible sin cuenta e **indexable**, y `04_MVP` hace de la página del pasaje la unidad del sitio. Una SPA que rellena `/pasaje/<id>` con `GET /api/v1/anclas/{id}` en el cliente no es indexable de forma confiable, y la única diferencia real que `04_MVP §5` le reconoce al MVP frente a Hypothes.is es justamente la apuesta de SEO.

**Decisión que este contrato fuerza:** `/pasaje/<id>` y `/obra/<slug>` se sirven **renderizadas en el servidor**, con el hilo completo en el HTML. La API de §1 existe para el visor y para el cliente, no para pintar la página del pasaje. Es una restricción de arquitectura que la Fase 7 hereda, y sale gratis decidirla hoy.

### 9.3 La transacción de `I-BO-3` no cabe en un request, y eso tiene un modo de falla

`06_MODELO_DOMINIO §12.2` marca el cierre transaccional del borrador como la operación más compleja de la v1 y la que más se rompe bajo error parcial. Escribir los endpoints muestra dónde exactamente: entre `POST /auth/enlace` (correo entregado) y `POST /auth/sesion` (transacción) hay un viaje por correo, y el borrador tiene TTL propio. El caso "el correo tardó 40 minutos" produce un enlace válido con un borrador muerto.

Por eso `POST /auth/sesion` con `borrador_vencido` **crea la cuenta igual y devuelve el texto**. Es una decisión de producto, no de plomería: la alternativa —fallar entero— pierde la cuenta *y* la prosa por un timeout de infraestructura.

**Segunda consecuencia:** el TTL del borrador tiene que ser **holgadamente mayor** que el del enlace mágico (30 min). Propuesta: 24 horas. Que sean iguales garantiza el fallo.

---

## 10. Qué cambia este archivo

| Resultado | Efecto |
|---|---|
| `R-01` o `R-02` fallan | Este archivo se tira entero junto con `04_MVP` y `05_JOURNEYS`. |
| `R-03`: falsos positivos irrecuperables | `POST /borradores` y `POST /anclas` dejan de aceptar `offset_*` (`04_MVP §6`); el resto del contrato no se mueve. |
| Se fija `tope_caracteres`, `longitud_prefijo`/`sufijo` | Valores en `GET /config`, sin cambio de contrato. |
| Se decide `I-CU-3` | Se especifica `DELETE /api/v1/cuenta`. |

---

## 11. Registro

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial | Fase 6, escrita antes de la Fase 2 igual que 04, 05 y 06 |
| 2026-09-09 | §1: URL canónica del pasaje es `/pasaje/<slug>`; `GET /api/v1/anclas/{slug}` acepta sólo el slug | Corrección de `09_SLICE_1 §8` |
| 2026-09-09 | §4: efecto de `DELETE /api/v1/cuenta` especificado (I-CU-3 decidida: anonimiza, no retira) | D de baja |
