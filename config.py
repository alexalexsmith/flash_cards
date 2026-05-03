import os

REPO_PATH = os.path.dirname(os.path.abspath(__file__))
CARDS = f"{REPO_PATH}/cards"
SOUNDS = f"{REPO_PATH}/resources/sound"
STYLE_SHEETS = f"{REPO_PATH}/resources/style_sheets"

#  Try to make the CARDS directory if it doesn't exist
try:
    if not os.path.exists(CARDS):
        os.makedirs(CARDS)
except Exception as e:
    raise e
