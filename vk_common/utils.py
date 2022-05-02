import csv
import functools
from datetime import datetime

import itertools
from vk_api import ApiError

from .log import logger
from .models import VkClientProxy


class VKBaseException(Exception):
    error_code = 0

class RateLimitException(VKBaseException):
    error_code = 29

# class ProfileIsPrivateException(VKBaseException):
#     error_code = 30

class PermissionIsDeniedException(VKBaseException):
    error_code = 7

class UserIsBlockedException(VKBaseException):
    error_code = 5

RELOGIN_EXCEPTIONS_MAP = {ex.error_code: ex for ex in (
    RateLimitException,
    # ProfileIsPrivateException,
    PermissionIsDeniedException,
    UserIsBlockedException
)}


# ----------------------------------------------------------------------------------------------------------------------
def from_unix_time(ts):
    return datetime.utcfromtimestamp(ts)


def unwind_value(d, prefix=''):
    prefix = f'{prefix}_' if prefix else prefix
    result = {}
    for k, v in d.items():
        if type(v) == dict:
            result.update(unwind_value(v, prefix=f'{prefix}{k}'))
        elif type(v) == list:
            for idx, elem in enumerate(v):
                if type(elem) == dict:
                    result.update(unwind_value(elem, prefix=f'{prefix}{k}_{idx}'))
                else:
                    result[f'{prefix}{k}_{idx}'] = elem
        else:
            result[f'{prefix}{k}'] = v
    return result


def read_from_csv(filename, config, column='id'):
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, quotechar='"', delimiter=',')
        lines = [line for line in reader]
    if config.resume_from:
        resumed_lines = itertools.dropwhile(
            lambda x: x[column] != config.resume_from, lines
        )
        next(resumed_lines)
        lines = list(resumed_lines)
    chunk_size = config.search_count
    for x in range(0, len(lines), chunk_size):
        users_chunk = lines[x: x + chunk_size]
        yield len(lines), users_chunk


def repack_exc(func):
    @functools.wraps(func)
    def inner(client, *args, **kwargs):
        try:
            result = func(client, *args, **kwargs)
            return result

        except ApiError as ex:
            if ex.code in RELOGIN_EXCEPTIONS_MAP:
                raise RELOGIN_EXCEPTIONS_MAP[ex.code](str(ex))
            else:
                raise
    return inner


def repack_exc_gen(func):
    @functools.wraps(func)
    def inner(client, *args, **kwargs):
        try:
            result = func(client, *args, **kwargs)
            yield from result

        except ApiError as ex:
            if ex.code in RELOGIN_EXCEPTIONS_MAP:
                raise RELOGIN_EXCEPTIONS_MAP[ex.code](str(ex))
            else:
                raise
    return inner


def login_retrier(func):
    @functools.wraps(func)
    def inner(client: VkClientProxy, *args, **kwargs):
        try:
            result = func(client, *args, **kwargs)
            return result

        except tuple(RELOGIN_EXCEPTIONS_MAP.values()) as ex:
            logger.error(f'Retrying after error: {ex}')
            for i in range(len(client._accounts)):
                try:
                    username, _ = client.switch_account()
                    logger.info(f"Switching to another account: {client._session.login} -> {username}.")
                    # client.auth_until_success(username)
                    client._reauth_func(username)
                    client.num_calls = 0
                    result = func(client, *args, **kwargs)
                    return result
                except tuple(RELOGIN_EXCEPTIONS_MAP.values()) as ex:
                    logger.error(f'Failed with account {username}. Retrying after error: {ex}')
            else:
                raise
    return inner


def login_retrier_gen(func):
    @functools.wraps(func)
    def inner(client: VkClientProxy, *args, **kwargs):
        try:
            result = func(client, *args, **kwargs)
            yield from result

        except tuple(RELOGIN_EXCEPTIONS_MAP.values()) as ex:
            logger.error(f'Retrying after error: {ex}')
            for i in range(len(client._accounts)):
                try:
                    username, _ = client.switch_account()
                    logger.info(f"Switching to another account: {client._session.login} -> {username}.")
                    # client.auth_until_success(username)
                    client._reauth_func(username)
                    client.num_calls = 0
                    result = func(client, *args, **kwargs)
                    yield from result
                    break
                except tuple(RELOGIN_EXCEPTIONS_MAP.values()) as ex:
                    logger.error(f'Failed with account {username}. Retrying after error: {ex}')
            else:
                raise
    return inner
