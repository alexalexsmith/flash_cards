import sys
import subprocess

# 1. Check for PyQt5 and offer to install if missing
try:
    from PyQt5 import QtWidgets, QtGui
except ImportError:
    print("PyQt5 not found. This is required to run the Flash Cards app.")
    choice = input("Would you like to install it now via pip? (y/n): ").lower()
    if choice == 'y':
        try:
            print("Installing PyQt5... please wait.")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
            from PyQt5 import QtWidgets, QtGui
            print("Installation successful!\n")
        except Exception as e:
            print(f"Failed to install PyQt5: {e}")
            sys.exit(1)
    else:
        print("PyQt5 is required to run this application. Exiting.")
        sys.exit(1)

from ui.flash_cards_ui import FlashCardsUI

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # 1. Define the Global Font
    # 'Malgun Gothic' is the standard for Windows.
    # Use 'AppleGothic' for macOS or 'NanumGothic' as a general fallback.
    global_font = QtGui.QFont("Malgun Gothic", 11)

    # 2. Apply it to the entire Application
    app.setFont(global_font)
    flash_cards_ui = FlashCardsUI()
    flash_cards_ui.show()
    sys.exit(app.exec_())
