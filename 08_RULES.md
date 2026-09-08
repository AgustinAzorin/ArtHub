# 08_RULES.md

*artHUB — Fase 6. Versión 0.1, septiembre 2026.*

> Reglas de negocio en formato ejecutable. Cada una tiene ID estable, se referencia
> desde tests (Fase 8) y desde commits. Una regla sin test en la Fase 8 es una regla
> que nadie sabe si corre.
>
> **Qué es una regla acá y qué no.** Un invariante de `06_MODELO_DOMINIO` describe
> un estado que siempre tiene que ser verdad. Una regla describe **qué hace el
> sistema cuando pasa algo**. Muchas reglas existen para sostener un invariante;
> ninguna lo reemplaza. Donde una regla deriva de un invariante o de un principio,
> está citado: si la fuente cambia, la regla se revisa.
>
> **Orden de prioridad ante conflicto** (para el `CLAUDE.md` de la Fase 10):
> `01_PRODUCT_PRINCIPLES` → `00_CONSTRAINTS` → `06_MODELO_DOMINIO` → este archivo →
> `07_API` → código. Una regla que contradiga un principio es una regla mal escrita,
> no una excepción.

---

## 1. Creación de anclas y hilos

**R-001 — Selectores derivados en el servidor** (`I-AN-2`, `07_API §9.1`)
```
IF   llega una selección con (version_id, bloque_inicio, offset_inicio, bloque_fin, offset_fin)
THEN el servidor deriva texto_citado, prefijo y sufijo del texto canónico de esa versión
     y los persiste junto con la posición
ELSE si el cliente envía cita o contexto, se ignoran; no se confía nunca en ellos
```

**R-002 — Ancla incompleta no se guarda** (`I-AN-2`)
```
IF   falta cualquiera de los tres selectores después de derivar
THEN la escritura falla; no se crea nada
```

**R-003 — Rango vacío o invertido** (`I-AN-4`)
```
IF   bloque_inicio.orden > bloque_fin.orden
     OR (bloques iguales AND offset_inicio >= offset_fin)
THEN 422 seleccion_vacia
```

**R-004 — Cruce de bloques: prohibido en interfaz, permitido en esquema** (`I-AN-3`, `05_JOURNEYS §4`)
```
IF   bloque_inicio_id != bloque_fin_id
THEN 422 seleccion_cruza_bloques
ELSE se acepta
```
La validación corre **en el servidor**, no sólo en el cliente: una restricción de interfaz que el API no sostiene no es una restricción. El día que se levante, se levanta acá y en el cliente, y el esquema no se toca.

**R-005 — Tope de selección** (`I-AN-5`)
```
IF   (offset_fin - offset_inicio) > tope_caracteres
THEN 422 seleccion_demasiado_larga
```
`tope_caracteres` es `[PENDIENTE]` (`06_MODELO_DOMINIO §8`): se fija mirando los párrafos reales de las tres obras elegidas. La regla existe con el valor abierto; el test de la Fase 8 la ejercita contra el valor de configuración, no contra un literal.

**R-006 — Un hilo nace con su mensaje** (`I-HI-4`, `I-HI-2`)
```
IF   se crea un Ancla desde la interfaz
THEN se crean Ancla + Hilo + Mensaje en la misma transacción
ELSE ninguna de las tres existe
```

**R-007 — No hay hilo sin ancla** (`P-01` MUST NOT)
```
IF   una escritura intenta crear un Hilo sin ancla_id
THEN se rechaza a nivel de esquema, no de aplicación
```

**R-008 — Un ancla, un hilo** (`I-HI-1`)
```
IF   ya existe un Hilo para ese ancla_id
THEN no se crea otro
```
Dos selecciones **parecidas** son dos anclas distintas y por lo tanto dos hilos gemelos. Es tolerado a propósito en la v1 (`04_MVP`) y hay que mirarlo: es la primera evidencia de que la agrupación de solapadas dejó de ser opcional.

**R-009 — Idempotencia de escritura** (`07_API §2`)
```
IF   llega un POST de creación con un Idempotency-Key ya visto en las últimas 24h
THEN se devuelve la respuesta original, sin crear nada nuevo
```

