# Sistema de Diseño y Prueba de Autómatas

Aplicación de escritorio (Tkinter, solo librería estándar) para crear, editar,
visualizar y probar AFD, AFN y AFN-λ, según el SDD del proyecto.

## Ejecutar en desarrollo

```powershell
py -3 main.py
```

## Pruebas

```powershell
py -3 -m unittest discover -s tests
```

## Empaquetar como .exe independiente

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

Genera `dist\AutomataDesigner.exe`, sin necesitar Python instalado en la
máquina destino. No se usa Graphviz ni matplotlib: el grafo de estados y la
cinta se dibujan con `tkinter.Canvas`, así que no hay binarios externos que
distribuir aparte del propio `.exe`.

## Uso rápido

1. **Agregar estado**: seleccione el modo "Agregar estado" y haga clic en el lienzo.
2. **Agregar transición**: modo "Agregar transición", clic en el estado origen y luego en el destino; indique el/los símbolo(s) (use `λ` o `lambda` para transiciones nulas).
3. Clic derecho sobre un estado: renombrar, marcar como inicial, marcar como final, eliminar.
4. La **tabla de transiciones** (pestaña derecha) es editable y se sincroniza con el diagrama.
5. **Autómata > Validar consistencia** (CU7): revisa unicidad de q0, F ⊆ Q, alcanzabilidad y totalidad de δ en AFD.
6. **Autómata > Convertir AFND a AFD** (CU5): aplica construcción de subconjuntos y reemplaza el diagrama por el AFD equivalente.
7. Panel inferior: escriba una cadena `u` y use "Paso a paso" o "Reproducir" para animar "el cuadro" (la cinta), con el estado activo resaltado y el veredicto final (ACEPTADA/RECHAZADA).
8. **Autómata > Registrar lenguaje** (CU8): asocia nombre y descripción/regex al autómata (requiere que sea consistente).
9. **Archivo > Guardar/Abrir**: persiste en formato propio `.autm` (JSON).
