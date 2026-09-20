"""MainWindow (CU1/CU2): ventana principal de la aplicacion."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core import persistence
from core.automaton import Automaton
from core.subset_construction import subset_construction
from core.validator import ConsistencyValidator
from ui.canvas_editor import CanvasEditor
from ui.consistency_report import ConsistencyReportView
from ui.language_dialog import LanguageRegistryView
from ui.tape_simulator_view import TapeSimulatorView
from ui.transition_table import TransitionTableView

APP_TITLE = "Sistema de Diseno y Prueba de Automatas"


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1200x800")

        self.automaton = Automaton()
        self.current_path = None
        self.dirty = False

        self._build_menu()
        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_exit)

    # ------------------------------------------------------------------
    # CU2 - Cargar Interfaz Grafica de Usuario
    # ------------------------------------------------------------------
    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self._on_new)
        file_menu.add_command(label="Abrir...", command=self._on_open)
        file_menu.add_command(label="Guardar", command=self._on_save)
        file_menu.add_command(label="Guardar como...", command=self._on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self._on_exit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        automaton_menu = tk.Menu(menubar, tearoff=0)
        automaton_menu.add_command(label="Convertir AFND a AFD", command=self._on_convert)
        automaton_menu.add_command(label="Validar consistencia", command=self._on_validate)
        automaton_menu.add_command(label="Registrar lenguaje", command=self._on_focus_language)
        menubar.add_cascade(label="Automata", menu=automaton_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Acerca de", command=self._on_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.config(menu=menubar)

    def _build_layout(self):
        main_pane = ttk.PanedWindow(self, orient="vertical")
        main_pane.pack(fill="both", expand=True)

        top_pane = ttk.PanedWindow(main_pane, orient="horizontal")
        main_pane.add(top_pane, weight=4)

        self.canvas_editor = CanvasEditor(top_pane, self.automaton, on_change=self._on_model_changed)
        top_pane.add(self.canvas_editor, weight=3)

        notebook = ttk.Notebook(top_pane)
        top_pane.add(notebook, weight=2)

        self.table_view = TransitionTableView(notebook, self.automaton, on_change=self._on_model_changed)
        notebook.add(self.table_view, text="Tabla de transiciones")

        self.language_view = LanguageRegistryView(notebook, self.automaton, on_change=self._on_model_changed)
        notebook.add(self.language_view, text="Registro de lenguaje")

        self.report_view = ConsistencyReportView(notebook, self.automaton)
        notebook.add(self.report_view, text="Reporte de consistencia")
        self.notebook = notebook

        self.tape_view = TapeSimulatorView(
            main_pane, self.automaton, on_active_states_changed=self.canvas_editor.set_active_states
        )
        main_pane.add(self.tape_view, weight=1)

    # ------------------------------------------------------------------
    def _on_model_changed(self):
        self.dirty = True
        self._ensure_positions()
        self.canvas_editor.redraw()
        self.table_view.refresh()
        self.report_view.refresh()

    def _ensure_positions(self):
        next_slot = len(self.automaton.positions)
        for state in sorted(self.automaton.states):
            if state not in self.automaton.positions:
                col, row = next_slot % 5, next_slot // 5
                self.automaton.positions[state] = (120 + col * 140, 100 + row * 120)
                next_slot += 1

    def _refresh_all_views(self):
        self.canvas_editor.set_automaton(self.automaton)
        self.table_view.set_automaton(self.automaton)
        self.language_view.set_automaton(self.automaton)
        self.report_view.set_automaton(self.automaton)
        self.tape_view.set_automaton(self.automaton)

    # ------------------------------------------------------------------
    # CU1/CU3 - Ciclo de vida del aplicativo
    # ------------------------------------------------------------------
    def _confirm_discard_changes(self) -> bool:
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel(
            "Cambios sin guardar", "Hay cambios sin guardar. ¿Desea guardarlos antes de continuar?"
        )
        if answer is None:
            return False
        if answer is True:
            return self._on_save()
        return True

    def _on_new(self):
        if not self._confirm_discard_changes():
            return
        self.automaton = Automaton()
        self.current_path = None
        self.dirty = False
        self._refresh_all_views()

    def _on_open(self):
        if not self._confirm_discard_changes():
            return
        path = filedialog.askopenfilename(filetypes=[("Automata", "*.autm"), ("Todos", "*.*")])
        if not path:
            return
        try:
            self.automaton = persistence.load(path)
        except Exception as exc:
            messagebox.showerror("Error al abrir", str(exc))
            return
        self.current_path = path
        self.dirty = False
        self._refresh_all_views()

    def _on_save(self) -> bool:
        if self.current_path is None:
            return self._on_save_as()
        try:
            persistence.save(self.automaton, self.current_path)
        except Exception as exc:
            messagebox.showerror("Error al guardar", str(exc))
            return False
        self.dirty = False
        return True

    def _on_save_as(self) -> bool:
        path = filedialog.asksaveasfilename(
            defaultextension=".autm", filetypes=[("Automata", "*.autm")]
        )
        if not path:
            return False
        self.current_path = path
        return self._on_save()

    def _on_exit(self):
        if self._confirm_discard_changes():
            self.destroy()

    # ------------------------------------------------------------------
    # CU5 / CU7 / CU8
    # ------------------------------------------------------------------
    def _on_validate(self):
        self.notebook.select(self.report_view)
        report = self.report_view.refresh()
        if report.is_valid and not report.warnings:
            messagebox.showinfo("Consistencia", "El automata es consistente.")

    def _on_convert(self):
        report = ConsistencyValidator(self.automaton).run_all()
        if not report.is_valid:
            self.notebook.select(self.report_view)
            self.report_view.refresh()
            messagebox.showerror(
                "No se puede convertir",
                "El automata tiene errores de consistencia. Corrijalos antes de convertir.",
            )
            return
        if not messagebox.askyesno(
            "Convertir a AFD",
            "Esto reemplazara el diagrama actual por el AFD equivalente (construccion de subconjuntos). ¿Continuar?",
        ):
            return
        dfa = subset_construction(self.automaton)
        dfa.language = self.automaton.language
        self.automaton = dfa
        self.current_path = None
        self.dirty = True
        self._refresh_all_views()
        self.notebook.select(self.table_view)

    def _on_focus_language(self):
        self.notebook.select(self.language_view)

    def _on_about(self):
        messagebox.showinfo(
            "Acerca de",
            f"{APP_TITLE}\n\n"
            "Disena, edita, visualiza y prueba AFD, AFN y AFN-lambda,\n"
            "conforme a la teoria de Rodrigo De Castro (Cap. 2, Teoria de la Computacion).",
        )


def run():
    app = MainWindow()
    app.mainloop()
