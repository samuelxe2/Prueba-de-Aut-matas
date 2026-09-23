"""Persistencia de automatas en formato propio .autm (JSON)."""
from __future__ import annotations

import json

from core.automaton import Automaton

EXTENSION = ".autm"


def save(automaton: Automaton, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(automaton.to_dict(), f, ensure_ascii=False, indent=2)


def load(path: str) -> Automaton:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Automaton.from_dict(data)
