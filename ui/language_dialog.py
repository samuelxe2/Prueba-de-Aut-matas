"""LanguageRegistryView (CU8): registra nombre/descripcion de L(M).

Capa de Vista: delega en AutomatonController.register_language(), que a su
vez exige (via ValidationController) que el automata sea consistente.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class LanguageRegistryView(ttk.Frame):
    def __init__(self, master, controller, on_change=None):
        super().__init__(master)
        self.controller = controller
        self.on_change = on_change or (lambda: None)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Nombre del lenguaje:").grid(row=0, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="w")

        ttk.Label(form, text="Descripcion / expresion regular:").grid(row=1, column=0, sticky="nw", pady=4)
        self.desc_text = tk.Text(form, width=40, height=4)
        self.desc_text.grid(row=1, column=1, sticky="w")

        ttk.Button(form, text="Registrar lenguaje", command=self._register).grid(row=2, column=1, sticky="w", pady=8)

        self.refresh()

    def refresh(self):
        automaton = self.controller.automaton
        self.name_var.set(automaton.language.name)
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", automaton.language.regex_or_description)

    def _register(self):
        name = self.name_var.get().strip()
        description = self.desc_text.get("1.0", "end").strip()
        report = self.controller.register_language(name, description)
        if not report.is_valid:
            messagebox.showerror(
                "Automata inconsistente",
                "Solo se puede registrar un lenguaje sobre un automata consistente.\n\n"
                + "\n".join(report.errors),
            )
            return
        self.on_change()
        messagebox.showinfo("Lenguaje registrado", "El lenguaje se asocio correctamente al automata.")
