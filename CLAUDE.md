# CLAUDE.md

*artHUB — índice raíz. No es una spec: apunta a las specs.*

## 1. Índice (00 a 10)

| Archivo | Decide | NO decide |
|---|---|---|
| `00_CONSTRAINTS.md` | Tiempo del operador, dinero, fechas de cierre/reevaluación, restricciones legales, qué pasa si el proyecto se abandona | Producto, arquitectura |
| `01_PRODUCT_PRINCIPLES.md` | Los nueve principios MUST/MUST NOT, autoridad máxima ante conflicto | Esquema, contratos, implementación |
| `02_RISKS.md` | Qué riesgo se prueba primero y con qué criterio de fracaso | Producto ni solución técnica |
| `03_SPIKE_anclas.md` | Pregunta, arnés y resultado del experimento de reanclaje (R-03, corrido) | Producto ni solución técnica más allá del propio umbral |
| `04_MVP.md` | Qué entra y qué no entra en la v1 | Journeys, modelo de datos, contratos |
| `05_JOURNEYS.md` | Recorridos críticos J-01/J-02/J-03 paso a paso | Esquema, endpoints |
| `06_MODELO_DOMINIO.md` | Entidades, invariantes, campos del esquema | Contratos HTTP, reglas ejecutables |
| `07_API.md` | Contratos HTTP: endpoints, request/response, errores | Modelo de datos, reglas de negocio |
| `08_RULES.md` | Reglas de negocio ejecutables (`R-xxx`), ID estable | Producto nuevo: sólo instrumenta invariantes/principios ya escritos |
| `09_SLICE_1.md` | Corte del primer entregable + correcciones a specs anteriores | El slice 2 (cuentas, correo, escritura) |
| `10_TAREAS.md` | Cómo se escribe y se tipa una tarea | Producto, specs |

## 2. Orden de prioridad ante conflicto

`01_PRODUCT_PRINCIPLES` → `00_CONSTRAINTS` → `06_MODELO_DOMINIO` → `08_RULES` → `07_API` → código.

Una regla que contradiga un principio es una regla mal escrita, no una excepción.

## 3. Reglas para el agente (`10_TAREAS §7`)

1. No inventar comportamiento de producto: si falta, preguntar.
2. Ante specs en conflicto, seguir el orden de prioridad declarado.
3. No refactorizar fuera del alcance del slice ni de la lista `ARCHIVOS`.
4. Cada cambio de comportamiento actualiza la spec correspondiente, en el mismo commit.
5. Una tarea sin tipo no se empieza. Si no se puede tipar con las dos preguntas de `10_TAREAS §1`, está mal cortada.

## 4. Valores pendientes — no se inventan

| Valor | Dónde vive el pendiente |
|---|---|
| Longitud de prefijo/sufijo | `08_RULES` R-001 |
| `tope_caracteres` | `08_RULES` R-005 |
| Techo USD/mes | `00_CONSTRAINTS §2` |
| Umbral y plazo de la puerta social | `00_CONSTRAINTS §3` |

## 5. Este archivo no decide producto

Si algo tienta a agregar acá — un endpoint, un campo, una regla — va en la spec que le corresponde, no acá.
