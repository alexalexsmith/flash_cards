"""
Card management
"""
from utilities import file_utils


def get_flash_cards(*args, **kwargs):
    """
    Return a list of FlashCard objects
    :param args:
    :param kwargs:
    :return:
    """
    images = file_utils.get_card_file_list(*args, **kwargs)
    flash_cards = []
    for image in images:
        flash_cards.append(FlashCard(image))
    return flash_cards


class FlashCard(object):
    """
    Flash Card object
    """
    def __init__(self, image, *args, **kwargs):
        """
        Init card
        :param image: path to card image
        """
        self.image = image
        data = file_utils.get_card_data(image)
        self.answer = data.get("answer", "")
        self.hint = data.get("hint", "No Hint provided.")
        self.recall = data.get("recall", "")

    def create(self, src_path, answer, hint=""):
        """
        Create a new card. new card will be copied to the cards folder
        :param src_path: image source path
        :param answer:
        :param hint:
        """
        new_card = file_utils.save_new_card(src_path, answer, hint=hint)

    def update_card(self):
        """Saves card data to disk"""
        data = {"answer": self.answer, "hint": self.hint, "recall": self.recall}
        try:
            # rename the card if the answer was changed
            self.image = file_utils.update_card_data(self.image, data)
        except FileExistsError as e:
            print(e)

    def image_path(self):
        """return the image path"""
        return file_utils.get_image_path(self.image)

    def delete(self):
        """Delete the card and it's data"""
        file_utils.delete_card(self.image)

