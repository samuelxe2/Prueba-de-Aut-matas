"""CU7 - Verificar Consistencia del Grafo.

Reglas basadas en la definicion formal M = (Sigma, Q, q0, F, delta/Delta).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.automaton import LAMBDA, Automaton


@dataclass
class ValidationReport:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def __bool__(self) -> bool:
        return self.is_valid


class ConsistencyValidator:
    def __init__(self, automaton: Automaton):
        self.m = automaton

    def check_unique_initial_state(self, report: ValidationReport) -> None:
        if self.m.initial_state is None:
            report.errors.append("No hay un estado inicial definido (q0).")
        elif self.m.initial_state not in self.m.states:
            report.errors.append(
                f"El estado inicial '{self.m.initial_state}' no pertenece a Q."
            )

    def check_final_subset_of_states(self, report: ValidationReport) -> None:
        if not self.m.final_states:
            report.warnings.append("F es vacio: el automata no acepta ninguna cadena.")
        missing = self.m.final_states - self.m.states
        if missing:
            report.errors.append(
                "F no es subconjunto de Q, estados invalidos: " + ", ".join(sorted(missing))
            )

    def check_symbols_in_alphabet(self, report: ValidationReport) -> None:
        used = {sym for (_, sym) in self.m.transitions.keys() if sym != LAMBDA}
        missing = used - self.m.alphabet
        if missing:
            report.errors.append(
                "Se usan simbolos fuera de Sigma: " + ", ".join(sorted(missing))
            )

    def check_unreachable_states(self, report: ValidationReport) -> None:
        if self.m.initial_state is None:
            return
        reachable = {self.m.initial_state}
        stack = [self.m.initial_state]
        while stack:
            q = stack.pop()
            for (origin, _symbol), targets in self.m.transitions.items():
                if origin == q:
                    for t in targets:
                        if t not in reachable:
                            reachable.add(t)
                            stack.append(t)
        unreachable = self.m.states - reachable
        if unreachable:
            report.warnings.append(
                "Estados no alcanzables desde q0: " + ", ".join(sorted(unreachable))
            )

    def check_total_function_if_afd(self, report: ValidationReport) -> None:
        if self.m.has_lambda or not self.m.is_deterministic():
            return
        missing = []
        for state in sorted(self.m.states):
            for symbol in sorted(self.m.alphabet):
                if (state, symbol) not in self.m.transitions:
                    missing.append(f"delta({state},{symbol})")
        if missing:
            report.warnings.append(
                "AFD con funcion de transicion no total (version simplificada, "
                "se asume estado limbo implicito): " + ", ".join(missing)
            )

    def run_all(self) -> ValidationReport:
        report = ValidationReport()
        self.check_unique_initial_state(report)
        self.check_final_subset_of_states(report)
        self.check_symbols_in_alphabet(report)
        self.check_unreachable_states(report)
        self.check_total_function_if_afd(report)
        return report
