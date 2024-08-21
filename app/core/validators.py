from dateparser import parse

from core.utils import standardize_string_to_compare, repeat_to_length, try_pack_object


def validate_open_date_format(cls, v):  # noqa
    """
    Parse a string to date using dateparser
    :param cls:
    :param v: string to validate
    :return:
    """
    if isinstance(v, str):
        if date := parse(v):
            return date
    return v


# noinspection PyUnusedLocal
def validate_float(cls, v):
    """
    Transform strings to float if can
    :param cls:
    :param v: string to validate
    :return:
    """
    if isinstance(v, str):
        v = v.replace(',', '.').replace('%', '').strip()
        try:
            v = float(v)
            return v
        except ValueError:
            return None
    return v


# noinspection PyUnusedLocal
def remove_string_word(cls, v):
    """
    Remove empty "STRING" from all ingress strings
    :param cls:
    :param v: ingress string
    :return:
    """
    if isinstance(v, str):
        if v.upper() == 'STRING' or (len(v) > 0 and v.upper() == repeat_to_length('STRING', len(v))):
            v = None
        return None if not v else v
    return v


def standardize_string(cls, v):
    """
    Standardize all ingress strings
    :param cls:
    :param v: string to standardize
    :return:
    """
    if isinstance(v, str):
        v = standardize_string_to_compare(v)
        v = remove_string_word(cls, v)
        return None if not v else v
    return v


# noinspection PyUnusedLocal
def cut_length_list_dict(cls, v):
    if v and (isinstance(v, list) or isinstance(v, dict)):
        packed = try_pack_object(v)
        # clear content if is invalid
        if not isinstance(packed, str):
            return 'ERROR: not serializable content, replaced by this message'
        # if packed is getheader than 5 KB cut and return as str not list of dict
        if len(packed) > 5120:
            v = packed[: 5120]

    return v
