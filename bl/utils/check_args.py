import logging


class CheckArgs:
    @staticmethod
    def check_args_add_photo_clothes(id_user, id_category, id_subcategory, id_sub_subcategory, user_name, category,
                                     subcategory,
                                     sub_subcategory,
                                     photo_path):
        ret = True
        if id_user is None:
            logging.error(f"User '{user_name}' not found")
            ret = False
        if id_category is None:
            logging.error(f"Category '{category}' not found")
            ret = False
        if id_subcategory is None:
            logging.error(f"Subcategory '{subcategory}' not found")
            ret = False
        if id_sub_subcategory is None:
            logging.error(f"Sub_subcategory '{sub_subcategory}' not found")
            ret = False
        if photo_path == "":
            logging.error("Photo path is empty")
            ret = False
        return ret

    @staticmethod
    def check_args_add_photo_person(id_user, id_category, user_name, category, photo_path):
        ret = True
        if id_user is None:
            logging.error(f"User '{user_name}' not found")
            ret = False
        if id_category is None:
            logging.error(f"Category '{category}' not found")
            ret = False
        if photo_path == "":
            logging.error("Photo path is empty")
            ret = False
        return ret
