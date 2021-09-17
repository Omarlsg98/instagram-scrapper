import pandas as pd
import os
import os.path as path
import logging


def beautify_list(list_: list) -> str:
    str_ = ""
    total = len(list_)
    for index, item in enumerate(list_):
        if index < total - 2:
            str_ += f"{item}, "
        elif index < total - 1:
            str_ += f"{item} y "
        else:
            str_ += item
    return str_


def safe_str_to_int(string: str) -> int:
    characters_to_remove = " abcdefghijklmnñopqrstuvwxyz,"
    for character in characters_to_remove:
        string = string.replace(character, "")
    return int(string)


writes_memory = {}


def append_write_pandas_csv(file_path, dataframe, overwrite=False, index=False):
    global writes_memory
    if writes_memory.get(file_path):
        writes_memory[file_path] = writes_memory[file_path]+1
    else:
        writes_memory[file_path] = 1
        if overwrite:
            delete_file(file_path)

    if path.isfile(file_path):
        mode = "a"
        header = False
    else:
        mode = "w"
        header = True
    dataframe.to_csv(file_path, index=index, mode=mode, header=header)


def delete_file(file_path):
    os.remove(file_path)
    logging.info(f"{file_path} removed successfully")
