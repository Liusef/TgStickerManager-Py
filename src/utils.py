import logging
from logging import debug, info, warning, error, critical
import os
import sys

import jsonpickle
import phonenumbers
from telethon.tl.tlobject import TLObject
from telethon.tl.types import Document, DocumentAttributeFilename


def raise_exception_no_err(val=None):
    """
    Raises an exception and prints out the stringified value of val

    :param val: The object that you want to print out the thing from
    :raises: Exception
    """
    var = ""
    objstr: str = val.stringify() if isinstance(val, TLObject) else str(val)
    if (val != None):
        var = '\n' + str(type(val)) + '\n' + str(val)
    raise Exception("Program encountered something unexpected\n" + var)


def get_path_ext(path: str, fallback_ext: str = '') -> str:
    """
    Gets the extension of a file from its filename or path

    :param path: The Path to retrieve the extension from
    :param fallback_ext: The extension to use if the program fails to find the extension
    :return: The file extension
    """
    i: int = path.rfind('.', 0, len(path))
    return path[i + 1:] if (i != -1) else fallback_ext


def check_file(file: str) -> bool:
    """
    Checks if a file exists at a path
    :param file: The path to the file
    :return: Whether the file exists at the given location
    """
    debug(f'Checking if {file} exists')
    return os.path.exists(file)


def check_path(path: str) -> str:
    """
    Checks if a given path exists on the local device. If the path doesn't exist, the program will create it

    :param path: The path to check
    :return: The path that was input
    """
    debug(f'Checking if {path} exists')
    if not os.path.exists(path):
        debug(f'Path was not found, creating...')
        os.makedirs(path)
    return path


def check_all_paths(paths: list[str]):
    """
    Checks if all paths in an array exist

    :param paths: The array of paths to check
    :return: None
    """
    for p in paths:
        check_path(p)


def read_txt(file: str) -> str:
    """
    Reads text from a specified file.

    PLEASE NOTE this method DOES NOT check if the file already exists.

    :param file: The path to the file
    :return: The plain text in the file
    """
    debug(f'Reading text from {file}')
    with open(file, 'r') as f:
        return f.read()


def write_txt(txt: str, path: str, fname: str, encode: str = 'utf8'):
    """
    Writes text to a file

    :param txt: The text to write to file
    :param path: The path to where the file is
    :param fname: The filename of the file to write to
    :return: None
    """
    debug(f'Writing text to {path}{fname}')
    f = open(check_path(path) + fname, 'w', encoding=encode)
    f.write(txt)
    f.close()


def get_doc_attr(doc: Document, attr_type: type):
    """
    Gets the first instance of a Telethon Document Attribute of a specified type
    :param doc: The document containing the desired attributes
    :param attr_type: The type of the attribute to extract
    :return: (Hopefully) The desired document attribute
    """
    lst: list[attr_type] = [o for o in doc.attributes if isinstance(o, attr_type)]
    if (len(lst) == 0): return None
    return lst[0]


def get_attr_filename(f: Document, fallback: str = "") -> str:
    """
    Returns the filename attribute of a Document if present

    :param f: The Document in question
    :param fallback: The fallback string to return if the document doesn't have the filename attribute
    :return: The filename of the document
    """
    attr: DocumentAttributeFilename = get_doc_attr(f, DocumentAttributeFilename)
    if attr is None: return fallback
    return attr.file_name


def setup_logging(level: int, console: bool, file: bool, path: str = None):
    hnd = []
    hnd.append(logging.StreamHandler(sys.stdout)) if console else None
    hnd.append(logging.FileHandler(path)) if file else None
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=hnd
    )


def serialize(obj: object, path: str, fname: str):
    """
    Non-destructively serializes an object to a file
    :param obj: The object to be serialized
    :param path: The path where you want the serialized object to go
    :param fname: The filename of the serialized object
    :return: None
    """
    info(f"Serializing {type(obj)} object to {path}{fname}")
    jsonpickle.set_encoder_options('json', indent=4)
    ser: str = jsonpickle.encode(obj, unpicklable=True, keys=True)
    write_txt(ser, path, fname)


def deserialize(fpath: str):
    """
    Deserializes object at path.

    PLEASE NOTE This method DOES NOT check if the path is valid NOR does it check if the path actually contains valid
    json

    :param fpath: The path of the file to deserialize
    :return: The deserialized object
    """
    info(f"Attempting to deserialize object from {fpath}")
    return jsonpickle.decode(read_txt(fpath), keys=True)


def is_valid_phone(phone: str) -> bool:
    """
    Checks if an input phone number is valid
    :param phone: The phone number to check
    :return: Whether the phone number was valid
    """
    try:
        info(f"Parsing phone number: {phone}")
        return phonenumbers.is_valid_number(phonenumbers.parse('+' + phone))
    except phonenumbers.phonenumberutil.NumberParseException as e:
        warning(f'{phone}: {e}')
        return False


def format_phone(phone: str) -> str:
    """
    Formats the input phone number to an international standardized format
    :param phone: The phone number to format. Must already be a valid phone number
    :return: The formatted version of the phone number
    """
    info(f"Formatting phone number {phone}")
    return phonenumbers.format_number(phonenumbers.parse(phone), phonenumbers.PhoneNumberFormat.INTERNATIONAL)


