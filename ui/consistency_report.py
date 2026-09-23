"""ConsistencyReportView (CU7): reporte de validacion del grafo.

Capa de Vista: delega la validacion en ValidationController y solo se
ocupa de pintar el resultado.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ConsistencyReportView(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ttk.Button(self, text="Validar consistencia", command=self.refresh).pack(anchor="w", padx=6, pady=6)
        self.kind_var = tk.StringVar()
        ttk.Label(self, textvariable=self.kind_var, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=6)

        self.text = tk.Text(self, height=15, wrap="word", state="disabled")
        self.text.pack(fill="both", expand=True, padx=6, pady=6)
        self.text.tag_configure("error", foreground="#dc2626")
        self.text.tag_configure("warning", foreground="#b45309")
        self.text.tag_configure("ok", foreground="#16a34a")

        self.refresh()

    def refresh(self):
        report = self.controller.validate()
        self.kind_var.set(f"Tipo detectado: {self.controller.automaton.kind()}")

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        if report.is_valid and not report.warnings:
            self.text.insert("end", "El automata es consistente. Sin observaciones.\n", "ok")
        else:
            for e in report.errors:
                self.text.insert("end", f"[ERROR] {e}\n", "error")
            for w in report.warnings:
                self.text.insert("end", f"[AVISO] {w}\n", "warning")
        self.text.configure(state="disabled")
        return report
