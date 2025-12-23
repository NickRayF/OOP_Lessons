from PySide6.QtGui import QUndoCommand

class AddShapeCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        self.setText("Add Shape")

    def redo(self):
        if self.item.scene() != self.scene:
            self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class DeleteCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        self.setText("Delete Shape")

    def redo(self):
        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)

class MoveCommand(QUndoCommand):
    def __init__(self, item, old_pos, new_pos):
        super().__init__()
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
        self.setText("Move Shape")

    def undo(self):
        self.item.setPos(self.old_pos)
    
    def redo(self):
        self.item.setPos(self.new_pos)

class ChangeColorCommand(QUndoCommand):
    def __init__(self, item, new_color):
        super().__init__()
        self.item = item
        self.new_color = new_color
        self.old_color = item.pen().color().name() if hasattr(item, "pen") else "#000000"
        self.setText("Change Color")

    def redo(self):
        if hasattr(self.item, "set_active_color"):
            self.item.set_active_color(self.new_color)

    def undo(self):
        if hasattr(self.item, "set_active_color"):
            self.item.set_active_color(self.old_color)

class ChangeWidthCommand(QUndoCommand):
    def __init__(self, item, new_width):
        super().__init__()
        self.item = item
        self.new_width = new_width
        self.old_width = item.pen().width() if hasattr(item, "pen") else 1
        self.setText("Change Width")

    def redo(self):
        if hasattr(self.item, "set_stroke_width"):
            self.item.set_stroke_width(self.new_width)

    def undo(self):
        if hasattr(self.item, "set_stroke_width"):
            self.item.set_stroke_width(self.old_width)