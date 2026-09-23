"""Smoke test funcional de la UI (sin interaccion real de mouse/teclado).

Ejercita el flujo completo a traves de los controladores: crear estados y
transiciones, refrescar todas las vistas, simular una cadena paso a paso,
registrar un lenguaje y guardar/cargar en disco, verificando que ninguna
vista lance excepciones.
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

    # CU6: simular (via SimulationController)
    app.tape_view.input_var.set("aab")
    app.tape_view._reset()
    while app.simulation_controller.has_next():
        app.tape_view._step()
    app.update()
    print("Veredicto simulacion:", app.tape_view.status_var.get())

    # CU5: convertir a AFD (probado a fondo en tests/test_core.py; aqui solo
    # verificamos que el ConversionController + refresco de vistas no truene)
    dfa, report = app.conversion_controller.convert_to_dfa()
    assert report.is_valid
    assert dfa.is_deterministic()
    app._refresh_all_views()
    app.update()

    # CU8: registrar lenguaje (via AutomatonController)
    app.language_view.name_var.set("Ejemplo")
    app.language_view.desc_text.insert("1.0", "cadenas con doble a")
    app.language_view._register()
    app.update()
    assert app.automaton.language.name == "Ejemplo"

    # Persistencia (via AppController)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.autm")
        app.app_controller.save_automaton(path)
        assert os.path.exists(path)

        app._on_new()
        assert app.automaton.states == set()

        app.app_controller.open_automaton(path)
        app._refresh_all_views()
        app.update()
        assert app.automaton.states == dfa.states

    app.destroy()
    print("SMOKE TEST OK")


if __name__ == "__main__":
    run()