**R-047 — El slug de un ancla no se reusa** (`09_SLICE_1 D-06`, mismo motivo que R-028)
```
IF   se asigna un slug a un ancla
THEN es opaco, se asigna una vez y no se reusa jamás
ELSE ni siquiera si el ancla queda retirada
```

---

## 2. Cuenta sin contraseña y borrador

**R-010 — Escribir primero, registrarse después** (`P-02`, `05_JOURNEYS J-02`)
```
IF   un visitante sin cuenta envía un comentario
THEN se persiste el Borrador del lado del servidor con los tres selectores ya resueltos
     y RECIÉN ENTONCES se le pide correo y seudónimo
```
Invertir el orden es perder exactamente al visitante que `P-02` protege. Esta regla no es una comodidad de interfaz: es producto.

**R-011 — El endpoint de enlace no revela quién tiene cuenta** (`00_CONSTRAINTS §4`)
```
IF   se pide un enlace mágico para un correo
THEN 202, exista o no la cuenta, esté activa o suspendida
ELSE la única excepción es seudonimo_ocupado, que se responde ANTES de enviar el correo
```

**R-012 — Enlace mágico de un solo uso** (`I-EM-1`, `I-EM-2`)
```
IF   se consume un token
THEN se invalida inmediatamente y se guarda sólo su hash
ELSE token desconocido, usado o vencido → 401 enlace_invalido, sin distinguir cuál
```

**R-013 — Cierre transaccional del borrador** (`I-BO-3`)
```
IF   el enlace lleva un borrador vigente
THEN Cuenta + Ancla + Hilo + Mensaje + Suscripcion se crean en UNA transacción
ELSE no se crea ninguna de las cinco
```
Es la operación más compleja de la v1 y la que más se rompe bajo error parcial (`06_MODELO_DOMINIO §12.2`). Primeros tests de la Fase 8.

**R-014 — Borrador vencido no cuesta la cuenta** (`07_API §9.3`)
```
IF   el token es válido pero el borrador venció
THEN se crea la cuenta, se inicia sesión y se devuelve el texto del borrador
ELSE nunca se falla la sesión entera por un TTL
```

**R-015 — TTL del borrador mayor que el del enlace**
```
TTL(borrador) >= 8 × TTL(enlace_magico)
```
Propuesta: enlace 30 minutos, borrador 24 horas. Que sean iguales garantiza el fallo de R-014 en el caso normal de "el correo tardó".

**R-016 — Reintento del mismo enlace** (`07_API §2`)
```
IF   se consume un enlace ya usado cuyo borrador se convirtió en un hilo
THEN se devuelve el ancla_id existente en vez de un error
```
El caso real es tocar el enlace dos veces desde el correo, no un ataque.

**R-017 — Sin contraseñas** (`05_JOURNEYS §4`, `I-CU-1`)
```
IF   aparece cualquier necesidad de autenticación
THEN se resuelve con enlace mágico y cookie de sesión larga
ELSE no existe campo de contraseña, ni hashing, ni recuperación, ni pantalla de login
```

**R-018 — Datos mínimos** (`00_CONSTRAINTS §4`, Ley 25.326)
```
Se recolecta correo y seudónimo. Nada más. No hay campo de nombre real.
```

**R-049 — Baja de cuenta: anonimizar, no retirar** (`I-CU-3`, `P-05`)
```
IF   una cuenta se da de baja
THEN los mensajes que escribió permanecen en sus hilos, con autoría reemplazada
     por un seudónimo neutro estable
ELSE nunca se retiran: agujerear un hilo ajeno por la baja de un tercero viola P-05
```
Decidido. Qué otro dato se borra (correo, sesiones, preferencias) está en `07_API §4`.

Los mensajes anonimizados **no** quedan congelados contra edición retroactiva: la
anonimización de autoría no agrega ninguna regla de bloqueo nueva sobre el
contenido del mensaje, más allá de la que ya exista por otro motivo (`R-045`,
ventana de edición). Decisión del operador.

---

## 3. Lectura, orden y ausencia de puntaje

**R-019 — Ningún GET público exige cuenta** (`P-02` MUST)
```
IF   un endpoint de lectura de obra, texto, índice de hilos o pasaje devuelve 401
THEN es un bug de prioridad máxima, no una decisión de configuración
```

