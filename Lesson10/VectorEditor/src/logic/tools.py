from abc import ABC, abstractmethod
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsView
from src.logic.factory import ShapeFactory
from src.logic.commands import AddShapeCommand, MoveCommand

class Tool(ABC):
    def __init__(self, view, undo_stack):
        self.view = view
        self.scene = view.scene
        self.undo_stack = undo_stack

    @abstractmethod
    def mouse_press(self, event): pass
    @abstractmethod
    def mouse_move(self, event): pass
    @abstractmethod
    def mouse_release(self, event): pass

class SelectionTool(Tool):
    def __init__(self, view, undo_stack):
        super().__init__(view, undo_stack)
        self.start_positions = {}

    def mouse_press(self, event):
        QGraphicsView.mousePressEvent(self.view, event)
        self.start_positions.clear()
        for item in self.scene.selectedItems():
            self.start_positions[item] = item.pos()

    def mouse_move(self, event):
        QGraphicsView.mouseMoveEvent(self.view, event)

    def mouse_release(self, event):
        QGraphicsView.mouseReleaseEvent(self.view, event)
        moved = []
        for item, old_pos in self.start_positions.items():
            if item.pos() != old_pos:
                moved.append((item, old_pos, item.pos()))
        
        if moved:
            self.undo_stack.beginMacro("Move Items")
            for item, old, new in moved:
                self.undo_stack.push(MoveCommand(item, old, new))
            self.undo_stack.endMacro()

class CreationTool(Tool):
    def __init__(self, view, shape_type, undo_stack):
        super().__init__(view, undo_stack)
        self.shape_type = shape_type
        self.start_pos = None
        self.temp_shape = None

    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = self.view.mapToScene(event.pos())
            self.temp_shape = ShapeFactory.create_shape(self.shape_type, self.start_pos, self.start_pos)
            self.scene.addItem(self.temp_shape)

    def mouse_move(self, event):
        if self.start_pos and self.temp_shape:
            curr_pos = self.view.mapToScene(event.pos())
            self.temp_shape.set_geometry(self.start_pos, curr_pos)

    def mouse_release(self, event):
        if self.start_pos and self.temp_shape:
            self.scene.removeItem(self.temp_shape)
            final_shape = ShapeFactory.create_shape(self.shape_type, self.start_pos, 
                                                  self.view.mapToScene(event.pos()))
            self.temp_shape = None
            self.start_pos = None
            
            cmd = AddShapeCommand(self.scene, final_shape)
            self.undo_stack.push(cmd)