"""
Qt helpers
"""

from PyQt5 import QtWidgets, QtCore, QtGui


class EditCardDialog(QtWidgets.QDialog):
    def __init__(self, old_answer="", old_hint="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Card Details")

        # Layout and Form
        layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()

        self.answer_input = QtWidgets.QLineEdit(old_answer)
        self.hint_input = QtWidgets.QLineEdit(old_hint)

        form_layout.addRow("Answer:", self.answer_input)
        form_layout.addRow("Hint:", self.hint_input)
        layout.addLayout(form_layout)

        # Standard OK/Cancel Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self):
        return self.answer_input.text().strip(), self.hint_input.text().strip()


class MainWindowAbstract(QtWidgets.QMainWindow):
    TITLE = None
    STYLE_SHEET = None

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._set_style_sheet()
        self.setWindowTitle(self.TITLE)

        self.init_ui()
        self._set_up_socket_connections()

    def _set_style_sheet(self):
        """set the style sheet"""
        if self.STYLE_SHEET is None:
            return

        file = QtCore.QFile(self.STYLE_SHEET)
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        self.setStyleSheet(stream.readAll())

    def init_ui(self):
        return NotImplemented

    def _set_up_socket_connections(self):
        return NotImplemented

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