**R-020 — El orden lo da el texto** (`P-03`, `I-BL-3`)
```
IF   se lista un conjunto de hilos o anclas
THEN el orden es (Bloque.orden, offset_inicio)
ELSE nunca por respuestas_count, recencia, ni actividad
```

**R-021 — El único número permitido** (`I-HI-3`, excepción explícita de `P-03`)
```
IF   se expone un contador
THEN sólo puede ser densidad agregada por pasaje (respuestas por hilo, hilos por bloque)
ELSE ningún total por Cuenta, ningún porcentaje de lectura, ningún ranking
```
Agregar un contador por persona es un cambio de principio con fecha en el registro de `01_PRODUCT_PRINCIPLES`, no un campo nuevo.

**R-022 — Las huérfanas no se filtran** (`I-AN-7`)
```
IF   una consulta renderiza anclas
THEN incluye las de estado huerfana y las muestra con su cita original y el aviso
ELSE ninguna consulta las excluye por defecto
```

**R-023 — Retirada no es borrada** (`P-05`, `I-ME-5`, `05_JOURNEYS J-03`)
```
IF   se retira un Mensaje, un Hilo o una Obra
THEN la fila se conserva y el lugar muestra un aviso
ELSE nada desaparece en silencio: obra retirada → 410 con motivo, no 404
```

**R-024 — Retirar el primer mensaje retira el hilo, no el ancla** (`I-ME-2`)
```
IF   se retira el mensaje de orden 1
THEN el Hilo pasa a retirado
AND  el Ancla queda viva
```

---

## 4. Texto canónico y versiones

**R-025 — Inmutabilidad de la versión publicada** (`I-VT-1`)
```
IF   una VersionTexto está publicada
THEN ninguna operación —ingesta, moderación, operador— edita su contenido
ELSE corregir es publicar una versión nueva
```

**R-026 — El visor renderiza desde el texto canónico** (`§6` del concepto)
```
IF   se muestra texto de una obra
THEN sale de los Bloques normalizados que la ingesta hasheó, carácter a carácter
ELSE nunca del archivo de origen ni de una transformación del cliente
```
Si la interfaz altera el texto para mostrarlo, los offsets mienten.

**R-027 — Normalización versionada** (`I-VT-4`)
```
IF   cambian las reglas de normalización
THEN es un evento de esquema con normalizacion_id nuevo, no un deploy
ELSE dos versiones normalizadas con reglas distintas rompen el reanclaje sin avisar
```

**R-028 — Identificador estructural estable** (`I-IB-1`, `I-IB-2`, `03_SPIKE §4.2`)
```
IF   se asigna un identificador de bloque
THEN es opaco, se asigna una vez y no se reusa jamás
ELSE la única excepción son los ids de la estructura propia de la obra
     (acto/escena/verso, versículo), estables por definición
```
Nunca derivado de la posición: insertar un párrafo correría todos los ids de ahí para abajo y rompería el nivel "estable" del ancla, con un daño peor que el que el mecanismo venía a evitar.

**R-029 — Reanclaje acotado por bloque** (`I-BL-2`)
```
IF   se publica una versión nueva
THEN se comparan hashes por bloque
AND  sólo se procesan las anclas de los bloques cuyo hash cambió
```

**R-030 — Ante duda, huérfana** (`03_SPIKE §5`, `I-MI-3`)
```
IF   confianza_migracion < umbral_confianza  OR  hay empate entre dos candidatos
THEN el ancla queda huerfana visible
ELSE nunca se migra "por las dudas"
```
`umbral_confianza = 0.80`. Fijado por el barrido `--umbral` × `--semilla` de
`03_SPIKE §2`/§6 sobre una obra real (*El almohadón de pluma*, Quiroga): 0.75
y 0.8 empatan en el punto más bajo de falsos positivos medido (3.17% de
media) con la misma tasa de huérfanas evitables (0.17%); gana 0.8 por dar más
margen sin costo adicional en ese empate. **Condición de `03_SPIKE §3`:**
este número corrió sólo contra una obra cuyas ediciones reales fueron
mayoritariamente ortográficas; falta correrlo contra una obra con revisiones
que reescriban prosa antes de darlo por cerrado en producción.

