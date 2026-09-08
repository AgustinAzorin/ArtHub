# 05_JOURNEYS.md

*artHUB — Fase 4. Versión 0.1, septiembre 2026.*

> **Estado: hereda la condición de `04_MVP`.** Se escribió antes de que corrieran
> R-01, R-02 y R-03. Si `R-02` sale mal, este archivo se tira entero junto con el
> MVP que describe.
> **Qué agrega igual:** los journeys son gratis de escribir y caros de descubrir
> tarde. Recorrer los tres del camino crítico paso por paso destapó **tres huecos
> del recorte de la Fase 3**, uno de los cuales impide cumplir el criterio de "V1
> listo" tal como está redactado. Están en §3 y §5.

---

## 0. Alcance y actores pospuestos

Sólo el camino crítico del MVP. El resto, una línea cada uno, según pide
`PLANIFICAR_PROYECTO` Fase 4:

- **Autor que publica obra propia** — fuera de v1 (`04_MVP`). Journey propio cuando entre: cuarentena, licencia, cotejo, bajada.
- **Docente y alumnos de un curso** — fuera de v1, y además bloqueado por menores (`00_CONSTRAINTS §4`).
- **Anfitrión (el operador como usuario)** — recorre exactamente J-02 y J-03, sin ninguna pantalla propia. Es deliberado: si el anfitrión necesitara una interfaz distinta a la del resto, el MVP habría crecido sin avisar.
- **Operador ingiriendo una obra** — manual, fuera del producto: archivo normalizado + carga directa + registro de verificación de dominio público (`00_CONSTRAINTS §4`). No es un journey de software y no debe volverse uno en la v1.
- **Moderador** — acceso a la base y una regla escrita (`04_MVP`).

Los tres journeys de abajo tienen 6, 7 y 5 pasos. El techo de la guía es 10.

---

## J-01 — El que llega de afuera

**Actor.** Visitante sin cuenta, que llega desde un buscador, desde un enlace
compartido o desde una invitación del anfitrión. Es el mejor visitante que tiene
el proyecto según `P-02`, y es el que J-01 existe para no perder.

**Precondiciones.** Existe la URL de un pasaje con al menos un hilo con una
respuesta. Al principio no existe ninguna: las primeras las siembra el anfitrión a
mano, y ése es el trabajo que mide `R-01`, no el que mide este journey.

**Camino feliz.**

1. Abre `/pasaje/<id>`. Ve la cita, el contexto atenuado alrededor, la obra y el autor, y el hilo completo.
2. Entiende en qué obra está sin scrollear y sin hacer un clic.
3. Toca "leer la obra". El visor abre **en ese pasaje**, centrado, con el fragmento marcado un instante y un enlace de vuelta al hilo.
4. Lee. La obra es corta (30–40 minutos) porque no hay progreso guardado: si se va, vuelve por URL o vuelve al principio.
5. Encuentra otro pasaje que le interesa.
6. Entra en J-02, o se va.

**El paso donde abandona: el 3.** La transición pasaje → obra es el único
movimiento que la v1 no puede hacer mal. Si el visor abre al principio del texto,
o si al entrar pierde el hilo que estaba leyendo, la persona no vuelve a
encontrarlo y se va. Tiene que ser un enlace bidireccional: del hilo al punto
exacto del texto, y del texto de vuelta al hilo.

**Segundo punto de fuga, menos obvio: el paso 1.** Un fragmento de ocho palabras
con dos comentarios abajo parece un tuit, no una lectura. El prefijo y el sufijo
ya están en el esquema por otro motivo (`P-05`, tres selectores); acá se usan como
producto y se muestran atenuados alrededor de la cita. Cuesta cero y es la
diferencia entre una página de pasaje y una captura de pantalla.

**Errores y permisos.** Todo público, sin cuenta, indexable (`P-02` MUST). Obra
inexistente o versión inexistente → 404 con enlace a la biblioteca. Y un caso que
la v1 no va a producir pero el esquema permite desde el día uno: **ancla sin
posición válida** (huérfana). La página tiene que saber renderizarla —cita
original más aviso de que el pasaje cambió— aunque en la v1 no haya versión 2 de
ningún texto. Es media hora ahora y una excepción no manejada en producción
después.

**Resultado esperado.** El visitante leyó el hilo entero y sabe de qué obra es.
Nada más. Que además lea la obra completa es el caso bueno, no el esperado.

---

## J-02 — El primer subrayado que se vuelve hilo

**Actor.** Lector **sin cuenta**. Es el caso difícil; con cuenta es un subconjunto
de éste.

**Precondiciones.** Está en el visor, leyendo.

**Camino feliz.**

