import random

from PyQt5.QtMultimedia import QSoundEffect
from PyQt5 import QtWidgets, QtGui, QtCore

from utilities import card_utils, file_utils, qt_utils
from config import STYLE_SHEETS


class FlashCardsUI(qt_utils.MainWindowAbstract):
    TITLE = "Flash Cards"
    STYLE_SHEET = f"{STYLE_SHEETS}/dark_mode.qss"

    def __init__(self):
        super().__init__()
        self.cards = []
        self.pending_uploads = []
        self.session_mistakes = []
        self.study_mode = "STUDY"  # STUDY, RECAP, PRACTICE
        self.current_index = 0
        self.is_adding_new = False
        self.current_card = None

        self._init_sounds()
        self.shuffle_cards()
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
        # TODO: all string labels should be retrieved from a language settings file. along with errors and user messages
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

        # Study session settings
        study_session_group = QtWidgets.QGroupBox("Study Session Settings")
        study_session_layout = QtWidgets.QVBoxLayout()
        study_session_btns_layout = QtWidgets.QHBoxLayout()
        study_session_options_layout = QtWidgets.QHBoxLayout()
        self.spin_card_count = QtWidgets.QSpinBox()
        self.spin_card_count.setRange(0, 999)
        self.spin_card_count.setValue(20)
        self.spin_min = QtWidgets.QSpinBox()
        self.spin_min.setRange(0, 999)
        self.spin_max = QtWidgets.QSpinBox()
        self.spin_max.setRange(0, 999)
        self.spin_max.setValue(0)
        self.chckbx_practice_mode = QtWidgets.QCheckBox("Practice Mode")
        self.btn_shuffle_cards = QtWidgets.QPushButton("Shuffle Cards")
        self.btn_do_recap = QtWidgets.QPushButton("Do Session Mistake Recap")

        study_session_options_layout.addWidget(QtWidgets.QLabel("Cards:"))
        study_session_options_layout.addWidget(self.spin_card_count)
        study_session_options_layout.addWidget(QtWidgets.QLabel("Recall Min:"))
        study_session_options_layout.addWidget(self.spin_min)
        study_session_options_layout.addWidget(QtWidgets.QLabel("Recall Max:"))
        study_session_options_layout.addWidget(self.spin_max)
        study_session_options_layout.addWidget(self.chckbx_practice_mode)

        study_session_btns_layout.addWidget(self.btn_shuffle_cards)
        study_session_btns_layout.addWidget(self.btn_do_recap)

        study_session_layout.addLayout(study_session_options_layout)
        study_session_layout.addLayout(study_session_btns_layout)

        study_session_group.setLayout(study_session_layout)
        self.layout.addWidget(study_session_group)

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
        self.spelling_hint_label = QtWidgets.QLabel("")
        self.spelling_hint_label.setObjectName("spelling_hint_label")
        self.spelling_hint_label.setAlignment(QtCore.Qt.AlignCenter)
        self.spelling_hint_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Change cursor to hand
        self.spelling_hint_label.mousePressEvent = self.copy_hint_to_clipboard
        self.spelling_hint_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.spelling_hint_label)

        # Hint Area
        self.hint_label = QtWidgets.QLabel("")
        self.hint_label.setAlignment(QtCore.Qt.AlignCenter)
        self.hint_label.setStyleSheet("font-size: 18px; color: #2980b9; font-style: italic;")
        self.hint_label.hide()  # Hidden by default
        self.layout.addWidget(self.hint_label)

        self.btn_reveal_hint = QtWidgets.QPushButton("Reveal Hint")
        self.layout.addWidget(self.btn_reveal_hint)

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
        self.chckbx_practice_mode.toggled.connect(self._callback_practice_mode_state_changed)
        self.btn_shuffle_cards.clicked.connect(self.shuffle_cards)
        self.btn_do_recap.clicked.connect(self.load_session_recap)
        self.btn_reveal_hint.clicked.connect(self.toggle_hint)
        self.entry.returnPressed.connect(self.handle_submit)
        self.btn_confirm.clicked.connect(self.handle_submit)
        self.btn_skip.clicked.connect(self.skip_image)
        self.btn_edit.clicked.connect(self.edit_current_card)
        self.btn_delete.clicked.connect(self.delete_current_card)

    def shuffle_cards(self):
        # Make sure practice mode checkbox is enabled on new shuffle
        self.chckbx_practice_mode.setEnabled(True)
        self.study_mode = "STUDY"
        if self.chckbx_practice_mode.isChecked():
            self.study_mode = "PRACTICE"
        self.cards = card_utils.get_flash_cards(
            self.spin_min.value(),
            self.spin_max.value(),
            self.spin_card_count.value())
        self.current_index = 0
        if not self.is_adding_new:
            self.load_next()

    def load_session_recap(self):
        """Load all mistakes into a recap session"""
        self.study_mode = "RECAP"
        # In recap mode you can't use practice mode
        self.chckbx_practice_mode.setEnabled(False)
        self.cards = self.session_mistakes
        # Flush the session_mistakes
        self.session_mistakes = []
        self.current_index = 0
        if not self.is_adding_new:
            self.load_next()

    def _callback_practice_mode_state_changed(self):
        """ui actions when practice mode toggled"""
        if self.chckbx_practice_mode.isChecked():
            self.study_mode = "PRACTICE"
            self.mode_label.setText(f"MODE: {self.study_mode}")
            self.update_spelling_hint()
        else:
            self.study_mode = "STUDY"
            self.mode_label.setText(f"MODE: {self.study_mode}")
            self.update_spelling_hint()

    def copy_hint_to_clipboard(self, event):
        """Copies the current Korean word to the clipboard when the hint is clicked."""
        if not self.current_card:
            return

        word_to_copy = self.current_card.answer

        # Access the system clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(word_to_copy)

        # Optional: Provide a tiny visual feedback (changing the label text briefly)
        original_hint = self.spelling_hint_label.text()
        self.spelling_hint_label.setText("COPIED!")
        self.spelling_hint_label.setStyleSheet("color: #a6e3a1;")  # Temporary green color

        # Reset the text after 1 second
        QtCore.QTimer.singleShot(1000, lambda: self._reset_hint_style(original_hint))

    def _reset_hint_style(self, original_text):
        self.spelling_hint_label.setText(original_text)
        self.spelling_hint_label.setStyleSheet("")

    def update_spelling_hint(self):
        word = self.current_card.answer
        hint = ""
        for char in word:
            if char == " ":
                hint += "  "
            else:
                hint += "_ "
        # In practice mode the answer is displayed
        if self.study_mode == "PRACTICE":
            hint = word
        self.spelling_hint_label.setText(hint.strip())

    def toggle_hint(self):
        """Shows/Hides the Hint."""
        if self.hint_label.isHidden():
            hint = self.current_card.hint
            self.hint_label.setText(hint)
            self.hint_label.show()
            self.btn_reveal_hint.setText("Hide Hint")
        else:
            self.hint_label.hide()
            self.btn_reveal_hint.setText("Reveal Hint")

    def load_next(self):
        # Case 1: Processing new drops
        if self.pending_uploads:
            self.is_adding_new = True
            self.mode_label.setText("MODE: ADDING NEW CARD")
            self.mode_label.setStyleSheet("font-weight: bold; color: green;")
            self.btn_confirm.setText("Save New Card")
            self.hint_label.setText("[Type translation to save]")
            self.stats_label.setText(f"Cards Left: {len(self.pending_uploads)}")
            self.display_image(self.pending_uploads[0])
            self.entry.clear()
            self.entry.setFocus()
            self.save_new_card()
            return

        # Case 2: Normal Study Mode
        self.is_adding_new = False
        self.mode_label.setText(f"MODE: {self.study_mode}")
        self.mode_label.setStyleSheet("font-weight: bold; color: #cdd6f4;")
        self.btn_confirm.setText("Confirm Answer")

        # Reset Hint UI for every new card
        self.hint_label.hide()
        self.btn_reveal_hint.setText("Reveal Hint")
        self.btn_reveal_hint.setVisible(not self.is_adding_new)  # Don't show hint when adding cards

        if self.current_index < len(self.cards):
            self.img_label.setStyleSheet("border: none;")
            self.current_card = self.cards[self.current_index]
            self.display_image(self.current_card.image_path())

            self.stats_label.setText(f"Cards Left: {len(self.cards) - self.current_index}")
            self.update_spelling_hint()

            self.entry.clear()
            self.entry.setFocus()
        else:
            # TODO: make this it's own function
            self._display_image_label_border(True)
            self.hint_label.setText("")
            self.stats_label.setText("")

    def _display_image_label_border(self, display):
        """
        Display the image label dashed border
        :param bool display: option to display or hide dashed border
        :return:
        """
        if display:
            self.img_label.setStyleSheet("border: 3px dashed gray;")
            self.img_label.clear()
            self.img_label.setText("Session Finished. Drag new images or shuffle cards.")
        else:
            self.img_label.setStyleSheet("border: none;")

    def display_image(self, path):
        # Use Pillow to check for EXIF rotation
        rotation = file_utils.get_image_rotation(path)

        # 2. Load into QPixmap
        pixmap = QtGui.QPixmap(path)

        if not pixmap.isNull():
            # 3. Apply rotation if needed
            if rotation != 0:
                transform = QtGui.QTransform()
                transform.rotate(rotation)
                pixmap = pixmap.transformed(transform, QtCore.Qt.SmoothTransformation)

            scaled = pixmap.scaled(
                self.img_label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled)
        else:
            self.img_label.clear()


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
                self.shuffle_cards()
            self.load_next()
            return

        dialog = qt_utils.EditCardDialog(parent=self)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            answer, hint = dialog.get_values()

            if not answer:
                QtWidgets.QMessageBox.warning(self, "Error", "Answer cannot be empty.")
                # We return without popping, so the user can click 'Save' again
                # and the same image will still be there.
                return

            try:
                file_utils.save_new_card(src_path, answer, hint)
                self.pending_uploads.pop(0)  # Success! Remove from queue.
            except FileExistsError as e:
                QtWidgets.QMessageBox.warning(self, "Skipped", str(e))
                self.pending_uploads.pop(0)  # Duplicate! Skip it.
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save: {e}")
                # Keep in queue so we don't lose the image reference on a random crash.

            # Check if we need to go back to Study Mode or load the next pending item
            if not self.pending_uploads:
                self.shuffle_cards()
            self.load_next()

    def check_answer(self):
        if not self.cards: return
        user_input = self.entry.text().strip()
        correct_word = self.current_card.answer
        next_card_index = 1
        if user_input == correct_word:
            random.choice(self.correct_sounds).play()
            if self.study_mode == "STUDY":
                self.current_card.recall += 1
            QtWidgets.QMessageBox.information(self, "Correct!", f"answer: {correct_word}")
        else:
            random.choice(self.incorrect_sounds).play()
            if self.study_mode == "STUDY":
                self.current_card.recall = max(0, self.current_card.recall - 1)
            QtWidgets.QMessageBox.critical(self, "Wrong", f"The answer was: {correct_word}")

            # add card to session mistake storage
            if self.study_mode == "STUDY":
                self.session_mistakes.append(self.cards[self.current_index])

            # stay on this card if we are in recap mode
            if self.study_mode == "RECAP":
                next_card_index = 0

        # Only update data if we are in study mode
        if self.study_mode == "STUDY":
            self.current_card.update_card()

        self.current_index += next_card_index
        self.load_next()

    def edit_current_card(self):
        if self.is_adding_new or not self.cards:
            return

            # Initialize the custom dialog with existing data
        dialog = qt_utils.EditCardDialog(
            old_answer=self.current_card.answer,
            old_hint=self.current_card.hint,
            parent=self
        )

        # Executing the dialog (returns True if OK was clicked)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_answer, new_hint = dialog.get_values()

            # Validate that the answer isn't empty
            if not new_answer:
                QtWidgets.QMessageBox.warning(self, "Error", "Answer cannot be empty.")
                return

            # Update the Card object
            self.current_card.answer = new_answer
            self.current_card.hint = new_hint

            # Update the UI visuals
            self.update_spelling_hint()
            if not self.hint_label.isHidden():
                self.hint_label.setText(new_hint)

            # Save card updates to disk
            self.current_card.update_card()

    def skip_image(self):
        if self.is_adding_new:
            self.pending_uploads.pop(0)
        else:
            self.current_index += 1
        self.load_next()

    def delete_current_card(self):
        if self.is_adding_new or not self.cards: return
        reply = QtWidgets.QMessageBox.question(self, 'Delete', "Delete this card forever?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.current_card.delete()
            self.cards.pop(self.current_index)
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
        if hasattr(self, 'files') and self.cards and not self.is_adding_new:
            self.display_image(self.current_card.image_path())
        elif self.pending_uploads:
            self.display_image(self.pending_uploads[0])
