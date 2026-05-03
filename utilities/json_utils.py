"""
json utils for importing and exporting .json files
"""
import json
import os


def save_json(file_path, data):
    """
    save json file with data
    :param str file_path: file_path to write
    :param dict data: dictionary formatted data to write into json file"""
    with open(file_path, 'w', encoding='utf-8') as outFile:
        json.dump(data, outFile, indent=4, ensure_ascii=False)


def load_json(file_path):
    """read in jason file data
    :param str file_path: file_path to read
    :return dict: contents of the json file"""
    with open(file_path, encoding='utf-8') as json_data:
        json_file_contents = json.load(json_data)
    return json_file_contents
