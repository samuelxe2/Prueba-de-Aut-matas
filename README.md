# Sistema de Diseño y Prueba de Autómatas

Aplicación de escritorio para Windows (Python + Tkinter, sin dependencias
externas más allá de la librería estándar) que permite **crear, editar,
visualizar y probar** Autómatas Finitos Deterministas (AFD), Autómatas
Finitos No Deterministas (AFN) y Autómatas con transiciones λ (AFN-λ).

## Contenido

- [¿Qué hace la aplicación?](#qué-hace-la-aplicación)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Guía de uso](#guía-de-uso)
- [Formato de archivo `.autm`](#formato-de-archivo-autm)
- [Pruebas](#pruebas)
- [Empaquetado a `.exe`](#empaquetado-a-exe)
- [Estructura del proyecto](#estructura-del-proyecto)

## ¿Qué hace la aplicación?

| Función | Descripción |
|---|---|
| **Editor de diagramas** | Lienzo interactivo: agregar/mover/renombrar estados con el mouse, marcar estado inicial y estados finales, crear transiciones (incluye auto-lazos y transiciones λ). |
| **Tabla de transiciones** | Vista tipo hoja de cálculo de δ/Δ, editable, sincronizada en ambos sentidos con el diagrama. |
| **Validación de consistencia** | Revisa: existencia y pertenencia de q0, F ⊆ Q, símbolos usados dentro de Σ, alcanzabilidad de estados desde q0, y totalidad de δ cuando el modelo es un AFD. |
| **Conversión AFND → AFD** | Construcción de subconjuntos con cierre-λ; el estado vacío resultante se representa como **∅** con auto-lazo en todos los símbolos, para que el AFD quede con función de transición total. |
| **Simulador de cadena ("el cuadro")** | Anima la cinta de entrada símbolo por símbolo, resaltando el/los estado(s) activo(s) bajo la cabeza lectora, con veredicto final ACEPTADA/RECHAZADA. |
| **Registro de lenguaje** | Asocia un nombre y una descripción/expresión regular al lenguaje reconocido por el autómata (solo si es consistente). |
| **Persistencia** | Guardar/abrir autómatas en un formato propio `.autm` (JSON legible). |

El tipo del autómata (AFD / AFN / AFN-λ) se deduce automáticamente de sus
transiciones: si existe algún símbolo λ es AFN-λ; si algún par (estado,
símbolo) tiene más de un destino es AFN; en otro caso es AFD.

## Arquitectura

El proyecto sigue el patrón **Modelo–Vista–Controlador**:

```
ui/            Vista: ventana principal, lienzo, tabla, simulador de cinta,
               dialogos. Solo dibuja y despacha eventos de mouse/menu.
controllers/   Controlador: AppController, AutomatonController,
               ValidationController, ConversionController,
               SimulationController. Contienen las reglas de negocio y
               son el unico punto de contacto entre la Vista y el Modelo.
core/          Modelo: Automaton, ConsistencyValidator, subset_construction,
               TapeSimulator, persistencia en JSON. No conoce nada de Tkinter.
rendering/     Dibujo de bajo nivel sobre tk.Canvas (grafo de estados y cinta),
               usado por la Vista.
```

La Vista nunca importa `core.*` directamente ni muta el autómata por su
cuenta: siempre pasa por un controlador, que a su vez valida y actualiza
el Modelo. Esto permite, por ejemplo, testear las reglas de conversión o
validación sin levantar ninguna ventana.

## Instalación

### Requisitos

- Windows 10/11.
- [Python 3.10+](https://www.python.org/downloads/) instalado (con Tkinter,
  que viene incluido en el instalador oficial de Windows). Verifica con:

```powershell
py -3 --version
```

### Preparar el proyecto

El proyecto no tiene dependencias de terceros para ejecutarse: solo usa la
librería estándar de Python (`tkinter`, `json`, `dataclasses`). No hace
falta `pip install` nada para correrlo en modo desarrollo.

Solo si vas a **generar el ejecutable** necesitas instalar PyInstaller:

```powershell
py -3 -m pip install -r requirements.txt
```

## Ejecución

Desde la carpeta del proyecto:

```powershell
py -3 main.py
```

Esto abre la ventana principal, vacía y lista para dibujar un autómata.

## Guía de uso

1. **Agregar estado**: selecciona el modo "Agregar estado" en la barra
   superior del lienzo y haz clic donde quieras ubicarlo. El primer estado
   creado queda automáticamente como estado inicial.
2. **Agregar transición**: modo "Agregar transición" → clic en el estado
   origen → clic en el destino → escribe el/los símbolo(s), separados por
   coma (usa `λ` o la palabra `lambda` para una transición nula). Para
   representar no-determinismo (un mismo símbolo con varios destinos),
   repite el proceso una vez por cada destino.
3. **Clic derecho sobre un estado**: renombrar, definir/quitar como
   inicial, marcar/desmarcar como final, o eliminarlo.
4. **Tabla de transiciones** (panel derecho): doble clic en una celda para
   editar δ(estado, símbolo); "Agregar símbolo a Σ" añade una columna nueva.
5. **Menú Autómata → Validar consistencia**: corre las reglas de
   validación y muestra errores (bloquean conversión/simulación/registro
   de lenguaje) y avisos (no bloquean, p. ej. estados inalcanzables).
6. **Menú Autómata → Convertir AFND a AFD**: aplica la construcción de
   subconjuntos y reemplaza el diagrama actual por el AFD equivalente
   (los nombres de los nuevos estados son los subconjuntos de estados
   originales, p. ej. `{q0,q1}`; el estado vacío se llama `∅`).
7. **Panel inferior (simulador de cadena)**: escribe una cadena `u` y usa
   "Paso a paso" o "Reproducir" para animar la cinta. El recuadro bajo la
   cabeza lectora muestra el/los estado(s) activo(s) y, al terminar, se
   pone verde (ACEPTADA) o rojo (RECHAZADA).
8. **Menú Autómata → Registrar lenguaje**: asocia un nombre y una
   descripción/expresión regular al autómata actual (requiere que sea
   consistente).
9. **Menú Archivo**: Nuevo, Abrir, Guardar, Guardar como (formato `.autm`).

## Formato de archivo `.autm`

Es JSON plano, legible y editable a mano si es necesario:

```json
{
  "type": "AFN-lambda",
  "alphabet": ["a", "b"],
  "states": ["q0", "q1", "q2"],
  "initial_state": "q0",
  "final_states": ["q0", "q2"],
  "transitions": {
    "q0,a": ["q0"],
    "q0,b": ["q1"],
    "q1,b": ["q2"]
  },
  "positions": { "q0": [100, 100], "q1": [250, 100], "q2": [400, 100] },
  "language": { "name": "Cadenas que terminan en b", "description": "(a|b)*b" }
}
```

## Pruebas

```powershell
py -3 -m unittest discover -s tests -v
```

Incluye pruebas unitarias del núcleo (autómatas, cierre-λ, construcción de
subconjuntos, validador, simulador) y un smoke test que ejercita toda la
aplicación a través de los controladores (crear/editar/validar/convertir/
simular/guardar/cargar) sin necesitar interacción real de mouse/teclado:

```powershell
py -3 -m tests.test_ui_smoke
```

## Empaquetado a `.exe`

Genera un ejecutable independiente que corre en Windows sin tener Python
instalado:

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

El resultado queda en `dist\AutomataDesigner.exe`. No se usan Graphviz ni
matplotlib: tanto el diagrama de estados como la cinta se dibujan con
`tkinter.Canvas`, así que no hay binarios externos que distribuir además
del propio `.exe`.

## Estructura del proyecto

```
main.py                        Punto de entrada
core/
  automaton.py                 Modelo Automaton (AFD/AFN/AFN-λ), LanguageEntry
  validator.py                 ConsistencyValidator, ValidationReport
  subset_construction.py       Algoritmo de construcción de subconjuntos
  simulator.py                 TapeSimulator, TapeFrame
  persistence.py               Guardar/cargar .autm
controllers/
  app_controller.py            Ciclo de vida del autómata activo (nuevo/abrir/guardar)
  automaton_controller.py      Edición del grafo (estados, transiciones, alfabeto, lenguaje)
  validation_controller.py     Ejecuta la validación de consistencia
  conversion_controller.py     Ejecuta la conversión AFND → AFD
  simulation_controller.py     Controla el avance de la simulación de cadena
ui/
  main_window.py               Ventana principal y menús
  canvas_editor.py             Lienzo interactivo del diagrama
  transition_table.py          Tabla de transiciones editable
  tape_simulator_view.py       Panel de simulación de cadena
  language_dialog.py           Registro de lenguaje
  consistency_report.py        Reporte de validación
rendering/
  graph_renderer.py            Dibujo del diagrama de estados sobre Canvas
  tape_renderer.py             Dibujo de la cinta sobre Canvas
tests/
  test_core.py                 Pruebas unitarias del núcleo
  test_ui_smoke.py             Prueba funcional de extremo a extremo
```
