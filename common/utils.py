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
