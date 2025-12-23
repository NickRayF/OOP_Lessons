import tkinter as tk
from tkinter import ttk, messagebox
from backend import truth_table, filtered

def calc():
    expr = entry.get().strip()
    if not expr:
        messagebox.showwarning("Ошибка","Введи выражение")
        return
    try:
        vars_list, table = truth_table(expr)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
        return
    global VARS, TABLE
    VARS, TABLE = vars_list, table
    draw("all")

def draw(kind):
    if not TABLE: return
    data = filtered(TABLE, kind)
    tree.delete(*tree.get_children())
    cols = VARS + ["result"]
    tree["columns"] = cols
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=70)
    for r in data:
        v = [r[x] for x in VARS] + [int(r["result"])]
        tree.insert("", "end", values=v)

root = tk.Tk()
root.title("Полуавтомат таблицы истинности №2")
root.geometry("600x400")

VARS = []
TABLE = []

tk.Label(root, text="Логическое выражение:").pack()
entry = tk.Entry(root, width=40)
entry.pack()
entry.insert(0, "(x or not y) <= z")

tk.Button(root, text="Построить таблицу", command=calc).pack(pady=5)

frm = tk.Frame(root)
frm.pack()
tk.Button(frm, text="Все", command=lambda: draw("all")).grid(row=0,column=0,padx=3)
tk.Button(frm, text="True", command=lambda: draw("true")).grid(row=0,column=1,padx=3)
tk.Button(frm, text="False", command=lambda: draw("false")).grid(row=0,column=2,padx=3)

tree = ttk.Treeview(root, show="headings", height=12)
tree.pack(fill="both", expand=True, pady=10)

root.mainloop()