1. Selecciona texto. Aparece **una sola acción**: comentar. No hay menú de tres opciones, porque nota privada y subrayado sin comentario no existen en la v1.
2. Escribe en prosa, en un panel al costado, con la cita arriba a la vista.
3. Envía.
4. **Recién ahí** se le pide correo y seudónimo. El borrador y la selección ya están guardados del lado del servidor.
5. Recibe un enlace por correo. No hay contraseña.
6. Toca el enlace: se crea la cuenta, el comentario se publica y aterriza en la URL pública de su propio pasaje.
7. Copia el enlace, si quiere.

**El paso donde abandona: del 4 al 6, el ida y vuelta por correo.** Es el muro y
no se puede eliminar sin dejar el ágora abierta al spam anónimo, que una persona
sola no puede moderar. Lo que sí se puede es que sea la **última** pregunta y no
la primera, que el borrador sobreviva al viaje, y que no haya contraseña. Escribir
primero y registrarse después no es una comodidad: invertir ese orden es perder
exactamente al visitante que `P-02` protege.

**Decisión que este journey fuerza y que `04_MVP` no había tomado: la v1 no tiene
contraseñas.** Enlace mágico para crear la cuenta y para volver a entrar, sesión
larga por cookie. Elimina hashing, recuperación, pantalla de login y "olvidé mi
contraseña" —un slice entero— y baja el registro a un campo. El precio es la
dependencia del correo transaccional, que ya está presupuestado
(`00_CONSTRAINTS §2`) y que ahora pasa a ser **infraestructura crítica**: si los
correos caen en spam, no hay sitio. Se verifica el primer día contra Gmail y
Outlook, no el día del lanzamiento.

**Errores y permisos.**

- Selección vacía o de un solo carácter: no habilita la acción.
- **Selección a caballo de dos bloques:** la interfaz la recorta al bloque donde empezó y lo dice. Ver §4.
- Selección larguísima (un capítulo entero arrastrado): tope duro de caracteres. Las anclas de obra completa y de capítulo existen en el modelo pero no tienen interfaz en la v1.
- Correo inválido, enlace vencido (30 minutos), enlace usado dos veces: reenviar sin perder el borrador. El borrador tiene TTL y se limpia solo.
- Dos personas subrayan casi el mismo fragmento: en la v1 salen **dos hilos gemelos**, porque la agrupación de selecciones solapadas está fuera (`04_MVP`). Con tres obras y veinte personas es tolerable; hay que mirarlo, porque es la primera evidencia de que esa función dejó de ser opcional.

**Resultado esperado.** Existe un hilo nuevo con URL pública propia, y una persona
con cuenta que sabe volver.

---

## J-03 — La respuesta que cierra el bucle

Es el journey que mide el criterio de "V1 listo". Los otros dos son su
precondición.

**Actores.** Un segundo lector (B) y el autor del hilo (A).

**Camino feliz.**

1. B llega al hilo, por J-01 o desde el índice de hilos de la obra (§3).
2. B responde. Si no tiene cuenta, atraviesa J-02 pasos 4 a 6.
3. **A se entera.**
4. A vuelve y contesta.
5. El hilo llega a tres respuestas y deja de ser un comentario suelto.

**El paso donde abandona: el 3, y no es un problema de interfaz — es que no
existe.** `04_MVP` no incluye notificaciones y tampoco las excluye: se le pasó. Sin
ellas, A se entera de que le respondieron sólo si vuelve por casualidad a una URL
que no está en ninguna parte de su navegación, porque en la v1 no hay perfil, ni
diario de lectura, ni feed, ni búsqueda. Con veinte personas que entran una vez
por semana, el ciclo de respuesta se mide en semanas, o directamente no ocurre. El
criterio de aceptación del MVP **no se puede cumplir sin el operador avisando a
mano**, que es justo lo que ese criterio prohíbe.

**Decisión forzada.** Un correo por respuesta a un hilo que abriste o en el que
comentaste, con enlace directo al pasaje y baja por hilo. Es el único mecanismo de
retorno de toda la v1, y por eso no es opcional. Reusa el canal del enlace mágico:
infraestructura nueva, ninguna. No hay digest, no hay notificaciones en pantalla,
no hay nada más: una respuesta, un correo.

**Errores y permisos.** Cualquiera con cuenta responde cualquier hilo; la lectura
como llave no está en la v1 (`04_MVP`, recorte legítimo sobre `P-02`). Un hilo
borrado por moderación deja el ancla y avisa; no desaparece en silencio, por la
misma razón que `P-05` lo prohíbe para las versiones.

**Resultado esperado, con número.** A responde a B en menos de 48 horas. Esa
latencia es la métrica de este journey y probablemente el mejor indicador temprano
de si el ágora está viva: mucho antes de que haya cinco hilos por semana, ya se ve
si la gente vuelve cuando le hablan.

---

## 3. El hueco grande: la conversación es invisible desde adentro de la obra

