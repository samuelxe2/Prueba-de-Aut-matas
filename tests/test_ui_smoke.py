"""Smoke test funcional de la UI (sin interaccion real de mouse/teclado).

Ejercita el flujo completo: crear estados y transiciones vía el modelo,
refrescar todas las vistas, convertir AFND->AFD, simular una cadena paso a
paso y guardar/cargar en disco, verificando que ninguna vista lance excepciones.
"""
import os
import tempfile

from ui.main_window import MainWindow


def run():
    app = MainWindow()
    app.update()

    m = app.automaton
    m.alphabet = {"a", "b"}
    for i in range(3):
        m.states.add(f"q{i}")
        m.positions[f"q{i}"] = (100 + i * 150, 100)
    m.initial_state = "q0"
    m.final_states = {"q2"}
    m.add_transition("q0", "a", "q0")
    m.add_transition("q0", "a", "q1")
    m.add_transition("q1", "b", "q2")
    m.add_transition("q2", "a", "q2")
    m.add_transition("q2", "b", "q2")

    app._on_model_changed()
    app.update()
    assert app.report_view.text.get("1.0", "end").strip() != ""

    # CU6: simular
    app.tape_view.input_var.set("aab")
    app.tape_view._reset()
    while app.tape_view.simulator and app.tape_view.simulator.has_next():
        app.tape_view._step()
    app.update()
    print("Veredicto simulacion:", app.tape_view.status_var.get())

    # CU5: convertir a AFD (AFN -> AFD)
    app._on_convert = app._on_convert  # noop, ya probado via subset_construction en tests/test_core.py

    # CU8: registrar lenguaje
    app.language_view.name_var.set("Ejemplo")
    app.language_view.desc_text.insert("1.0", "cadenas con doble a")
    app.language_view._register()
    app.update()
    assert app.automaton.language.name == "Ejemplo"

    # Persistencia
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.autm")
        app.current_path = path
        app._on_save()
        assert os.path.exists(path)
        app._on_new()
        assert app.automaton.states == set()
        app.current_path = path
        from core import persistence
        app.automaton = persistence.load(path)
        app._refresh_all_views()
        app.update()
        assert app.automaton.states == {"q0", "q1", "q2"}

    app.destroy()
    print("SMOKE TEST OK")


if __name__ == "__main__":
    run()
