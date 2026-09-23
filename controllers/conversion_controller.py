"""ConversionController: CU5 - Transformar Modelo AFND a AFD.

Incluye (invoca) a ValidationController antes de convertir, tal como
indica la relacion "include" hacia CU7 en el diagrama de casos de uso.
"""
from __future__ import annotations

from core.automaton import Automaton
from core.subset_construction import subset_construction
from core.validator import ValidationReport
from controllers.app_controller import AppController
from controllers.validation_controller import ValidationController


class ConversionController:
    def __init__(self, app: AppController, validation: ValidationController):
        self.app = app
        self.validation = validation

    def convert_to_dfa(self) -> tuple[Automaton | None, ValidationReport]:
        report = self.validation.validate()
        if not report.is_valid:
            return None, report

        dfa = subset_construction(self.app.automaton)
        dfa.language = self.app.automaton.language
        self.app.replace_automaton(dfa)
        return dfa, report
