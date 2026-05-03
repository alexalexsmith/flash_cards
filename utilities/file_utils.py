"""
File management utilities
"""
import os
import shutil
import random

from config import CARDS, SOUNDS
from utilities import json_utils


# NOTE: flash card file management

def get_card_file_list(min_score, max_score):
    """Filters images based on the score range and returns a shuffled list."""
    if not os.path.exists(CARDS):
        os.makedirs(CARDS)

    all_images = [f for f in os.listdir(CARDS) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    filtered_list = []

    for img_name in all_images:
        json_path = _get_json_path(img_name)
        score = 0
        if os.path.exists(json_path):
            data = json_utils.load_json(json_path)
            score = data.get('answered_correctly', 0)

        if min_score <= score <= max_score:
            filtered_list.append(img_name)

    random.shuffle(filtered_list)
    return filtered_list


def get_image_path(filename):
    """Returns the full path to an image file."""
    return os.path.join(CARDS, filename)


def get_card_data(filename):
    """Loads the JSON data associated with an image file."""
    json_path = _get_json_path(filename)
    if os.path.exists(json_path):
        return json_utils.load_json(json_path)
    # Return a default structure if the file is missing or new
    return {"word": "", "english": "", "answered_correctly": 0}


def update_card_data(filename, data):
    """Saves updated JSON data."""
    json_path = _get_json_path(filename)
    json_utils.save_json(json_path, data)


def card_exists(src_path):
    """check if the card already exists"""
    base_name = os.path.basename(src_path)
    dest_path = os.path.join(CARDS, base_name)

    if os.path.exists(dest_path):
        return True
    return False


def save_new_card(src_path, word, english=""):
    """Copies a new image to the folder and creates its JSON. Raises error if exists."""
    base_name = os.path.basename(src_path)
    dest_path = os.path.join(CARDS, base_name)

    if os.path.exists(dest_path):
        raise FileExistsError(f"The file '{base_name}' already exists in the cards folder.")

    # Copy file if it's not already in the target directory
    if os.path.abspath(src_path) != os.path.abspath(dest_path):
        shutil.copy2(src_path, dest_path)

        json_path = os.path.splitext(dest_path)[0] + ".json"
        json_utils.save_json(json_path, {
            "word": word,
            "english": english,
            "answered_correctly": 0
        })


def delete_card(filename):
    """Deletes both image and JSON files."""
    img_path = os.path.join(CARDS, filename)
    json_path = _get_json_path(filename)

    if os.path.exists(img_path):
        os.remove(img_path)
    if os.path.exists(json_path):
        os.remove(json_path)


def _get_json_path(filename):
    """Internal helper to get JSON path from image filename."""
    return os.path.splitext(os.path.join(CARDS, filename))[0] + ".json"


# NOTE: resource management
def get_sound_files(category):
    """return the sound file path"""
    sounds_directory = os.path.join(SOUNDS, category)
    sound_files = []
    for filename in os.listdir(sounds_directory):
        if filename.lower().endswith(".wav"):
            sound_files.append(os.path.abspath(os.path.join(sounds_directory, filename)))
    return sound_files
