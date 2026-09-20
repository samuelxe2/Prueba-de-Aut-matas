"""CanvasEditor: lienzo interactivo del diagrama de estados (seccion 5.2 del SDD)."""
from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk

from core.automaton import LAMBDA
from rendering.graph_renderer import GraphRenderer

MODE_SELECT = "select"
MODE_ADD_STATE = "add_state"
MODE_ADD_TRANSITION = "add_transition"

DRAG_THRESHOLD = 3


class CanvasEditor(ttk.Frame):
    def __init__(self, master, automaton, on_change=None):
        super().__init__(master)
        self.automaton = automaton
        self.on_change = on_change or (lambda: None)
        self.mode = tk.StringVar(value=MODE_SELECT)
        self.active_states = set()

        self._drag_state = None
        self._drag_start = None
        self._pending_source = None
        self._selected = None
        self._state_counter = 0

        self._build_toolbar()
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=1, highlightbackground="#d1d5db")
        self.canvas.pack(fill="both", expand=True)
        self.renderer = GraphRenderer(self.canvas)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)

        self.redraw()

    # ------------------------------------------------------------------
    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x")
        ttk.Radiobutton(bar, text="Seleccionar / Mover", variable=self.mode, value=MODE_SELECT).pack(side="left", padx=4, pady=4)
        ttk.Radiobutton(bar, text="Agregar estado", variable=self.mode, value=MODE_ADD_STATE).pack(side="left", padx=4)
        ttk.Radiobutton(bar, text="Agregar transicion", variable=self.mode, value=MODE_ADD_TRANSITION).pack(side="left", padx=4)
        ttk.Label(bar, text="(clic derecho sobre un estado: renombrar / inicial / final / eliminar)").pack(side="left", padx=10)

    # ------------------------------------------------------------------
    def set_automaton(self, automaton):
        self.automaton = automaton
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

    def _next_state_name(self):
        while True:
            name = f"q{self._state_counter}"
            self._state_counter += 1
            if name not in self.automaton.states:
                return name

    # ------------------------------------------------------------------
    def _on_press(self, event):
        state = self.renderer.node_at(self.automaton, event.x, event.y)
        mode = self.mode.get()

        if mode == MODE_ADD_STATE:
            if state is None:
                name = self._next_state_name()
                self.automaton.states.add(name)
                self.automaton.positions[name] = (event.x, event.y)
                if self.automaton.initial_state is None:
                    self.automaton.initial_state = name
                self.on_change()
                self.redraw()
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
            self._drag_start = (event.x, event.y)
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
            self.automaton.add_transition(origin, sym, dest)
        self.on_change()
        self.redraw()

    def _on_drag(self, event):
        if self.mode.get() != MODE_SELECT or self._drag_state is None:
            return
        self.automaton.positions[self._drag_state] = (event.x, event.y)
        self.redraw()

    def _on_release(self, event):
        if self._drag_state is not None:
            self.on_change()
        self._drag_state = None
        self._drag_start = None

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
        if not new_name or new_name == state or new_name in self.automaton.states:
            return
        m = self.automaton
        m.states.discard(state)
        m.states.add(new_name)
        if m.initial_state == state:
            m.initial_state = new_name
        if state in m.final_states:
            m.final_states.discard(state)
            m.final_states.add(new_name)
        if state in m.positions:
            m.positions[new_name] = m.positions.pop(state)
        for key in list(m.transitions.keys()):
            origin, sym = key
            targets = m.transitions[key]
            new_targets = {new_name if t == state else t for t in targets}
            if origin == state:
                del m.transitions[key]
                m.transitions[(new_name, sym)] = new_targets
            else:
                m.transitions[key] = new_targets
        self.on_change()
        self.redraw()

    def _toggle_initial(self, state):
        self.automaton.initial_state = None if self.automaton.initial_state == state else state
        self.on_change()
        self.redraw()

    def _toggle_final(self, state):
        if state in self.automaton.final_states:
            self.automaton.final_states.discard(state)
        else:
            self.automaton.final_states.add(state)
        self.on_change()
        self.redraw()

    def _delete_state(self, state):
        if not messagebox.askyesno("Eliminar estado", f"¿Eliminar el estado '{state}' y sus transiciones?"):
            return
        self.automaton.remove_state(state)
        if self._selected == state:
            self._selected = None
        self.on_change()
        self.redraw()
