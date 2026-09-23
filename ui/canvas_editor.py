"""CanvasEditor: lienzo interactivo del diagrama de estados.

Capa de Vista: no muta el Automaton directamente, delega toda edicion del
grafo al AutomatonController y solo se ocupa de eventos de mouse y dibujo.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk

from core.automaton import LAMBDA
from rendering.graph_renderer import GraphRenderer

MODE_SELECT = "select"
MODE_ADD_STATE = "add_state"
MODE_ADD_TRANSITION = "add_transition"


class CanvasEditor(ttk.Frame):
    def __init__(self, master, controller, on_change=None):
        super().__init__(master)
        self.controller = controller
        self.on_change = on_change or (lambda: None)
        self.mode = tk.StringVar(value=MODE_SELECT)
        self.active_states = set()

        self._drag_state = None
        self._pending_source = None
        self._selected = None

        self._build_toolbar()
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=1, highlightbackground="#d1d5db")
        self.canvas.pack(fill="both", expand=True)
        self.renderer = GraphRenderer(self.canvas)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)

        self.redraw()

    @property
    def automaton(self):
        return self.controller.automaton

    # ------------------------------------------------------------------
    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x")
        ttk.Radiobutton(bar, text="Seleccionar / Mover", variable=self.mode, value=MODE_SELECT).pack(side="left", padx=4, pady=4)
        ttk.Radiobutton(bar, text="Agregar estado", variable=self.mode, value=MODE_ADD_STATE).pack(side="left", padx=4)
        ttk.Radiobutton(bar, text="Agregar transicion", variable=self.mode, value=MODE_ADD_TRANSITION).pack(side="left", padx=4)
        ttk.Label(bar, text="(clic derecho sobre un estado: renombrar / inicial / final / eliminar)").pack(side="left", padx=10)

    # ------------------------------------------------------------------
    def reset_view(self):
        self._pending_source = None
        self._selected = None
        self.active_states = set()
        self.redraw()

    def set_active_states(self, states):
        self.active_states = set(states)
        self.redraw()

    def redraw(self):
        self.renderer.draw(
            self.automaton,
            active_states=self.active_states,
            selected_state=self._selected,
            pending_source=self._pending_source,
        )

    def _notify_changed(self):
        self.on_change()
        self.redraw()

    # ------------------------------------------------------------------
    def _on_press(self, event):
        state = self.renderer.node_at(self.automaton, event.x, event.y)
        mode = self.mode.get()

        if mode == MODE_ADD_STATE:
            if state is None:
                self.controller.add_state((event.x, event.y))
                self._notify_changed()
            return

        if mode == MODE_ADD_TRANSITION:
            if state is None:
                return
            if self._pending_source is None:
                self._pending_source = state
                self.redraw()
            else:
                origin, dest = self._pending_source, state
                self._pending_source = None
                self._prompt_symbols(origin, dest)
            return

        # MODE_SELECT
        self._selected = state
        if state is not None:
            self._drag_state = state
        self.redraw()

    def _prompt_symbols(self, origin, dest):
        text = simpledialog.askstring(
            "Nueva transicion",
            f"Simbolo(s) para {origin} -> {dest}\n"
            f"(separe varios con coma; use '{LAMBDA}' o 'lambda' para transicion nula)",
            parent=self,
        )
        if not text:
            self.redraw()
            return
        symbols = [s.strip() for s in text.split(",") if s.strip()]
        for sym in symbols:
            if sym.lower() in ("lambda", "l", LAMBDA):
                sym = LAMBDA
            self.controller.add_transition(origin, sym, dest)
        self._notify_changed()

    def _on_drag(self, event):
        if self.mode.get() != MODE_SELECT or self._drag_state is None:
            return
        self.controller.move_state(self._drag_state, (event.x, event.y))
        self.redraw()

    def _on_release(self, event):
        if self._drag_state is not None:
            self.on_change()
        self._drag_state = None

    def _on_right_click(self, event):
        state = self.renderer.node_at(self.automaton, event.x, event.y)
        if state is None:
            return
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Renombrar", command=lambda: self._rename_state(state))
        is_initial = self.automaton.initial_state == state
        is_final = state in self.automaton.final_states
        menu.add_command(
            label="Quitar como inicial" if is_initial else "Definir como inicial",
            command=lambda: self._toggle_initial(state),
        )
        menu.add_command(
            label="Quitar de finales" if is_final else "Marcar como final",
            command=lambda: self._toggle_final(state),
        )
        menu.add_separator()
        menu.add_command(label="Eliminar estado", command=lambda: self._delete_state(state))
        menu.tk_popup(event.x_root, event.y_root)

    def _rename_state(self, state):
        new_name = simpledialog.askstring("Renombrar estado", "Nuevo nombre:", initialvalue=state, parent=self)
        if new_name is None:
            return
        if not self.controller.rename_state(state, new_name):
            return
        if self._selected == state:
            self._selected = new_name
        self._notify_changed()

    def _toggle_initial(self, state):
        self.controller.toggle_initial(state)
        self._notify_changed()

    def _toggle_final(self, state):
        self.controller.toggle_final(state)
        self._notify_changed()

    def _delete_state(self, state):
        if not messagebox.askyesno("Eliminar estado", f"¿Eliminar el estado '{state}' y sus transiciones?"):
            return
        self.controller.remove_state(state)
        if self._selected == state:
            self._selected = None
        self._notify_changed()
