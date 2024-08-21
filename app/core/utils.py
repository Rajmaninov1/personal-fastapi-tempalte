import asyncio
import functools
from datetime import datetime
from typing import Any, Callable
from uuid import uuid4

from fastapi.responses import ORJSONResponse
from orjson import orjson
from pydantic import BaseModel


def generate_transaction_id():
    return datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4()).upper()


def try_unpack_json(s: str) -> Any:
    """
    Tries to parse a string as JSON using the `orjson` library.

    Args:
        s (str): The string to be parsed as JSON.

    Returns:
        Any: The parsed JSON object as a Python object. If the input string cannot
             be parsed as JSON, the original string is returned.

    """
    # noinspection PyBroadException
    try:
        return orjson.loads(s)
    except Exception:
        return s


def try_pack_object(s: Any) -> str:
    """
    Tries to dump an object as JSON str using the `orjson` library.

    Args:
        s (str): The object to be dumped as JSON str.

    Returns:
        Any: The dumped JSON str. If the input object cannot
             be dumped as JSON, the original object is returned.

    """
    # noinspection PyBroadException
    try:
        return orjson.dumps(s).decode('utf-8')
    except Exception:
        return s


def pydantic_orjson_result(func):
    """
    Decorator that converts the result of an asynchronous function to an ORJSONResponse.

    This decorator is designed to work with FastAPI endpoints. It wraps an asynchronous function and ensures that the
    response is converted to a JSON format using ORJSON, which is a fast and efficient JSON library.
    The decorator handles
    the following types of return values:

    1. If the return value is an instance of a Pydantic BaseModel, it converts the model to a dictionary and returns it
    as an ORJSONResponse.
    2. If the return value is a list of Pydantic BaseModel instances, it converts each model to a dictionary and returns
    the list as an ORJSONResponse.
    3. For any other type of return value, it directly returns it as an ORJSONResponse.

    Args:
        func (Callable): The asynchronous function to be wrapped.

    Returns:
        Callable: The wrapped function which returns an ORJSONResponse.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if isinstance(result, BaseModel):
            return ORJSONResponse(result.dict())
        elif isinstance(result, list):
            return ORJSONResponse([_.dict() for _ in result])
        else:
            return ORJSONResponse(result)

    return wrapper


def merge_dicts(collision_func: Callable[[Any, Any], Any], d1: dict, d2: dict):
    """
    Merge two dictionaries using collision_func to combine keys on collision
    :param collision_func:
    :param d1:
    :param d2:
    :return:
    """
    return {key: collision_func(d1.get(key, None), d2.get(key, None)) for key in set(list(d1.keys()) + list(d2.keys()))}


async def wrap_sync_function(function: Callable, *args, **kwargs) -> Any:
    """
    Run a function in a new thread and wrap it into the main asyncio loop
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        functools.partial(function, *args, **kwargs)
    )


def repeat_to_length(s: str, wanted: int):
    """
    Repeat a string 's' until the length 'wanted'
    :param s:
    :param wanted:
    :return:
    """
    return (s * (wanted // len(s) + 1))[:wanted]


def standardize_string_to_compare(text: str):
    """
    Convert to uppercase, ensure one space after each comma, then remove all spaces even if are two or more consecutive
    and join wih only one space between words
    :param text:
    :return:
    """
    if text is None:
        return None
    return ' '.join(text.upper().replace(',', ', ').split())
