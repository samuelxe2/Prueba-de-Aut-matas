"""CU6 - Verificar Secuencia de Caracteres: simulador paso a paso de "el cuadro"."""
from __future__ import annotations

from dataclasses import dataclass

from core.automaton import Automaton

BLANK = "≡"  # simbolo de casilla en blanco tras el final de la cadena


@dataclass
class TapeFrame:
    position: int
    symbol: str | None
    states: list
    finished: bool
    accepted: bool | None


class TapeSimulator:
    def __init__(self, automaton: Automaton, input_string: str, trailing_blanks: int = 3):
        self.automaton = automaton
        self.input_string = input_string
        self.trailing_blanks = trailing_blanks
        self._current = automaton.lambda_closure(
            {automaton.initial_state} if automaton.initial_state else set()
        )
        self._position = -1
        self._finished = False

    @property
    def tape_symbols(self) -> list:
        return list(self.input_string) + [BLANK] * self.trailing_blanks

    def current_frame(self) -> TapeFrame:
        accepted = None
        if self._finished:
            accepted = bool(self._current & self.automaton.final_states)
        symbol = None
        if 0 <= self._position < len(self.input_string):
            symbol = self.input_string[self._position]
        return TapeFrame(
            position=self._position,
            symbol=symbol,
            states=sorted(self._current),
            finished=self._finished,
            accepted=accepted,
        )

    def has_next(self) -> bool:
        return not self._finished

    def step(self) -> TapeFrame:
        if self._finished:
            return self.current_frame()

        if self._position + 1 >= len(self.input_string):
            self._finished = True
            return self.current_frame()

        self._position += 1
        symbol = self.input_string[self._position]
        self._current = self.automaton.lambda_closure(self.automaton.move(self._current, symbol))

        if self._position + 1 >= len(self.input_string) or not self._current:
            self._finished = True

        return self.current_frame()

    def run_to_end(self) -> list:
        frames = [self.current_frame()]
        while self.has_next():
            frames.append(self.step())
        return frames
