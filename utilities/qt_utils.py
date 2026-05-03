"""
Qt helpers
"""

from PyQt5 import QtWidgets, QtCore, QtGui

from config import STYLE_SHEETS


class EditCardDialog(QtWidgets.QDialog):
    def __init__(self, old_korean="", old_english="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Card Details")

        # Layout and Form
        layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()

        self.korean_input = QtWidgets.QLineEdit(old_korean)
        self.english_input = QtWidgets.QLineEdit(old_english)

        form_layout.addRow("Korean Word:", self.korean_input)
        form_layout.addRow("English Translation:", self.english_input)
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
        return self.korean_input.text().strip(), self.english_input.text().strip()


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
