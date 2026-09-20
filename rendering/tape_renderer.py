"""TapeRenderer: dibuja "el cuadro" (la cinta) sobre un tk.Canvas, seccion 5.3 del SDD.

┌───┬───┬───┬───┬───┬───┬───┐
│ a │ a │ b │ a │ b │ ≡ │...│
└───┴───┴───┴───┴───┴───┴───┘
  ↑
[ q0 ]
"""
from __future__ import annotations

CELL_W = 50
CELL_H = 50
TOP_MARGIN = 20
LEFT_MARGIN = 30

COLOR_CELL = "#f9fafb"
COLOR_OUTLINE = "#1f2937"
COLOR_BOX_NEUTRAL = "#dc2626"
COLOR_BOX_ACCEPTED = "#16a34a"
COLOR_BOX_REJECTED = "#dc2626"


class TapeRenderer:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self, tape_symbols, frame):
        canvas = self.canvas
        canvas.delete("all")

        y0 = TOP_MARGIN
        y1 = y0 + CELL_H
        for i, symbol in enumerate(tape_symbols):
            x0 = LEFT_MARGIN + i * CELL_W
            x1 = x0 + CELL_W
            canvas.create_rectangle(x0, y0, x1, y1, fill=COLOR_CELL, outline=COLOR_OUTLINE, width=2)
            canvas.create_text(
                (x0 + x1) / 2, (y0 + y1) / 2, text=symbol, font=("Consolas", 14, "bold"),
            )

        pointer_index = max(frame.position, 0)
        cx = LEFT_MARGIN + pointer_index * CELL_W + CELL_W / 2

        arrow_top = y1 + 22
        arrow_bottom = y1 + 4
        canvas.create_line(cx, arrow_top, cx, arrow_bottom, arrow="last", width=2, fill=COLOR_OUTLINE)

        box_color = COLOR_BOX_NEUTRAL
        if frame.finished:
            box_color = COLOR_BOX_ACCEPTED if frame.accepted else COLOR_BOX_REJECTED

        label = ",".join(frame.states) if frame.states else "∅"
        box_w = max(60, 14 * len(label))
        bx0, by0 = cx - box_w / 2, arrow_top + 4
        bx1, by1 = cx + box_w / 2, arrow_top + 4 + 30
        canvas.create_rectangle(bx0, by0, bx1, by1, outline=box_color, width=3)
        canvas.create_text(cx, (by0 + by1) / 2, text=label, font=("Segoe UI", 11, "bold"), fill=box_color)

        if frame.finished:
            verdict = "ACEPTADA" if frame.accepted else "RECHAZADA"
            canvas.create_text(
                cx, by1 + 22, text=verdict, font=("Segoe UI", 11, "bold"), fill=box_color,
            )