Visor de lectura pura sin marcas + sin agregado de densidad en el margen + sin
búsqueda + sin perfil + sin feed = **las URLs de pasaje son islas a las que sólo
se llega desde afuera del sitio**. J-01 funciona porque viene de Google o del
anfitrión. J-02 funciona porque crea un hilo nuevo. Pero nadie encuentra jamás un
hilo que ya existe mientras está leyendo, y el paso 1 de J-03 depende de eso.

Un ágora donde la conversación no se ve desde la obra no es un ágora: es una
colección de páginas sueltas que el operador reparte por privado. El criterio de
"V1 listo" se cumpliría por enlaces pegados a mano.

Lo mínimo que lo arregla, en orden de costo:

- **Índice de hilos por obra.** Una página que lista los pasajes con conversación **en el orden en que aparecen en el texto**, con la cita y el número de respuestas. No es popularidad: el orden lo da el texto, no la actividad, así que no toca `P-03`. Es una consulta y una plantilla. **Va a la v1.**
- **Conmutador de una capa en el visor.** Un botón que enciende las marcas de los pasajes anclados; apagado por defecto. Es el modo estudio del concepto reducido a su mínima expresión, y respeta "lectura pura por defecto" sin romperlo. Recomendado, no obligatorio: entra si el índice resulta insuficiente en las primeras semanas.

No hace falta el agregado de densidad ni la agrupación de solapadas para esto. Con
tres obras y pocos hilos, una marca es una marca.

---

## 4. Decisiones que la Fase 5 hereda de acá

- **Anclas a caballo de dos bloques (`03_SPIKE §4.5`).** Resolución: **el esquema guarda `(bloque_inicio, offset)` y `(bloque_fin, offset)` desde el día uno; la interfaz de la v1 recorta la selección al primer bloque.** El spike decía que prohibir en la interfaz es más barato y probablemente peor; separar las dos capas se queda con lo barato sin pagar lo peor, porque lo irreversible es el esquema y la restricción de interfaz se levanta cuando se quiera. Es el mismo criterio con el que `04_MVP` dejó afuera el migrador y adentro el esquema.
- **Sin contraseñas.** El correo es el único identificador; el seudónimo es lo único que se muestra.
- **Un solo tipo de anotación en la v1 (pública, con hilo)**, pero la tabla nace con el campo que la distingue de nota privada y de subrayado sin texto. Un valor hoy, tres mañana, cero migraciones.
- **Tope de caracteres por selección**, a definir mirando los párrafos reales de las tres obras elegidas, no a ojo.
- **Borrador anónimo con TTL**, que es la pieza que hace posible escribir antes de registrarse.

---

## 5. Qué le exige este archivo a `04_MVP`

| Sección de `04_MVP` | Cambio |
|---|---|
| V1 INCLUYE | **+ Índice de hilos por obra**, ordenado por posición en el texto. |
| V1 INCLUYE | **+ Correo de notificación por respuesta**, con baja por hilo. |
| V1 INCLUYE ítem 5 | Se precisa: cuenta **sin contraseña**, por enlace mágico, pedida **después** de escribir, con borrador persistido. |
| V1 NO INCLUYE | Se agregan con nombre: contraseñas, login, recuperación de cuenta; cualquier notificación que no sea una respuesta directa (nada de digest, nada de "novedades"); selección que cruce bloques en la interfaz. |
| V1 ESTÁ LISTO CUANDO | Se agrega al final: *…y el autor del hilo se entera de la respuesta sin que nadie se lo avise a mano.* Sin esa cláusula, el criterio lo cumple el operador mandando un mensaje por WhatsApp. |

El MVP pasa de cinco ítems a siete, y eso merece desconfianza: es exactamente
cómo un MVP se convierte en un roadmap. La defensa es que **ninguno de los dos es
una función nueva del producto**; son las dos condiciones sin las cuales el
recorrido del criterio de aceptación no se completa sin el operador adentro. Si
hubiera que elegir uno solo, el correo de respuesta pesa más que el índice: sin
índice el ágora es chica, sin correo no hay segunda vuelta.

---

## 6. Lo que este archivo no resuelve

`04_MVP §5` dejó abierta la objeción de Hypothes.is y estos journeys no la
mueven ni un centímetro: J-01, J-02 y J-03 se pueden recorrer hoy sobre
Wikisource con una extensión. Lo único que aparece acá y no está allá es la página
del pasaje como unidad indexable, que es el eje de J-01 y sigue siendo una apuesta
de SEO a meses. El experimento de `R-02` sigue siendo el que decide, y este
archivo no adelanta nada de esa respuesta.

---

## 7. Registro

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-09 | Versión inicial | Fase 4, escrita antes de la Fase 2 igual que `04_MVP` |
