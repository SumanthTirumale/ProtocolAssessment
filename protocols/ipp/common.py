from protocols.ipp.ipp_logger import get_logger

import json
from pathlib import Path


def load_json_file(file_name):
    """
    function to load data from json file and convert
    it in dictionary and return the value
    """
    logger = get_logger("Load json")
    logger.info(f'Getting data from {file_name}')
    try:
        with open(file_name) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.critical(f"{file_name} not found")
    except FileExistsError:
        logger.critical(f"{file_name} not exists")
    finally:
        logger.info("Json load completed")


def load_enum_data(file_name):
    """
    function to load enum data and return it in dictionary
    """
    logger = get_logger("Load Enum Data")
    logger.info("Loading Enum Data")

    enum_data = load_json_file(file_name)
    enum_tag = dict()

    try:
        for key, value in enum_data.items():
            new_key = key.split(",")
            if len(new_key) > 1:
                for i in new_key:
                    enum_tag[i] = value
            else:
                enum_tag["".join(new_key)] = value

        return enum_tag

    except KeyError as k:
        logger.critical(f"key Error {k}")

    finally:
        logger.info("Loading Enum Data completed")


def get_raw_data(file):
    try:
        with open(file, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        print(f"{file} not found !!!")
    except FileExistsError:
        print(f"{file} not exists !!!")


def load_enum():
    enum_tag_file_path = str(Path("protocols/ipp/ipp_data/ipp_enum.json"))
    enum_tag = dict()

    with open(enum_tag_file_path) as f:
        temp = json.load(f)

    for key, value in temp.items():
        new_key = key.split(",")
        if len(new_key) > 1:
            for i in new_key:
                enum_tag[i] = value
        else:
            enum_tag["".join(new_key)] = value

    return enum_tag


def load_attributes():
    attr_value_tag_file_path = str(Path("printerprotocolsipp/ipp_data/ipp_attributes.json"))
    with open(attr_value_tag_file_path) as f:
        return json.load(f)
