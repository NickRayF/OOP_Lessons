import tkinter as tk

class SimplePoints:
    def __init__(self):
        self.points = [
            (100, 50), (200, 10), (80, 200), 
            (100, 250), (300, 50), (250, 250)
        ]
        self.selected = None
        self.lines = {}
        self.dragging = None
    
    def setup(self, canvas):
        self.canvas = canvas
        for i, (x, y) in enumerate(self.points):
            point_id = i + 1
            canvas.create_oval(x-6, y-6, x+6, y+6, fill="blue", tags=f"point_{point_id}")
            canvas.create_text(x+15, y, text=str(point_id), tags=f"text_{point_id}")
            
            canvas.tag_bind(f"point_{point_id}", "<Button-1>", lambda e, pid=point_id: self.point_click(pid))
            canvas.tag_bind(f"point_{point_id}", "<B1-Motion>", lambda e, pid=point_id: self.drag_point(e, pid))
            canvas.tag_bind(f"point_{point_id}", "<ButtonRelease-1>", lambda e: self.stop_drag())
        
        # Привязываем правый клик для удаления линий
        canvas.bind("<Button-3>", self.delete_line)
    
    def point_click(self, point_id):
        if self.dragging:
            return
            
        if self.selected is None:
            self.selected = point_id
            self.canvas.itemconfig(f"point_{self.selected}", fill="red")
        else:
            if self.selected != point_id:
                self.create_line(self.selected, point_id)
            self.canvas.itemconfig(f"point_{self.selected}", fill="blue")
            self.selected = None
    
    def create_line(self, id1, id2):
        line_key = tuple(sorted((id1, id2)))
        
        if line_key not in self.lines:
            x1, y1 = self.points[id1-1]
            x2, y2 = self.points[id2-1]
            line_id = self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2, tags="line")
            self.lines[line_key] = line_id
    
    def drag_point(self, event, point_id):
        self.dragging = point_id
        self.canvas.itemconfig(f"point_{point_id}", fill="green")
        
        self.points[point_id-1] = (event.x, event.y)
        
        self.canvas.coords(f"point_{point_id}", event.x-6, event.y-6, event.x+6, event.y+6)
        self.canvas.coords(f"text_{point_id}", event.x+15, event.y)
        
        self.update_lines(point_id)
    
    def stop_drag(self):
        if self.dragging:
            self.canvas.itemconfig(f"point_{self.dragging}", fill="blue")
            self.dragging = None
    
    def update_lines(self, point_id):
        for (id1, id2), line_id in self.lines.items():
            if point_id in (id1, id2):
                x1, y1 = self.points[id1-1]
                x2, y2 = self.points[id2-1]
                self.canvas.coords(line_id, x1, y1, x2, y2)
    
    def delete_line(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        
        if "line" in tags:
            self.canvas.delete(item)
            
            for key, line_id in list(self.lines.items()):
                if line_id == item:
                    del self.lines[key]
                    break

def main():
    root = tk.Tk()
    root.title("Точки - Перемещение и удаление")
    
    canvas = tk.Canvas(root, width=400, height=300, bg="white")
    canvas.pack()
    
    # Добавляем подсказку
    label = tk.Label(root, text="ЛКМ: соединять точки | ПКМ: удалять линии | Перетаскивание: двигать точки")
    label.pack()
    
    app = SimplePoints()
    app.setup(canvas)
    
    root.mainloop()

if __name__ == "__main__":
    main()