**R-031 — Toda migración deja registro** (`I-AN-8`, `I-MI-1`)
```
IF   se crea un ancla con derivada_de
THEN confianza_migracion y metodo_migracion son obligatorios
ELSE la escritura se rechaza
AND  se escribe una fila de MigracionAncla por cada ancla, incluidas huérfanas e intactas
```

**R-032 — Publicación bloqueada por migración incompleta** (`I-VT-5`)
```
IF   se publica una versión con numero > 1 y quedan anclas sin resolver
THEN la publicación no se completa
ELSE no existe "publicada a medias"
```

**Nota de alcance:** R-029 a R-032 gobiernan un código que **no se construye en la v1** (`04_MVP`: el migrador queda afuera, el esquema entra). Se escriben igual porque son las reglas que hacen que el esquema tenga sentido, y porque el día que se corran no va a haber tiempo de pensarlas.

---

## 5. Catálogo y legalidad

**R-033 — Sin verificación no hay publicación** (`I-OB-1`, `00_CONSTRAINTS §4`)
```
IF   una Obra no tiene verificacion_dominio_publico completa
     (fuente, quién, cuándo, razonamiento, plazo aplicado)
THEN no se publica
ELSE no existe estado intermedio "publicada pero sin verificar"
```

**R-034 — Atribución perpetua** (derecho moral, `P-04`)
```
IF   se muestra cualquier fragmento de una obra en cualquier superficie
     (visor, página de pasaje, tarjeta, export)
THEN aparece autor_nombre
```

**R-035 — Procedencia obligatoria de la edición** (`I-ED-3`)
```
IF   una Edicion no tiene fuente_url y licencia_origen
THEN no es publicable
```

**R-036 — Nada de disponibilidad revocable** (`P-04` MUST NOT)
```
IF   una obra o un formato depende de un contrato con un tercero que puede retirarlo
THEN no entra, aunque sea técnicamente fácil
```

**R-037 — Una edición default por obra e idioma** (`I-ED-2`)
```
IF   se marca una Edicion como default
THEN la anterior deja de serlo, en la misma transacción
AND  se emite edicion.default_cambiado
```
Mueve el tráfico entre silos de traducción: es decisión de producto, no de catálogo.

---

## 6. Licencias y datos

**R-048 — Licencia de las anotaciones** (`00_CONSTRAINTS §4`)
```
IF   una persona publica un comentario o un mensaje en un hilo
THEN conserva su copyright sobre ese texto y otorga una licencia CC BY-SA 4.0
     irrevocable al publicarlo
ELSE cualquier exportación del grafo (00_CONSTRAINTS §5) sale bajo la misma
     licencia, con atribución por autor
```
Decidido: candidata cerrada. Cláusula completa en `TERMINOS.md`.

---

## 7. Notificaciones: el único mecanismo de retorno

**R-038 — Una respuesta, un correo** (`I-SU-3`, `05_JOURNEYS §5`)
```
IF   se publica un Mensaje en un hilo
THEN se envía un correo a cada suscriptor distinto del autor
ELSE no hay digest, no hay agrupación, no hay notificaciones en pantalla
```

**R-039 — Suscripción automática** (`I-SU-1`)
```
IF   alguien abre un hilo o responde en él
THEN queda suscripto a ese hilo
```

**R-040 — Baja de un clic, sin login** (`I-SU-2`)
```
IF   se toca el enlace de baja de un correo
THEN se da de baja de ESE hilo, sin pedir sesión
ELSE nunca una baja global implícita
```

**R-041 — El correo se verifica el primer día** (`I-SU-4`)
```
IF   los tres tipos de correo no llegan a bandeja de entrada en Gmail y Outlook
     con SPF, DKIM y DMARC configurados
THEN no se sigue construyendo hasta que lleguen
```
J-03 entero cuelga de ahí, y J-03 es el criterio de "V1 listo".

**R-042 — Latencia de respuesta como métrica** (`05_JOURNEYS J-03`)
```
Se registra el tiempo entre mensaje.publicado y la respuesta del autor del hilo.
Objetivo observado, no impuesto: mediana < 48 horas.
```
Es el mejor indicador temprano de si el ágora está viva, mucho antes de que haya cinco hilos por semana.

