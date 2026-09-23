"""AutomatonController: operaciones de edicion del grafo (CU4 - Tabla de Transiciones
y las mutaciones que dispara el editor de lienzo), mas el registro de lenguaje (CU8).

Toda mutacion del modelo que antes hacia la Vista directamente sobre el
Automaton (agregar/mover/renombrar estados, agregar transiciones, etc.)
pasa por aqui, para que la Vista no conozca las reglas del dominio.
"""
from __future__ import annotations

from core.automaton import Automaton
from core.validator import ValidationReport
from controllers.app_controller import AppController
from controllers.validation_controller import ValidationController


class AutomatonController:
    def __init__(self, app: AppController, validation: ValidationController):
        self.app = app
        self.validation = validation

    @property
    def automaton(self) -> Automaton:
        return self.app.automaton

    # ------------------------------------------------------------------
    # Estados
    # ------------------------------------------------------------------
    def next_state_name(self) -> str:
        i = 0
        existing = self.automaton.states
        while f"q{i}" in existing:
            i += 1
        return f"q{i}"

    def add_state(self, position, name: str | None = None) -> str:
        m = self.automaton
        name = name or self.next_state_name()
        m.states.add(name)
        m.positions[name] = position
        if m.initial_state is None:
            m.initial_state = name
        self.app.mark_dirty()
        return name

    def move_state(self, state: str, position) -> None:
        self.automaton.positions[state] = position
        self.app.mark_dirty()

    def rename_state(self, old: str, new: str) -> bool:
        m = self.automaton
        if not new or new == old or new in m.states:
            return False
        m.states.discard(old)
        m.states.add(new)
        if m.initial_state == old:
            m.initial_state = new
        if old in m.final_states:
            m.final_states.discard(old)
            m.final_states.add(new)
        if old in m.positions:
            m.positions[new] = m.positions.pop(old)
        for key in list(m.transitions.keys()):
            origin, sym = key
            targets = m.transitions[key]
            new_targets = {new if t == old else t for t in targets}
            if origin == old:
                del m.transitions[key]
                m.transitions[(new, sym)] = new_targets
            else:
                m.transitions[key] = new_targets
        self.app.mark_dirty()
        return True

    def toggle_initial(self, state: str) -> None:
        m = self.automaton
        m.initial_state = None if m.initial_state == state else state
        self.app.mark_dirty()

    def toggle_final(self, state: str) -> None:
        m = self.automaton
        if state in m.final_states:
            m.final_states.discard(state)
        else:
            m.final_states.add(state)
        self.app.mark_dirty()

    def remove_state(self, state: str) -> None:
        self.automaton.remove_state(state)
        self.app.mark_dirty()

    # ------------------------------------------------------------------
    # Transiciones / alfabeto
    # ------------------------------------------------------------------
    def add_transition(self, origin: str, symbol: str, destination: str) -> None:
        self.automaton.add_transition(origin, symbol, destination)
        self.app.mark_dirty()

    def set_transition_targets(self, origin: str, symbol: str, targets) -> None:
        m = self.automaton
        key = (origin, symbol)
        targets = set(targets)
        if targets:
            m.states |= targets
            m.transitions[key] = targets
        else:
            m.transitions.pop(key, None)
        self.ensure_positions()
        self.app.mark_dirty()

    def add_symbol(self, symbol: str) -> None:
        self.automaton.alphabet.add(symbol)
        self.app.mark_dirty()

    def ensure_positions(self) -> None:
        """Ubica en cuadricula cualquier estado sin posicion (p. ej. creado desde la tabla)."""
        m = self.automaton
        used = len(m.positions)
        for state in sorted(m.states):
            if state not in m.positions:
                col, row = used % 5, used // 5
                m.positions[state] = (120 + col * 140, 100 + row * 120)
                used += 1

    # ------------------------------------------------------------------
    # CU8 - Registrar Lenguaje (solo sobre un automata consistente)
    # ------------------------------------------------------------------
    def register_language(self, name: str, description: str) -> ValidationReport:
        report = self.validation.validate()
        if report.is_valid:
            self.automaton.language.name = name
            self.automaton.language.regex_or_description = description
            self.app.mark_dirty()
        return report
