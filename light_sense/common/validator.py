def key_validator(exp_keys: list, data: dict) -> list:
    """
    Returns a list of keys that aren't present in the data dict
    If all are present, returns nothing

    Arguments:
        exp_keys {list} -- list of keys
        data {dict} -- dict to verify

    Returns:
        list/ None
    """
    return_list = []
    for key in exp_keys:
        if key not in data.keys():
            return_list.append(key)

    if len(return_list) > 0:
        return return_list