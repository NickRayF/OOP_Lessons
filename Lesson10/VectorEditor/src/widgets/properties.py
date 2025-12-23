from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QColorDialog
from src.logic.commands import ChangeColorCommand, ChangeWidthCommand

class PropertiesPanel(QWidget):
    def __init__(self, scene, undo_stack):
        super().__init__()
        self.scene = scene
        self.undo_stack = undo_stack
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Width:"))
        self.spin_w = QSpinBox()
        self.spin_w.setRange(1, 20)
        self.spin_w.valueChanged.connect(self.on_width_changed)
        layout.addWidget(self.spin_w)
        
        layout.addWidget(QLabel("Color:"))
        self.btn_col = QPushButton("Pick")
        self.btn_col.clicked.connect(self.on_color_clicked)
        layout.addWidget(self.btn_col)
        
        layout.addStretch()
        self.scene.selectionChanged.connect(self.on_sel_changed)

    def on_sel_changed(self):
        sel = self.scene.selectedItems()
        if not sel:
            self.setEnabled(False)
            return
        self.setEnabled(True)
        item = sel[0]
        
        self.blockSignals(True)
        if hasattr(item, "pen"):
            self.spin_w.setValue(item.pen().width())
            c = item.pen().color().name()
            self.btn_col.setStyleSheet(f"background-color: {c}")
        self.blockSignals(False)

    def on_width_changed(self, val):
        sel = self.scene.selectedItems()
        if sel:
            self.undo_stack.beginMacro("Change Width")
            for item in sel:
                self.undo_stack.push(ChangeWidthCommand(item, val))
            self.undo_stack.endMacro()
            self.scene.update()

    def on_color_clicked(self):
        c = QColorDialog.getColor()
        if c.isValid():
            sel = self.scene.selectedItems()
            if sel:
                self.undo_stack.beginMacro("Change Color")
                for item in sel:
                    self.undo_stack.push(ChangeColorCommand(item, c.name()))
                self.undo_stack.endMacro()
                self.scene.update()