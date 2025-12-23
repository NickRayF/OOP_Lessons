
import sys
from PySide6 import QtWidgets, QtCore
import backend


def _int(s: str, default: int = 0) -> int:
    try:
        return int(s.strip())
    except Exception:
        return default


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЕГЭ Информатика №15 — решатель (перебор A)")
        self.resize(1100, 760)

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        layout = QtWidgets.QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        top = QtWidgets.QHBoxLayout()
        self.expr = QtWidgets.QPlainTextEdit()
        self.expr.setPlaceholderText(
            "Введите формулу в стиле Python.\n"
            "Примеры:\n"
            "((x & A) != 0) <= ((x & 36) != 0)\n"
            "(div(x,2) <= (div(x,3))) or (x < A)\n"
            "between(x, 10, 20) <= (x in_seg(A, 30, 60))  (используй between/in_seg)\n\n"
            "Функции: div(a,b), between(x,l,r), in_seg(x,l,r), in_int(x,l,r), abs, min, max\n"
            "Операторы: and/or/not, сравнения, + - * // % **, битовые &,|,^,~,<<,>>"
        )
        self.expr.setPlainText("((x & A) != 0) <= ((x & 36) != 0)")
        top.addWidget(self.expr, 2)

        side = QtWidgets.QVBoxLayout()

        cfg_box = QtWidgets.QGroupBox("Параметры")
        cfg_l = QtWidgets.QFormLayout(cfg_box)
        cfg_l.setHorizontalSpacing(10)
        cfg_l.setVerticalSpacing(8)

        self.cb_obj = QtWidgets.QComboBox()
        self.cb_obj.addItems(["min", "max", "all"])
        self.cb_obj.setCurrentText("min")

        self.ed_A_from = QtWidgets.QLineEdit("0")
        self.ed_A_to = QtWidgets.QLineEdit("200")
        self.ed_A_step = QtWidgets.QLineEdit("1")

        cfg_l.addRow("Искать A:", self.cb_obj)
        cfg_l.addRow("A от:", self.ed_A_from)
        cfg_l.addRow("A до:", self.ed_A_to)
        cfg_l.addRow("A шаг:", self.ed_A_step)

        side.addWidget(cfg_box)

        q_box = QtWidgets.QGroupBox("Кванторы и диапазоны")
        q_l = QtWidgets.QGridLayout(q_box)
        q_l.setHorizontalSpacing(10)
        q_l.setVerticalSpacing(8)

        self.cb_qx = QtWidgets.QComboBox()
        self.cb_qx.addItems(["forall", "exists", "none"])
        self.cb_qx.setCurrentText("forall")
        self.x_from = QtWidgets.QLineEdit("0")
        self.x_to = QtWidgets.QLineEdit("200")
        self.x_step = QtWidgets.QLineEdit("1")

        self.cb_qy = QtWidgets.QComboBox()
        self.cb_qy.addItems(["forall", "exists", "none"])
        self.cb_qy.setCurrentText("none")
        self.y_from = QtWidgets.QLineEdit("0")
        self.y_to = QtWidgets.QLineEdit("200")
        self.y_step = QtWidgets.QLineEdit("1")

        q_l.addWidget(QtWidgets.QLabel("x:"), 0, 0)
        q_l.addWidget(self.cb_qx, 0, 1)
        q_l.addWidget(QtWidgets.QLabel("от"), 0, 2)
        q_l.addWidget(self.x_from, 0, 3)
        q_l.addWidget(QtWidgets.QLabel("до"), 0, 4)
        q_l.addWidget(self.x_to, 0, 5)
        q_l.addWidget(QtWidgets.QLabel("шаг"), 0, 6)
        q_l.addWidget(self.x_step, 0, 7)

        q_l.addWidget(QtWidgets.QLabel("y:"), 1, 0)
        q_l.addWidget(self.cb_qy, 1, 1)
        q_l.addWidget(QtWidgets.QLabel("от"), 1, 2)
        q_l.addWidget(self.y_from, 1, 3)
        q_l.addWidget(QtWidgets.QLabel("до"), 1, 4)
        q_l.addWidget(self.y_to, 1, 5)
        q_l.addWidget(QtWidgets.QLabel("шаг"), 1, 6)
        q_l.addWidget(self.y_step, 1, 7)

        side.addWidget(q_box)

        self.btn = QtWidgets.QPushButton("Решить")
        self.btn.setDefault(True)
        side.addWidget(self.btn)

        self.out = QtWidgets.QPlainTextEdit()
        self.out.setReadOnly(True)
        self.out.setMinimumHeight(140)
        side.addWidget(self.out, 1)

        side_w = QtWidgets.QWidget()
        side_w.setLayout(side)
        top.addWidget(side_w, 1)

        layout.addLayout(top, 1)

        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color:#b00020; font-weight:600;")
        layout.addWidget(self.status)

        self.btn.clicked.connect(self.on_solve)
        self.cb_qx.currentTextChanged.connect(self._sync_enable)
        self.cb_qy.currentTextChanged.connect(self._sync_enable)
        self._sync_enable()

    def _sync_enable(self):
        x_on = self.cb_qx.currentText() != "none"
        for w in (self.x_from, self.x_to, self.x_step):
            w.setEnabled(x_on)
        y_on = self.cb_qy.currentText() != "none"
        for w in (self.y_from, self.y_to, self.y_step):
            w.setEnabled(y_on)

    def on_solve(self):
        self.status.setText("")
        self.out.setPlainText("")
        try:
            expr = self.expr.toPlainText().strip()

            A_dom = backend.Domain(
                _int(self.ed_A_from.text(), 0),
                _int(self.ed_A_to.text(), 0),
                max(1, abs(_int(self.ed_A_step.text(), 1))),
            )

            qx_mode = self.cb_qx.currentText()
            qy_mode = self.cb_qy.currentText()

            qx = backend.Quant(qx_mode, None)
            qy = backend.Quant(qy_mode, None)

            if qx_mode != "none":
                qx.domain = backend.Domain(
                    _int(self.x_from.text(), 0),
                    _int(self.x_to.text(), 0),
                    max(1, abs(_int(self.x_step.text(), 1))),
                )
            if qy_mode != "none":
                qy.domain = backend.Domain(
                    _int(self.y_from.text(), 0),
                    _int(self.y_to.text(), 0),
                    max(1, abs(_int(self.y_step.text(), 1))),
                )

            cfg = backend.SolveConfig(
                expr=expr,
                ax=qx,
                ay=qy,
                a_domain=A_dom,
                objective=self.cb_obj.currentText(),
                a_name="A",
            )

            ans = backend.solve(cfg)
            if not ans:
                self.out.setPlainText("Подходящих A не найдено.")
            else:
                if cfg.objective == "all":
                    self.out.setPlainText("A:\n" + ", ".join(map(str, ans)))
                else:
                    self.out.setPlainText(f"A = {ans[0]}")
        except Exception as e:
            self.status.setText(str(e))


def main():
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