---

## 8. Moderación: conducta, no sentido

**R-043 — Qué se borra** (`P-07`)
```
IF   el contenido es ataque personal o spam
THEN se retira (R-023: queda el hueco)
ELSE una lectura equivocada, disparatada o minoritaria NO se toca
```

**R-044 — No hay nota canónica**
```
IF   dos lecturas del mismo pasaje se contradicen
THEN conviven sin jerarquía; ninguna se marca como correcta
```

**R-045 — Ventana de edición** (`I-ME-4`)
```
IF   pasó la ventana desde creado_en
THEN el mensaje es inmutable, incluso para su autor
```
Un hilo cuya primera intervención cambia de sentido tres días después rompe las respuestas que le contestaron.

---

## 9. Máquina

**R-046 — Buscar sí, interpretar no** (`P-06`)
```
IF   se propone una función con IA
THEN sólo puede buscar, encontrar, alinear traducciones como sugerencia o detectar duplicados
ELSE resumir hilos, generar notas críticas o producir interpretaciones no existe como función
```
En la v1 no hay ninguna función de IA. La regla se escribe ahora porque el momento de escribirla es antes de que alguien la proponga con buenas intenciones.

---

## 10. Reglas que este archivo NO puede escribir todavía

Mismo criterio que `06_MODELO_DOMINIO §8`: se nombran, no se inventan.

| Regla faltante | La desbloquea |
|---|---|
| Valor de `tope_caracteres` en R-005 | Los párrafos reales de las tres obras |
| Longitud de prefijo/sufijo (R-001) | El mismo spike: es la palanca contra la ambigüedad literal |

`umbral_confianza` de R-030 ya no está pendiente: `0.80`, fijado por el
barrido real de `03_SPIKE §2`/§6 (con la condición anotada en R-030 sobre
volver a correrlo contra una obra con reescritura de prosa). Las dos
restantes son técnicas: la longitud de prefijo/sufijo la destraba el mismo
spike variando `--contexto`, todavía no corrido; `tope_caracteres` no es
parte de R-03.

---

## 11. Índice inverso para la Fase 8

Cada test nombra su regla. Cobertura mínima exigida:

| Grupo | Reglas | Test obligatorio |
|---|---|---|
| Creación de ancla | R-001 a R-005 | Un caso que viole cada validación y falle |
| Transacción de borrador | R-006, R-013, R-014, R-016 | Error parcial: correo entregado + transacción fallida |
| Sin puntaje | R-020, R-021 | Ningún endpoint devuelve un total por cuenta |
| Nada en silencio | R-022, R-023, R-024 | Retirar el primer mensaje deja el ancla viva y visible |
| Texto canónico | R-025, R-026, R-028 | Insertar un párrafo no cambia ningún identificador existente |
| Correo | R-038, R-040 | Un mensaje, un correo por suscriptor, cero al autor |

Los casos borde del mecanismo central (reanclaje) se escriben **antes** de implementarlo, y hoy no se pueden escribir bien porque falta el número de R-030.

---

## 12. Registro

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial | Fase 6, escrita antes de la Fase 2 |
| 2026-09-09 | + R-047 (slug de ancla no se reusa) en §1 | Corrección de `09_SLICE_1 §8` |
| 2026-09-09 | + R-048 (licencia de las anotaciones) en §5; sacada de la tabla de pendientes de §9 | D de licencia |
| 2026-09-09 | + R-049 (baja de cuenta: anonimizar) en §2; sacada de la tabla de pendientes de §9 | D de baja |
| 2026-09-08 | R-049: aclarado que los mensajes anonimizados NO se congelan contra edición retroactiva; no se agrega regla de bloqueo | Decisión del operador |
| 2026-09-08 | R-048 movida de §5 (Catálogo y legalidad) a §6, nueva (Licencias y datos); §§6–11 anteriores renumeradas a §§7–12 | La licencia de las anotaciones no es catálogo de obras: es dato de usuario |
| 2026-09-08 | R-030: `umbral_confianza` fijado en `0.80`; sacado de la tabla de pendientes de §10 | Barrido real de `03_SPIKE_anclas.md §2`/§6 sobre *El almohadón de pluma* |
