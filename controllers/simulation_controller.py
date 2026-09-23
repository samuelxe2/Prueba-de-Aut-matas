"""SimulationController: CU6 - Verificar Secuencia de Caracteres.

Incluye (invoca) a ValidationController antes de simular, y expone al
TapeSimulator paso a paso para que la Vista solo se ocupe de dibujar
cada TapeFrame que este controlador entrega.
"""
from __future__ import annotations

from core.simulator import TapeFrame, TapeSimulator
from core.validator import ValidationReport
from controllers.app_controller import AppController
from controllers.validation_controller import ValidationController


class SimulationController:
    def __init__(self, app: AppController, validation: ValidationController):
        self.app = app
        self.validation = validation
        self.simulator: TapeSimulator | None = None

    @property
    def tape_symbols(self) -> list:
        return self.simulator.tape_symbols if self.simulator else []

    def start(self, word: str) -> tuple[TapeFrame | None, ValidationReport]:
        report = self.validation.validate()
        if not report.is_valid:
            self.simulator = None
            return None, report
        self.simulator = TapeSimulator(self.app.automaton, word)
        return self.simulator.current_frame(), report

    def has_next(self) -> bool:
        return self.simulator is not None and self.simulator.has_next()

    def step(self) -> TapeFrame | None:
        if self.simulator is None:
            return None
        return self.simulator.step()

    def reset(self) -> None:
        self.simulator = None
