# frontend.py
import tkinter as tk
from tkinter import ttk, font
import math
import random
import re
import collections
import backend


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        master.title("Решатель задачи 1 ЕГЭ")
        master.geometry("1200x800")
        master.minsize(1100, 700)

        self.style = ttk.Style(master)
        self.style.theme_use("clam")

        self.c = {
            "bg": "#f2f4f7",
            "card": "#ffffff",
            "muted": "#667085",
            "head": "#101828",
            "line": "#eaecf0",
            "btn": "#175cd3",
            "btn_fg": "white",
            "ok": "#067647",
            "ok_bg": "#ecfdf3",
            "err": "#b42318",
            "err_bg": "#fef3f2",
        }
        master.configure(bg=self.c["bg"])
        self.configure(style="Root.TFrame")

        self.f_title = font.Font(family="Segoe UI", size=14, weight="bold")
        self.f_h = font.Font(family="Segoe UI", size=11, weight="bold")
        self.f_lbl = font.Font(family="Segoe UI", size=10)
        self.f_res = font.Font(family="Consolas", size=15, weight="bold")

        self.style.configure("Root.TFrame", background=self.c["bg"])
        self.style.configure("Card.TFrame", background=self.c["card"], relief=tk.SOLID, borderwidth=1)
        self.style.configure("TLabel", background=self.c["card"], foreground=self.c["head"])
        self.style.configure("Muted.TLabel", background=self.c["card"], foreground=self.c["muted"])
        self.style.configure("Title.TLabel", background=self.c["bg"], foreground=self.c["head"], font=self.f_title)
        self.style.configure("H.TLabel", background=self.c["card"], foreground=self.c["head"], font=self.f_h)
        self.style.configure("Accent.TButton", padding=10, font=self.f_h, background=self.c["btn"], foreground=self.c["btn_fg"])
        self.style.map("Accent.TButton", background=[("active", self.c["btn"])])

        self.matrix_widgets = []
        self.dimension = 0
        self.node_positions = {}

        self._build()
        master.after(50, self.on_mode_change)

    def _build(self):
        self.grid(row=0, column=0, sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        top = ttk.Frame(self, style="Root.TFrame")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top.columnconfigure(0, weight=1)

        ttk.Label(top, text="Интерактивный решатель", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(top, text="Матрица ↔ граф ↔ ответ", style="Muted.TLabel").grid(row=1, column=0, sticky="w")

        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.grid(row=1, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)

        left = ttk.Frame(body, style="Root.TFrame")
        right = ttk.Frame(body, style="Root.TFrame")
        body.add(left, weight=2)
        body.add(right, weight=3)

        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self._card_settings(left).grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._card_matrix(left).grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self._card_input(left).grid(row=2, column=0, sticky="nsew")

        self._card_canvas(right).grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self._card_result(right).grid(row=1, column=0, sticky="nsew")

    def _card(self, parent):
        f = ttk.Frame(parent, style="Card.TFrame", padding=12)
        f.columnconfigure(0, weight=1)
        return f

    def _card_settings(self, parent):
        f = self._card(parent)
        ttk.Label(f, text="Настройки", style="H.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        row = ttk.Frame(f, style="Card.TFrame")
        row.grid(row=1, column=0, sticky="ew")
        row.columnconfigure(3, weight=1)

        ttk.Label(row, text="Размерность", font=self.f_lbl).grid(row=0, column=0, sticky="w")
        self.spin = ttk.Spinbox(row, from_=2, to=15, width=5, command=self.generate_matrix_grid)
        self.spin.set("7")
        self.spin.grid(row=0, column=1, sticky="w", padx=(8, 16))

        self.w_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row, text="Веса", variable=self.w_var, command=self.on_mode_change).grid(row=0, column=2, sticky="w")

        return f

    def _card_matrix(self, parent):
        f = self._card(parent)
        self.matrix_title = ttk.Label(f, text="Таблица", style="H.TLabel")
        self.matrix_title.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.matrix_frame = ttk.Frame(f, style="Card.TFrame")
        self.matrix_frame.grid(row=1, column=0, sticky="ew")
        return f

    def _card_input(self, parent):
        f = self._card(parent)
        ttk.Label(f, text="Данные графа", style="H.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.graph_label = ttk.Label(f, text="", font=self.f_lbl, style="Muted.TLabel")
        self.graph_label.grid(row=1, column=0, sticky="w")

        self.edges_text = tk.Text(f, height=8, relief=tk.SOLID, borderwidth=1, font=("Consolas", 10))
        self.edges_text.grid(row=2, column=0, sticky="nsew", pady=(6, 10))
        f.rowconfigure(2, weight=1)

        bottom = ttk.Frame(f, style="Card.TFrame")
        bottom.grid(row=3, column=0, sticky="ew")
        bottom.columnconfigure(1, weight=1)

        ttk.Label(bottom, text="Искомые вершины", font=self.f_lbl).grid(row=0, column=0, sticky="w")
        self.targets_entry = ttk.Entry(bottom)
        self.targets_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        return f

    def _card_canvas(self, parent):
        f = self._card(parent)
        head = ttk.Frame(f, style="Card.TFrame")
        head.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        head.columnconfigure(0, weight=1)

        ttk.Label(head, text="Граф", style="H.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(head, text="Обновить", command=self.draw_graph).grid(row=0, column=1, sticky="e")

        self.canvas = tk.Canvas(f, bg="white", relief=tk.SOLID, borderwidth=1, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        f.rowconfigure(1, weight=1)
        self.canvas.bind("<Configure>", lambda e: self.draw_graph())
        return f

    def _card_result(self, parent):
        f = self._card(parent)
        top = ttk.Frame(f, style="Card.TFrame")
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)

        ttk.Label(top, text="Ответ", style="H.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(top, text="Найти", style="Accent.TButton", command=self.solve_problem).grid(row=0, column=1, sticky="e")

        self.result_label = ttk.Label(f, text="...", font=self.f_res, padding=10, background="#f9fafb", relief=tk.RIDGE, anchor="center")
        self.result_label.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        return f

    def on_mode_change(self):
        w = self.w_var.get()
        self.edges_text.delete("1.0", tk.END)
        self.targets_entry.delete(0, tk.END)
        if w:
            self.matrix_title.config(text="Таблица длин")
            self.graph_label.config(text="Рёбра: A-B 15")
            self.edges_text.insert("1.0", "А-Б 13\nА-В 7\nБ-В 6\nБ-Г 15\nВ-Д 10\nГ-Е 5\nД-Е 8\nД-Ж 9\nЕ-Ж 11")
            self.targets_entry.insert(0, "Г, Д")
        else:
            self.matrix_title.config(text="Таблица связей")
            self.graph_label.config(text="Рёбра: A-B")
            self.edges_text.insert("1.0", "А-Б\nБ-В\nБ-Г\nВ-Г\nГ-Д\nД-Е")
            self.targets_entry.insert(0, "А, Е")

        self.generate_matrix_grid()
        self.draw_graph()

    def generate_matrix_grid(self):
        try:
            n = int(self.spin.get())
        except ValueError:
            return
        self.dimension = n
        for w in self.matrix_frame.winfo_children():
            w.destroy()

        self.matrix_widgets = [[None] * n for _ in range(n)]
        weighted = self.w_var.get()
        vcmd = (self.register(lambda p: p.isdigit() or p == ""), "%P")

        for i in range(n + 1):
            self.matrix_frame.grid_columnconfigure(i, weight=1, minsize=34)
            self.matrix_frame.grid_rowconfigure(i, weight=1)
            for j in range(n + 1):
                if i == 0 and j == 0:
                    continue
                if i == 0:
                    ttk.Label(self.matrix_frame, text=f"П{j}", font=self.f_lbl, anchor="center").grid(row=i, column=j, sticky="nsew")
                elif j == 0:
                    ttk.Label(self.matrix_frame, text=f"П{i}", font=self.f_lbl, anchor="center").grid(row=i, column=j, sticky="nsew")
                else:
                    r, c = i - 1, j - 1
                    if r == c:
                        ttk.Frame(self.matrix_frame).grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
                    elif weighted:
                        e = ttk.Entry(self.matrix_frame, justify="center", validate="key", validatecommand=vcmd, width=4)
                        e.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
                        e.bind("<KeyRelease>", lambda ev, a=r, b=c: self._sync_e(a, b))
                        if c < r:
                            e.config(state=tk.DISABLED)
                        self.matrix_widgets[r][c] = e
                    else:
                        v = tk.BooleanVar()
                        cb = ttk.Checkbutton(self.matrix_frame, variable=v, command=lambda a=r, b=c: self._sync_c(a, b))
                        if c < r:
                            cb.config(state=tk.DISABLED)
                        cb.grid(row=i, column=j, sticky="nsew")
                        self.matrix_widgets[r][c] = v

    def _sync_e(self, r, c):
        s = self.matrix_widgets[r][c]
        t = self.matrix_widgets[c][r]
        t.config(state=tk.NORMAL)
        t.delete(0, tk.END)
        t.insert(0, s.get())
        t.config(state=tk.DISABLED)

    def _sync_c(self, r, c):
        self.matrix_widgets[c][r].set(self.matrix_widgets[r][c].get())

    def _parse_for_draw(self):
        adj = collections.defaultdict(list)
        nodes = set()
        weights = {}
        w = self.w_var.get()
        seen = set()
        txt = self.edges_text.get("1.0", tk.END)

        for raw in txt.strip().splitlines():
            line = raw.strip().upper()
            if not line:
                continue
            line = line.replace("—", "-").replace("–", "-").replace("−", "-")
            line = re.sub(r"[;,]", " ", line)
            parts = [p for p in re.split(r"\s+|-", line) if p]

            if len(parts) == 1:
                nodes.add(parts[0])
                adj.setdefault(parts[0], [])
                continue

            if w:
                if len(parts) >= 3 and parts[-1].isdigit():
                    u, v, wt = parts[0], parts[1], parts[-1]
                    k = tuple(sorted((u, v)))
                    if k in seen:
                        continue
                    seen.add(k)
                    adj[u].append(v)
                    adj[v].append(u)
                    nodes |= {u, v}
                    weights[k] = wt
            else:
                if len(parts) >= 2:
                    u, v = parts[0], parts[1]
                    k = tuple(sorted((u, v)))
                    if k in seen:
                        continue
                    seen.add(k)
                    adj[u].append(v)
                    adj[v].append(u)
                    nodes |= {u, v}

        for n in nodes:
            adj.setdefault(n, [])

        return adj, sorted(nodes), weights

    def _layout(self, adj, nodes, w, h):
        if not nodes:
            return {}
        pos = {n: (random.uniform(40, w - 40), random.uniform(40, h - 40)) for n in nodes}
        area = w * h
        k = 0.9 * math.sqrt(area / max(1, len(nodes)))
        t = w / 12
        for _ in range(80):
            disp = {n: [0.0, 0.0] for n in nodes}
            for u in nodes:
                for v in nodes:
                    if u == v:
                        continue
                    dx = pos[u][0] - pos[v][0]
                    dy = pos[u][1] - pos[v][1]
                    d = math.hypot(dx, dy) + 1e-4
                    f = k * k / d
                    disp[u][0] += dx / d * f
                    disp[u][1] += dy / d * f
            edges = {(min(u, v), max(u, v)) for u in nodes for v in adj[u] if u < v}
            for u, v in edges:
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                d = math.hypot(dx, dy) + 1e-4
                f = d * d / k
                disp[u][0] -= dx / d * f
                disp[u][1] -= dy / d * f
                disp[v][0] += dx / d * f
                disp[v][1] += dy / d * f
            for n in nodes:
                dx, dy = disp[n]
                d = math.hypot(dx, dy) + 1e-4
                pos[n] = (
                    max(40, min(w - 40, pos[n][0] + dx / d * min(d, t))),
                    max(40, min(h - 40, pos[n][1] + dy / d * min(d, t))),
                )
            t *= 0.98
        return pos

    def draw_graph(self):
        self.canvas.delete("all")
        adj, nodes, weights = self._parse_for_draw()
        if not nodes:
            return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 50 or h < 50:
            self.master.after(50, self.draw_graph)
            return
        self.node_positions = self._layout(adj, nodes, w, h)

        drawn = set()
        for u, vs in adj.items():
            for v in vs:
                k = tuple(sorted((u, v)))
                if k in drawn:
                    continue
                drawn.add(k)
                p1, p2 = self.node_positions[u], self.node_positions[v]
                self.canvas.create_line(p1, p2, fill="#98a2b3", width=2)
                if k in weights:
                    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
                    tid = self.canvas.create_text(mx, my, text=weights[k], fill="#175cd3", font=("Segoe UI", 10, "bold"))
                    r = self.canvas.bbox(tid)
                    self.canvas.tag_lower(self.canvas.create_rectangle(r, fill="white", outline="white"), tid)

        for n, (x, y) in self.node_positions.items():
            self.canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill="#d1e9ff", outline="#175cd3", width=2)
            self.canvas.create_text(x, y, text=n, font=("Segoe UI", 12, "bold"), fill="#101828")

    def solve_problem(self):
        w = self.w_var.get()
        rows = []
        for r in range(self.dimension):
            if w:
                row = ["0" if r == c else (self.matrix_widgets[r][c].get() or "0") for c in range(self.dimension)]
            else:
                row = ["0" if r == c else ("1" if self.matrix_widgets[r][c].get() else "0") for c in range(self.dimension)]
            rows.append(" ".join(row))

        m = "\n".join(rows)
        e = self.edges_text.get("1.0", tk.END)
        t = self.targets_entry.get()

        if not m.strip() or not e.strip() or not t.strip():
            self._set_result("Заполните все поля!", True)
            return

        res = backend.solve(m, e, t, w)
        bad = any(x in res.lower() for x in ("ошибка", "не удалось", "не найден"))
        self._set_result(f"Ответ: {res}" if not bad else res, bad)

    def _set_result(self, text, is_err):
        fg, bg = (self.c["err"], self.c["err_bg"]) if is_err else (self.c["ok"], self.c["ok_bg"])
        self.result_label.config(text=text, foreground=fg, background=bg)


if __name__ == "__main__":
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    App(root)
    root.mainloop()
