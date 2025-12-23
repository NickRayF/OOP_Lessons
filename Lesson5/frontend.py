import tkinter as tk
from tkinter import ttk, messagebox
from backend import TruthTableCalculator

class ModernTruthTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Logic Master")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f5f5f5')
        
        self.calc = TruthTableCalculator()
        self.current_filter = 'all'
        self.edit_mode = False
        self.modified_data = None
        
        self.create_interface()

    def create_interface(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_table_tab()
        self.create_ege_tab()

    def create_table_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Таблицы истинности")
        
        left_frame = ttk.Frame(frame)
        left_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        right_frame = ttk.Frame(frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        self.create_input_section(left_frame)
        self.create_controls_section(left_frame)
        self.create_table_section(right_frame)

    def create_input_section(self, parent):
        ttk.Label(parent, text="Логическое выражение:").pack(anchor='w', pady=5)
        self.expr_entry = tk.Entry(parent, font=('Arial', 11), width=25)
        self.expr_entry.pack(fill='x', pady=5)
        self.expr_entry.insert(0, "(x and y) or not z")
        
        ttk.Button(parent, text="Вычислить", 
                  command=self.calculate_table).pack(fill='x', pady=10)

    def create_controls_section(self, parent):
        self.edit_var = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Режим редактирования", 
                       variable=self.edit_var, 
                       command=self.toggle_edit).pack(anchor='w', pady=5)
        
        ttk.Button(parent, text="Восстановить выражение",
                  command=self.reconstruct_expr).pack(fill='x', pady=5)
        
        ttk.Label(parent, text="Фильтры:").pack(anchor='w', pady=5)
        
        filters = [("Все", "all"), ("True", "true"), ("False", "false")]
        for text, filter_type in filters:
            ttk.Button(parent, text=text, width=15,
                      command=lambda f=filter_type: self.set_filter(f)).pack(fill='x', pady=2)

    def create_table_section(self, parent):
        self.table_tree = ttk.Treeview(parent, height=15, show='headings')
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.table_tree.yview)
        self.table_tree.configure(yscrollcommand=scrollbar.set)
        
        self.table_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.table_tree.bind("<Double-1>", self.edit_table_row)
        
        self.stats_label = ttk.Label(parent, text="Введите выражение")
        self.stats_label.pack(fill='x', pady=5)

    def create_ege_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Решатель ЕГЭ")
        
        left_frame = ttk.Frame(frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        self.create_ege_input_section(left_frame)
        self.create_ege_table_section(left_frame)
        self.create_ege_results_section(right_frame)

    def create_ege_input_section(self, parent):
        ttk.Label(parent, text="Выражение для ЕГЭ:").pack(anchor='w', pady=5)
        self.ege_expr_entry = tk.Entry(parent, font=('Arial', 11))
        self.ege_expr_entry.pack(fill='x', pady=5)
        self.ege_expr_entry.insert(0, "(x and not y) or (y == z)")
        
        ttk.Button(parent, text="Решить задачу", 
                  command=self.solve_ege).pack(fill='x', pady=10)

    def create_ege_table_section(self, parent):
        ttk.Label(parent, text="Таблица ЕГЭ:").pack(anchor='w', pady=5)
        
        self.ege_tree = ttk.Treeview(parent, height=8, show='headings', 
                                   columns=('F1', 'F2', 'F3', 'F4', 'Result'))
        for col in ('F1', 'F2', 'F3', 'F4', 'Result'):
            self.ege_tree.heading(col, text=col)
            self.ege_tree.column(col, width=60, anchor='center')
        
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.ege_tree.yview)
        self.ege_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ege_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.ege_tree.bind("<Double-1>", self.edit_ege_cell)
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Добавить строку", 
                  command=self.add_ege_row).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Удалить строку", 
                  command=self.remove_ege_row).pack(side='left', padx=2)

    def create_ege_results_section(self, parent):
        ttk.Label(parent, text="Результаты:").pack(anchor='w', pady=5)
        
        self.results_text = tk.Text(parent, height=15, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.results_text.insert("1.0", "Результаты появятся здесь...")

    def calculate_table(self):
        expr = self.expr_entry.get().strip()
        if not expr:
            messagebox.showwarning("Ошибка", "Введите выражение")
            return
        
        try:
            self.calc.calculate(expr)
            self.modified_data = None
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_table(self):
        for item in self.table_tree.get_children():
            self.table_tree.delete(item)
        
        data = self.modified_data or self.calc.generator.table_data
        if not data:
            return
        
        if self.current_filter == 'true':
            data = [r for r in data if r['result']]
        elif self.current_filter == 'false':
            data = [r for r in data if not r['result']]
        
        vars_list = self.calc.generator.variable_list
        self.table_tree['columns'] = vars_list + ['Result']
        
        for col in self.table_tree['columns']:
            self.table_tree.heading(col, text=col)
            self.table_tree.column(col, width=80, anchor='center')
        
        for row in data:
            values = [row[var] for var in vars_list] + [row['result']]
            self.table_tree.insert("", "end", values=values)
        
        self.update_stats()

    def update_stats(self):
        data = self.modified_data or self.calc.generator.table_data
        if not data:
            return
        
        true_count = sum(1 for r in data if r['result'])
        total = len(data)
        
        self.stats_label.config(text=f"Всего: {total} | True: {true_count} | False: {total-true_count}")

    def toggle_edit(self):
        self.edit_mode = self.edit_var.get()
        if not self.edit_mode:
            self.modified_data = None
            self.refresh_table()

    def edit_table_row(self, event):
        if not self.edit_mode:
            return
        
        selection = self.table_tree.selection()
        if not selection:
            return
        
        if not self.modified_data:
            self.modified_data = [r.copy() for r in self.calc.generator.table_data]
        
        selected_values = self.table_tree.item(selection[0])['values']
        vars_list = self.calc.generator.variable_list
        
        for data_row in self.modified_data:
            if all(str(data_row[var]) == str(selected_values[i]) for i, var in enumerate(vars_list)):
                data_row['result'] = not data_row['result']
                break
        
        self.refresh_table()

    def reconstruct_expr(self):
        if not self.modified_data:
            messagebox.showinfo("Инфо", "Нет изменений")
            return
        
        try:
            expr = self.calc.create_expression_from_table(self.modified_data)
            self.expr_entry.delete(0, tk.END)
            self.expr_entry.insert(0, expr)
            messagebox.showinfo("Успех", "Выражение восстановлено")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def set_filter(self, filter_type):
        self.current_filter = filter_type
        self.refresh_table()

    def solve_ege(self):
        expr = self.ege_expr_entry.get().strip()
        if not expr:
            messagebox.showwarning("Ошибка", "Введите выражение")
            return
        
        table_data = []
        for item in self.ege_tree.get_children():
            values = self.ege_tree.item(item)['values']
            if len(values) == 5:
                try:
                    row = {
                        'F1': int(values[0]) if values[0] else None,
                        'F2': int(values[1]) if values[1] else None,
                        'F3': int(values[2]) if values[2] else None,
                        'F4': int(values[3]) if values[3] else None,
                        'result': bool(int(values[4]))
                    }
                    table_data.append(row)
                except:
                    messagebox.showerror("Ошибка", "Проверьте данные таблицы")
                    return
        
        if not table_data:
            messagebox.showwarning("Ошибка", "Добавьте строки в таблицу")
            return
        
        try:
            solutions = self.calc.solve_ege_task(expr, table_data)
            self.results_text.delete("1.0", tk.END)
            
            if not solutions:
                self.results_text.insert("1.0", "Решений не найдено")
            else:
                self.results_text.insert("1.0", f"Найдено решений: {len(solutions)}\n\n")
                for i, sol in enumerate(solutions, 1):
                    self.results_text.insert(tk.END, f"{i}. {sol}\n")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_ege_row(self):
        self.ege_tree.insert("", "end", values=("", "", "", "", "0"))

    def remove_ege_row(self):
        selection = self.ege_tree.selection()
        if selection:
            self.ege_tree.delete(selection[0])

    def edit_ege_cell(self, event):
        selection = self.ege_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        col = self.ege_tree.identify_column(event.x)
        col_idx = int(col[1:]) - 1
        
        values = list(self.ege_tree.item(item)['values'])
        
        if 0 <= col_idx < 4:  
            current = values[col_idx]
            if current == "":
                new_value = "0"
            elif current == "0":
                new_value = "1"
            else:  
                new_value = ""
            values[col_idx] = new_value
        elif col_idx == 4: 
            current = values[col_idx]
            values[col_idx] = "1" if current == "0" else "0"
        
        self.ege_tree.item(item, values=values)


def main():
    root = tk.Tk()
    app = ModernTruthTableApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()