"""
Qt helpers
"""

from PyQt5 import QtWidgets, QtCore


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
