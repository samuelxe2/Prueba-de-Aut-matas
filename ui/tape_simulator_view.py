"""TapeSimulatorView (CU6): panel inferior con "el cuadro" animado."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.simulator import TapeSimulator
from core.validator import ConsistencyValidator
from rendering.tape_renderer import TapeRenderer

STEP_DELAY_MS = 600


class TapeSimulatorView(ttk.Frame):
    def __init__(self, master, automaton, on_active_states_changed=None):
        super().__init__(master)
        self.automaton = automaton
        self.on_active_states_changed = on_active_states_changed or (lambda states: None)
        self.simulator = None
        self._playing = False
        self._after_id = None

        controls = ttk.Frame(self)
        controls.pack(fill="x")
        ttk.Label(controls, text="Cadena u:").pack(side="left", padx=(4, 2))
        self.input_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.input_var, width=30).pack(side="left", padx=2)
        ttk.Button(controls, text="Reiniciar", command=self._reset).pack(side="left", padx=4)
        ttk.Button(controls, text="Paso a paso", command=self._step).pack(side="left", padx=4)
        ttk.Button(controls, text="Reproducir", command=self._play).pack(side="left", padx=4)
        ttk.Button(controls, text="Detener", command=self._stop).pack(side="left", padx=4)
        self.status_var = tk.StringVar(value="Escriba una cadena y presione Reiniciar.")
        ttk.Label(controls, textvariable=self.status_var).pack(side="left", padx=10)

        self.canvas = tk.Canvas(self, bg="white", height=150, highlightthickness=1, highlightbackground="#d1d5db")
        self.canvas.pack(fill="x", expand=False)
        self.renderer = TapeRenderer(self.canvas)

    def set_automaton(self, automaton):
        self.automaton = automaton
        self._stop()
        self.simulator = None
        self.canvas.delete("all")

    # ------------------------------------------------------------------
    def _reset(self):
        self._stop()
        report = ConsistencyValidator(self.automaton).run_all()
        if not report.is_valid:
            self.status_var.set("Corrija los errores de consistencia antes de simular.")
            return
        word = self.input_var.get()
        self.simulator = TapeSimulator(self.automaton, word)
        frame = self.simulator.current_frame()
        self.renderer.draw(self.simulator.tape_symbols, frame)
        self.on_active_states_changed(frame.states)
        self.status_var.set("Listo. Use Paso a paso o Reproducir.")

    def _step(self):
        if self.simulator is None:
            self._reset()
            if self.simulator is None:
                return
        frame = self.simulator.step()
        self.renderer.draw(self.simulator.tape_symbols, frame)
        self.on_active_states_changed(frame.states)
        if frame.finished:
            self._stop()
            verdict = "ACEPTADA" if frame.accepted else "RECHAZADA"
            self.status_var.set(f"Cadena {verdict}.")

    def _play(self):
        if self.simulator is None:
            self._reset()
            if self.simulator is None:
                return
        self._playing = True
        self._tick()

    def _tick(self):
        if not self._playing or self.simulator is None:
            return
        if not self.simulator.has_next():
            self._stop()
            return
        self._step()
        if self.simulator and self.simulator.has_next() and self._playing:
            self._after_id = self.after(STEP_DELAY_MS, self._tick)

    def _stop(self):
        self._playing = False
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
