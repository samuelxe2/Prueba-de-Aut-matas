"""AppController: ciclo de vida de la aplicacion y del automata activo (CU1/CU2/CU3).

Es el unico dueno de la instancia de Automaton en memoria. El resto de
controladores reciben una referencia a este AppController en vez de al
automata directamente, para que siempre lean/escriban el modelo vigente
(incluso despues de un Nuevo/Abrir/Convertir, que reemplazan el objeto).
"""
from __future__ import annotations

from core import persistence
from core.automaton import Automaton


class AppController:
    def __init__(self):
        self.automaton = Automaton()
        self.current_path = None
        self.dirty = False

    def mark_dirty(self) -> None:
        self.dirty = True

    def replace_automaton(self, automaton: Automaton) -> None:
        """Sustituye el automata activo (p. ej. resultado de CU5)."""
        self.automaton = automaton
        self.current_path = None
        self.dirty = True

    def new_automaton(self) -> Automaton:
        self.automaton = Automaton()
        self.current_path = None
        self.dirty = False
        return self.automaton

    def open_automaton(self, path: str) -> Automaton:
        self.automaton = persistence.load(path)
        self.current_path = path
        self.dirty = False
        return self.automaton

    def save_automaton(self, path: str | None = None) -> None:
        target = path or self.current_path
        if not target:
            raise ValueError("No se especifico una ruta de guardado.")
        persistence.save(self.automaton, target)
        self.current_path = target
        self.dirty = False
