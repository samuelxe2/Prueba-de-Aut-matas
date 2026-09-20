"""CU5 - Transformar Modelo AFND a AFD (algoritmo de construccion de subconjuntos).

Implementacion directa de la seccion 2.5 del material de referencia.
"""
from __future__ import annotations

from core.automaton import Automaton


def _name_for(subset: frozenset) -> str:
    if not subset:
        return "muerto"
    return "{" + ",".join(sorted(subset)) + "}"


def subset_construction(source: Automaton) -> Automaton:
    """Convierte un AFN o AFN-lambda en un AFD equivalente."""
    if source.initial_state is None:
        raise ValueError("El automata no tiene estado inicial definido")

    start = source.lambda_closure({source.initial_state})
    dfa_states = {start}
    pending = [start]
    dfa_delta = {}

    while pending:
        subset = pending.pop()
        for symbol in sorted(source.alphabet):
            moved = source.move(subset, symbol)
            target = source.lambda_closure(moved)
            dfa_delta[(subset, symbol)] = target
            if target not in dfa_states:
                dfa_states.add(target)
                pending.append(target)

    dfa = Automaton()
    dfa.alphabet = set(source.alphabet)
    dfa.states = {_name_for(s) for s in dfa_states}
    dfa.initial_state = _name_for(start)
    dfa.final_states = {
        _name_for(s) for s in dfa_states if s & source.final_states
    }
    for (subset, symbol), target in dfa_delta.items():
        dfa.transitions[(_name_for(subset), symbol)] = {_name_for(target)}

    # layout simple en cuadricula para que la UI tenga algo razonable que dibujar
    ordered = sorted(dfa.states)
    for i, name in enumerate(ordered):
        col = i % 4
        row = i // 4
        dfa.positions[name] = (120 + col * 180, 100 + row * 140)

    return dfa
