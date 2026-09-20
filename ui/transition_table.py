"""TransitionTableView (CU4): tabla delta/Delta editable, sincronizada con el diagrama."""
from __future__ import annotations

from tkinter import simpledialog, ttk

from core.automaton import LAMBDA


class TransitionTableView(ttk.Frame):
    def __init__(self, master, automaton, on_change=None):
        super().__init__(master)
        self.automaton = automaton
        self.on_change = on_change or (lambda: None)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Agregar simbolo a Sigma", command=self._add_symbol).pack(side="left", padx=4, pady=4)

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self._on_double_click)

        self.refresh()

    def set_automaton(self, automaton):
        self.automaton = automaton
        self.refresh()

    def _columns(self):
        cols = sorted(self.automaton.alphabet)
        if self.automaton.has_lambda:
            cols.append(LAMBDA)
        return cols

    def refresh(self):
        cols = self._columns()
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ["estado"] + cols
        self.tree.heading("estado", text="Estado")
        self.tree.column("estado", width=90, anchor="center")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")

        for state in sorted(self.automaton.states):
            row = [state]
            prefix = ">" if state == self.automaton.initial_state else ""
            suffix = "*" if state in self.automaton.final_states else ""
            row[0] = f"{prefix}{state}{suffix}"
            for sym in cols:
                targets = self.automaton.transitions.get((state, sym), set())
                row.append(",".join(sorted(targets)))
            self.tree.insert("", "end", iid=state, values=row)

    def _add_symbol(self):
        sym = simpledialog.askstring("Agregar simbolo", "Nuevo simbolo de Sigma:", parent=self)
        if sym:
            sym = sym.strip()
        if sym:
            self.automaton.alphabet.add(sym)
            self.on_change()
            self.refresh()

    def _on_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or col_id == "#1":
            return
        cols = self._columns()
        col_index = int(col_id.replace("#", "")) - 2
        if col_index < 0 or col_index >= len(cols):
            return
        state = row_id
        symbol = cols[col_index]
        current = ",".join(sorted(self.automaton.transitions.get((state, symbol), set())))
        new_value = simpledialog.askstring(
            "Editar transicion",
            f"delta({state}, {symbol}) = (deje vacio para borrar; separe varios estados con coma)",
            initialvalue=current,
            parent=self,
        )
        if new_value is None:
            return
        targets = {t.strip() for t in new_value.split(",") if t.strip()}
        key = (state, symbol)
        if targets:
            self.automaton.states |= targets
            self.automaton.transitions[key] = targets
        else:
            self.automaton.transitions.pop(key, None)
        self.on_change()
        self.refresh()
