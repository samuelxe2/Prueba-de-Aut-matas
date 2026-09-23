"""GraphRenderer: dibuja el diagrama de estados sobre un tk.Canvas.

Convenciones:
- estado -> circulo
- estado inicial -> circulo + flecha de entrada corta sin origen
- estado final -> doble circulo
- transicion delta(q,a)=p -> arco dirigido con etiqueta (agrupando simbolos)
- auto-lazo delta(q,a)=q -> arco curvo que sale y entra al mismo nodo
"""
from __future__ import annotations

import math

NODE_RADIUS = 28
FINAL_RING_GAP = 6

COLOR_NODE = "#ffffff"
COLOR_NODE_OUTLINE = "#1f2937"
COLOR_NODE_ACTIVE = "#fde68a"
COLOR_NODE_SELECTED = "#bfdbfe"
COLOR_EDGE = "#374151"
COLOR_TEXT = "#111827"


class GraphRenderer:
    def __init__(self, canvas):
        self.canvas = canvas

    def node_at(self, automaton, x, y):
        """Devuelve el nombre del estado bajo (x, y), o None."""
        for state in automaton.states:
            px, py = automaton.positions.get(state, (0, 0))
            if (px - x) ** 2 + (py - y) ** 2 <= NODE_RADIUS ** 2:
                return state
        return None

    def draw(self, automaton, active_states=None, selected_state=None, pending_source=None):
        canvas = self.canvas
        canvas.delete("all")
        active_states = active_states or set()

        edge_groups = self._group_edges(automaton)
        for (origin, dest), symbols in edge_groups.items():
            if origin == dest:
                self._draw_self_loop(automaton, origin, symbols)
            else:
                self._draw_edge(automaton, origin, dest, symbols, edge_groups)

        if automaton.initial_state and automaton.initial_state in automaton.states:
            self._draw_initial_arrow(automaton, automaton.initial_state)

        for state in automaton.states:
            self._draw_node(
                automaton,
                state,
                is_active=state in active_states,
                is_selected=state == selected_state or state == pending_source,
            )

    # ------------------------------------------------------------------
    def _group_edges(self, automaton):
        groups: dict[tuple[str, str], list[str]] = {}
        for (origin, symbol), targets in automaton.transitions.items():
            for dest in targets:
                groups.setdefault((origin, dest), []).append(symbol)
        for key in groups:
            groups[key] = sorted(set(groups[key]))
        return groups

    def _draw_node(self, automaton, state, is_active, is_selected):
        x, y = automaton.positions.get(state, (60, 60))
        color = COLOR_NODE
        if is_active:
            color = COLOR_NODE_ACTIVE
        elif is_selected:
            color = COLOR_NODE_SELECTED
        self.canvas.create_oval(
            x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS,
            fill=color, outline=COLOR_NODE_OUTLINE, width=2, tags=("node", state),
        )
        if state in automaton.final_states:
            r2 = NODE_RADIUS - FINAL_RING_GAP
            self.canvas.create_oval(
                x - r2, y - r2, x + r2, y + r2,
                outline=COLOR_NODE_OUTLINE, width=2, tags=("node", state),
            )
        self.canvas.create_text(
            x, y, text=state, fill=COLOR_TEXT, font=("Segoe UI", 10, "bold"),
            tags=("node", state),
        )

    def _draw_initial_arrow(self, automaton, state):
        x, y = automaton.positions.get(state, (60, 60))
        x0, y0 = x - NODE_RADIUS - 40, y
        x1, y1 = x - NODE_RADIUS - 4, y
        self.canvas.create_line(x0, y0, x1, y1, arrow="last", width=2, fill=COLOR_EDGE)

    def _draw_edge(self, automaton, origin, dest, symbols, edge_groups):
        x0, y0 = automaton.positions.get(origin, (60, 60))
        x1, y1 = automaton.positions.get(dest, (60, 60))
        dx, dy = x1 - x0, y1 - y0
        dist = math.hypot(dx, dy) or 1
        ux, uy = dx / dist, dy / dist

        # curvar si existe el arco inverso, para no solapar las dos flechas
        curve = 22 if (dest, origin) in edge_groups else 0
        nx, ny = -uy, ux  # normal unitaria

        sx, sy = x0 + ux * NODE_RADIUS, y0 + uy * NODE_RADIUS
        ex, ey = x1 - ux * NODE_RADIUS, y1 - uy * NODE_RADIUS
        mx, my = (sx + ex) / 2 + nx * curve, (sy + ey) / 2 + ny * curve

        label = ",".join(symbols)
        if curve:
            self.canvas.create_line(
                sx, sy, mx, my, ex, ey, smooth=True, arrow="last", width=2, fill=COLOR_EDGE,
            )
            lx, ly = mx + nx * 14, my + ny * 14
        else:
            self.canvas.create_line(sx, sy, ex, ey, arrow="last", width=2, fill=COLOR_EDGE)
            lx, ly = mx + nx * 14, my + ny * 14

        self.canvas.create_text(
            lx, ly, text=label, fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"),
        )

    def _draw_self_loop(self, automaton, state, symbols):
        x, y = automaton.positions.get(state, (60, 60))
        top = y - NODE_RADIUS
        r = 22
        self.canvas.create_arc(
            x - r, top - 2 * r + 6, x + r, top + 6,
            outline=COLOR_EDGE, width=2, style="arc", start=200, extent=320,
        )
        # cabeza de flecha aproximada en el extremo del arco
        self.canvas.create_line(x - 4, top - 6, x - 12, top - 2, arrow="last", width=2, fill=COLOR_EDGE)
        label = ",".join(symbols)
        self.canvas.create_text(
            x, top - 2 * r - 4, text=label, fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"),
        )
