import random

from PyQt5.QtMultimedia import QSoundEffect
from PyQt5 import QtWidgets, QtGui, QtCore

from utilities import file_utils, qt_utils
from config import STYLE_SHEETS


class FlashCardsUI(qt_utils.MainWindowAbstract):
    TITLE = "Flash Cards"
    STYLE_SHEET = f"{STYLE_SHEETS}/dark_mode.qss"

    def __init__(self):
        super().__init__()
        self.files = []
        self.pending_uploads = []
        self.current_index = 0
        self.is_adding_new = False
        self.current_data = {}

        self._init_sounds()
        self.refresh_file_list()
        self.load_next()

    def _init_sounds(self):
        """Initializes sound effects for feedback."""
        self.correct_sounds = []
        self.incorrect_sounds = []
        for path in file_utils.get_sound_files("correct"):
            effect = QSoundEffect(self)  # Parent ensures it isn't garbage collected
            effect.setSource(QtCore.QUrl.fromLocalFile(path))
            self.correct_sounds.append(effect)
        for path in file_utils.get_sound_files("incorrect"):
            effect = QSoundEffect(self)  # Parent ensures it isn't garbage collected
            effect.setSource(QtCore.QUrl.fromLocalFile(path))
            self.incorrect_sounds.append(effect)

    def init_ui(self):
        # Create a top-level layout for the QMainWindow itself (not the container)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.centralWidget().setMouseTracking(True)
        self.outer_layout = QtWidgets.QVBoxLayout(central_widget)
        self.outer_layout.setContentsMargins(10, 10, 10, 10)

        self.main_container = QtWidgets.QFrame()
        self.main_container.setObjectName("MainFrame")
        self.outer_layout.addWidget(self.main_container)

        # Rest of your layout (title bar, etc.) goes inside self.main_container
        self.layout = QtWidgets.QVBoxLayout(self.main_container)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Keep internal tight

        # Custom Title Bar Area
        self.title_bar = QtWidgets.QWidget()
        self.title_bar.setObjectName("TitleBar")
        self.title_layout = QtWidgets.QHBoxLayout(self.title_bar)

        self.title_label = QtWidgets.QLabel(self.TITLE)
        self.title_label.setObjectName("title_label")

        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.layout.addWidget(self.title_bar)

        # Score Range Filter UI
        filter_group = QtWidgets.QGroupBox("Study Range (Score)")
        filter_layout = QtWidgets.QHBoxLayout()
        self.spin_min = QtWidgets.QSpinBox()
        self.spin_min.setRange(0, 999)
        self.spin_max = QtWidgets.QSpinBox()
        self.spin_max.setRange(0, 999)
        self.spin_max.setValue(0)
        self.btn_apply_filter = QtWidgets.QPushButton("Apply Filter & Shuffle")

        filter_layout.addWidget(QtWidgets.QLabel("Min:"))
        filter_layout.addWidget(self.spin_min)
        filter_layout.addWidget(QtWidgets.QLabel("Max:"))
        filter_layout.addWidget(self.spin_max)
        filter_layout.addWidget(self.btn_apply_filter)
        filter_group.setLayout(filter_layout)
        self.layout.addWidget(filter_group)

        # Mode and Image
        self.mode_label = QtWidgets.QLabel("Mode: Study")
        self.mode_label.setAlignment(QtCore.Qt.AlignCenter)
        self.mode_label.setStyleSheet("font-weight: bold; color: blue;")
        self.layout.addWidget(self.mode_label)

        # image label container to add an offset dash border
        self.img_container = QtWidgets.QFrame()
        self.img_container.setObjectName("img_container")
        self.img_container_layout = QtWidgets.QVBoxLayout(self.img_container)
        # Add padding here - this is what "offsets" the dashed border inward
        self.img_container_layout.setContentsMargins(15, 15, 15, 15)
        self.img_label = QtWidgets.QLabel(self)
        self.img_label.setAlignment(QtCore.Qt.AlignCenter)
        self.img_label.setMinimumSize(370, 370)
        self.img_label.setObjectName("img_label")
        self.img_container_layout.addWidget(self.img_label)
        self.layout.addWidget(self.img_container)

        # Hint Area
        self.hint_label = QtWidgets.QLabel("")
        self.hint_label.setAlignment(QtCore.Qt.AlignCenter)
        self.hint_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #555; letter-spacing: 5px;")
        self.layout.addWidget(self.hint_label)

        # English Translation Area
        self.english_label = QtWidgets.QLabel("")
        self.english_label.setAlignment(QtCore.Qt.AlignCenter)
        self.english_label.setStyleSheet("font-size: 18px; color: #2980b9; font-style: italic;")
        self.english_label.hide()  # Hidden by default
        self.layout.addWidget(self.english_label)

        self.btn_reveal_english = QtWidgets.QPushButton("Reveal English")
        self.layout.addWidget(self.btn_reveal_english)

        # Input Area
        self.entry = QtWidgets.QLineEdit(self)
        self.entry.setFixedHeight(45)
        self.entry.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.entry)

        # Action Buttons
        self.btn_confirm = QtWidgets.QPushButton("Confirm Answer")
        self.btn_confirm.setFixedHeight(40)
        self.layout.addWidget(self.btn_confirm)

        # Management Buttons
        self.mgmt_layout = QtWidgets.QHBoxLayout()
        self.btn_skip = QtWidgets.QPushButton("Skip")
        self.btn_edit = QtWidgets.QPushButton("Edit Card")
        self.btn_delete = QtWidgets.QPushButton("Delete Card")
        self.btn_delete.setStyleSheet("background-color: #960005;")

        self.mgmt_layout.addWidget(self.btn_skip)
        self.mgmt_layout.addWidget(self.btn_edit)
        self.mgmt_layout.addWidget(self.btn_delete)
        self.layout.addLayout(self.mgmt_layout)

        self.stats_label = QtWidgets.QLabel("")
        self.stats_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.stats_label)

        self.resize(600, 850)

    def _set_up_socket_connections(self):
        self.btn_apply_filter.clicked.connect(self.refresh_file_list)
        self.btn_reveal_english.clicked.connect(self.toggle_english)
        self.entry.returnPressed.connect(self.handle_submit)
        self.btn_confirm.clicked.connect(self.handle_submit)
        self.btn_skip.clicked.connect(self.skip_image)
        self.btn_edit.clicked.connect(self.edit_current_word)
        self.btn_delete.clicked.connect(self.delete_current_card)

    def refresh_file_list(self):
        self.files = file_utils.get_card_file_list(self.spin_min.value(), self.spin_max.value())
        self.current_index = 0
        if not self.is_adding_new:
            self.load_next()

    def update_hint(self, word):
        hint = ""
        for char in word:
            if char == " ":
                hint += "  "
            else:
                hint += "_ "
        self.hint_label.setText(hint.strip())

    def toggle_english(self):
        """Shows/Hides the English translation."""
        if self.english_label.isHidden():
            translation = self.current_data.get('english', "No translation provided.")
            self.english_label.setText(translation)
            self.english_label.show()
            self.btn_reveal_english.setText("Hide English")
        else:
            self.english_label.hide()
            self.btn_reveal_english.setText("Reveal English")

    def load_next(self):
        # Case 1: Processing new drops
        if self.pending_uploads:
            self.is_adding_new = True
            self.mode_label.setText("MODE: ADDING NEW WORD")
            self.mode_label.setStyleSheet("font-weight: bold; color: green;")
            self.btn_confirm.setText("Save New Card")
            self.hint_label.setText("[Type translation to save]")
            self.display_image(self.pending_uploads[0])
            self.entry.clear()
            self.entry.setFocus()
            self.save_new_card()
            return

        # Case 2: Normal Study Mode
        self.is_adding_new = False
        self.mode_label.setText("MODE: STUDY")
        self.mode_label.setStyleSheet("font-weight: bold; color: #cdd6f4;")
        self.btn_confirm.setText("Confirm Answer")

        # Reset English UI for every new card
        self.english_label.hide()
        self.btn_reveal_english.setText("Reveal English")
        self.btn_reveal_english.setVisible(not self.is_adding_new)  # Only show in Study mode

        if self.current_index < len(self.files):
            self.img_label.setStyleSheet("border: none;")
            filename = self.files[self.current_index]
            img_path = file_utils.get_image_path(filename)
            self.display_image(img_path)

            self.current_data = file_utils.get_card_data(filename)
            self.stats_label.setText(f"Cards Left: {len(self.files) - self.current_index}")
            self.update_hint(self.current_data.get('word', ""))

            self.entry.clear()
            self.entry.setFocus()
        else:
            self.img_label.setStyleSheet("border: 3px dashed gray;")
            self.img_label.clear()
            self.hint_label.setText("")
            self.img_label.setText("Session Finished. Drag new images or adjust range.")
            self.stats_label.setText("")

    def display_image(self, path):
        pixmap = QtGui.QPixmap(path)
        if not pixmap.isNull():
            # Use the current size of the label to scale
            scaled = pixmap.scaled(
                self.img_label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled)

    def handle_submit(self):
        if self.is_adding_new:
            self.save_new_card()
        else:
            self.check_answer()

    def save_new_card(self):
        src_path = self.pending_uploads[0]
        if file_utils.card_exists(src_path):
            QtWidgets.QMessageBox.warning(self, "Skipped", "Card already exists")
            self.pending_uploads.pop(0)  # Duplicate! Skip it.
            # Check if we need to go back to Study Mode or load the next pending item
            if not self.pending_uploads:
                self.refresh_file_list()
            self.load_next()
            return

        dialog = qt_utils.EditCardDialog(parent=self)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            korean, english = dialog.get_values()

            if not korean:
                QtWidgets.QMessageBox.warning(self, "Error", "Korean word cannot be empty.")
                # We return without popping, so the user can click 'Save' again
                # and the same image will still be there.
                return

            try:
                file_utils.save_new_card(src_path, korean, english)
                self.pending_uploads.pop(0)  # Success! Remove from queue.
            except FileExistsError as e:
                QtWidgets.QMessageBox.warning(self, "Skipped", str(e))
                self.pending_uploads.pop(0)  # Duplicate! Skip it.
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save: {e}")
                # Keep in queue so we don't lose the image reference on a random crash.

            # Check if we need to go back to Study Mode or load the next pending item
            if not self.pending_uploads:
                self.refresh_file_list()
            self.load_next()

    def check_answer(self):
        if not self.files: return
        user_input = self.entry.text().strip()
        correct_word = self.current_data['word']

        if user_input == correct_word:
            random.choice(self.correct_sounds).play()
            self.current_data['answered_correctly'] += 1
            QtWidgets.QMessageBox.information(self, "Correct!", f"Word: {correct_word}")
        else:
            random.choice(self.incorrect_sounds).play()
            self.current_data['answered_correctly'] = max(0, self.current_data['answered_correctly'] - 1)
            QtWidgets.QMessageBox.critical(self, "Wrong", f"The word was: {correct_word}")

        file_utils.update_card_data(self.files[self.current_index], self.current_data)
        self.current_index += 1
        self.load_next()

    def edit_current_word(self):
        if self.is_adding_new or not self.files:
            return

            # Initialize the custom dialog with existing data
        dialog = qt_utils.EditCardDialog(
            old_korean=self.current_data.get('word', ""),
            old_english=self.current_data.get('english', ""),
            parent=self
        )

        # Executing the dialog (returns True if OK was clicked)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_korean, new_english = dialog.get_values()

            # Validate that the Korean word isn't empty
            if not new_korean:
                QtWidgets.QMessageBox.warning(self, "Error", "Korean word cannot be empty.")
                return

            # Update the data object
            self.current_data['word'] = new_korean
            self.current_data['english'] = new_english

            # Update the UI visuals
            self.update_hint(new_korean)
            if not self.english_label.isHidden():
                self.english_label.setText(new_english)

            # Save once to disk
            file_utils.update_card_data(self.files[self.current_index], self.current_data)

    def skip_image(self):
        if self.is_adding_new:
            self.pending_uploads.pop(0)
        else:
            self.current_index += 1
        self.load_next()

    def delete_current_card(self):
        if self.is_adding_new or not self.files: return
        reply = QtWidgets.QMessageBox.question(self, 'Delete', "Delete this card forever?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            file_utils.delete_card(self.files[self.current_index])
            self.files.pop(self.current_index)
            self.load_next()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        new_files = [u.toLocalFile() for u in urls if u.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg'))]
        if new_files:
            self.pending_uploads.extend(new_files)
            self.load_next()

    def resizeEvent(self, event):
        """Ensures the image rescales smoothly when the user resizes the window."""
        super().resizeEvent(event)
        # Re-trigger the image display logic to fit the new label size
        if hasattr(self, 'files') and self.files and not self.is_adding_new:
            filename = self.files[self.current_index]
            self.display_image(file_utils.get_image_path(filename))
        elif self.pending_uploads:
            self.display_image(self.pending_uploads[0])
