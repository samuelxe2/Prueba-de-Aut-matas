"""Modelo de dominio: M = (Sigma, Q, q0, F, delta/Delta).

Un unico modelo Automaton cubre AFD, AFN y AFN-lambda: el "tipo" se deriva
de las transiciones (uso de lambda, o mas de un destino / transicion
faltante para algun (estado, simbolo)) en vez de mantenerse tres clases
separadas, lo que evita duplicar logica de simulacion y persistencia.
"""
from __future__ import annotations

from dataclasses import dataclass, field

LAMBDA = "λ"  # simbolo especial para transiciones nulas


@dataclass
class LanguageEntry:
    name: str = ""
    regex_or_description: str = ""
    linked_automaton_id: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.regex_or_description,
        }

    @staticmethod
    def from_dict(data: dict | None) -> "LanguageEntry":
        if not data:
            return LanguageEntry()
        return LanguageEntry(
            name=data.get("name", ""),
            regex_or_description=data.get("description", ""),
        )


@dataclass
class Automaton:
    alphabet: set = field(default_factory=set)
    states: set = field(default_factory=set)
    initial_state: str | None = None
    final_states: set = field(default_factory=set)
    # (estado, simbolo) -> conjunto de estados destino. simbolo == LAMBDA para AFN-lambda.
    transitions: dict = field(default_factory=dict)
    # posiciones (x, y) de cada estado en el lienzo, usadas solo por la UI.
    positions: dict = field(default_factory=dict)
    language: LanguageEntry = field(default_factory=LanguageEntry)

    # ------------------------------------------------------------------
    # Clasificacion del modelo
    # ------------------------------------------------------------------
    @property
    def has_lambda(self) -> bool:
        return any(sym == LAMBDA for (_, sym) in self.transitions.keys())

    def is_deterministic(self) -> bool:
        if self.has_lambda:
            return False
        for state in self.states:
            for sym in self.alphabet:
                targets = self.transitions.get((state, sym), set())
                if len(targets) > 1:
                    return False
        return True

    def kind(self) -> str:
        if self.has_lambda:
            return "AFN-lambda"
        if self.is_deterministic():
            return "AFD"
        return "AFN"

    # ------------------------------------------------------------------
    # Operaciones basicas sobre transiciones
    # ------------------------------------------------------------------
    def add_transition(self, origin: str, symbol: str, destination: str) -> None:
        key = (origin, symbol)
        self.transitions.setdefault(key, set()).add(destination)
        self.states.add(origin)
        self.states.add(destination)
        if symbol != LAMBDA:
            self.alphabet.add(symbol)

    def remove_transition(self, origin: str, symbol: str, destination: str) -> None:
        key = (origin, symbol)
        if key in self.transitions:
            self.transitions[key].discard(destination)
            if not self.transitions[key]:
                del self.transitions[key]

    def remove_state(self, state: str) -> None:
        self.states.discard(state)
        self.final_states.discard(state)
        self.positions.pop(state, None)
        if self.initial_state == state:
            self.initial_state = None
        for key in list(self.transitions.keys()):
            origin, sym = key
            if origin == state:
                del self.transitions[key]
            else:
                self.transitions[key].discard(state)
                if not self.transitions[key]:
                    del self.transitions[key]

    # ------------------------------------------------------------------
    # Cierre lambda (usado tambien por el simulador de cadenas)
    # ------------------------------------------------------------------
    def lambda_closure(self, states) -> frozenset:
        stack = list(states)
        closure = set(states)
        while stack:
            q = stack.pop()
            for target in self.transitions.get((q, LAMBDA), set()):
                if target not in closure:
                    closure.add(target)
                    stack.append(target)
        return frozenset(closure)

    def move(self, states, symbol) -> set:
        result = set()
        for q in states:
            result |= self.transitions.get((q, symbol), set())
        return result

    # ------------------------------------------------------------------
    # CU6 - Verificar Secuencia de Caracteres
    # ------------------------------------------------------------------
    def accepts(self, word: str) -> tuple:
        """Simula la cadena y regresa (aceptada, traza).

        La traza es una lista de "frames": en cada paso se guarda el
        conjunto de estados activos (tras el cierre lambda) y el simbolo
        consumido (None para el frame inicial).
        """
        if self.initial_state is None:
            return False, []

        current = self.lambda_closure({self.initial_state})
        trace = [{"symbol": None, "states": sorted(current)}]

        for symbol in word:
            current = self.lambda_closure(self.move(current, symbol))
            trace.append({"symbol": symbol, "states": sorted(current)})
            if not current:
                break

        accepted = bool(current & self.final_states)
        return accepted, trace

    # ------------------------------------------------------------------
    # Persistencia (formato .autm, JSON)
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "type": self.kind(),
            "alphabet": sorted(self.alphabet),
            "states": sorted(self.states),
            "initial_state": self.initial_state,
            "final_states": sorted(self.final_states),
            "transitions": {
                f"{origin},{symbol}": sorted(targets)
                for (origin, symbol), targets in self.transitions.items()
            },
            "positions": {state: list(pos) for state, pos in self.positions.items()},
            "language": self.language.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict) -> "Automaton":
        automaton = Automaton()
        automaton.alphabet = set(data.get("alphabet", []))
        automaton.states = set(data.get("states", []))
        automaton.initial_state = data.get("initial_state")
        automaton.final_states = set(data.get("final_states", []))
        for key, targets in data.get("transitions", {}).items():
            origin, symbol = key.split(",", 1)
            automaton.transitions[(origin, symbol)] = set(targets)
        automaton.positions = {
            state: tuple(pos) for state, pos in data.get("positions", {}).items()
        }
        automaton.language = LanguageEntry.from_dict(data.get("language"))
        return automaton
