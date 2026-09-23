"""ValidationController: CU7 - Verificar Consistencia del Grafo.

Es invocado por AutomatonController (CU4), ConversionController (CU5) y
SimulationController (CU6), reproduciendo las flechas "include" hacia CU7
del diagrama de casos de uso.
"""
from __future__ import annotations

from core.automaton import Automaton
from core.validator import ConsistencyValidator, ValidationReport
from controllers.app_controller import AppController


class ValidationController:
    def __init__(self, app: AppController):
        self.app = app

    @property
    def automaton(self) -> Automaton:
        return self.app.automaton

    def validate(self) -> ValidationReport:
        return ConsistencyValidator(self.app.automaton).run_all()
