import os
import requests

import vk_api
from pydantic import BaseModel
from typing import List, Optional, Any, Union

from vk_common.log import logger


class Mapping(BaseModel):
    city: dict
    country: dict


class Config(BaseModel):
    search_criteria: Optional[dict] = {}
    search_count: Optional[int] = 100
    parse_posts: Optional[bool] = False
    fetch_fields: Optional[List[str]] = []
    csv_fields: Optional[List[str]] = []
    resume_from: Optional[str] = ''
    custom_csv_fields: Optional[List[str]] = []

    def get_fetch_fields(self):
        return ', '.join(self.fetch_fields)


class VkResponse(BaseModel):
    count: int
    items: List[Union[int, dict]]


class VkClientProxy:
    PROFILE_PHONE_NUMBER_PREFIX = 'USER_PHONE_NUMBER'
    PROFILE_PASSWORD_PREFIX = 'USER_PASSWORD'

    def __init__(self, config_data=None, num_calls_threshold=0, call_domain='', num_accounts_threshold=0):
        self._obj = None
        self._session = None
        self._accounts = []
        # self.config: Config = config
        self.config: Config = Config(**(config_data or {}))
        self.num_calls = 0
        self.call_domain = call_domain
        self.num_calls_threshold = num_calls_threshold
        self.num_accounts = 0
        self.num_accounts_threshold = num_accounts_threshold

    def __getattr__(self, item):
        if self.num_calls_threshold > 0:
            self._change_account()

        result = getattr(self._obj, item)
        if self.call_domain == item:
            self.num_calls += 1
        return result

    def _change_account(self):
        if self.num_calls == self.num_calls_threshold:
            logger.info(f"Num call threshold is exceeded ({self.num_calls_threshold})!")
            new_login, _ = self.next_account()
            logger.info(f"Switching to another account: {self._session.login} -> {new_login}.")
            self.auth(username=new_login)
            self.num_calls = 0
            self.num_accounts += 1

            if self.num_accounts_threshold > 0:
                self._change_vpn()

    def _change_vpn(self):
        """So far VPN change is not automated, so we just ASK a user to do it manually"""
        if (self.num_accounts) == self.num_accounts_threshold:
            logger.info(f"Num accounts threshold is exceeded ({self.num_accounts_threshold})!")
            logger.info("Please, change VPN region and press ENTER to continue...")

            print('\n---------------------------------------------------------')
            print(f"Num accounts threshold is exceeded ({self.num_accounts_threshold})!")
            input("Please, change VPN region and press ENTER to continue...")

            self.num_accounts = 0

    def set_proxy_obj(self, instance):
        if isinstance(instance, dict):
            for k, v in instance.items():
                setattr(self, k, v)
        else:
            self._obj = instance

    def load_accounts(self):
        accounts = []
        for k, v in os.environ.items():
            if k.startswith(self.PROFILE_PHONE_NUMBER_PREFIX):
                suffix = k.replace(f'{self.PROFILE_PHONE_NUMBER_PREFIX}', '')
                if os.environ.get(f'{self.PROFILE_PASSWORD_PREFIX}{suffix}'):
                    accounts.append((
                        os.getenv(k),
                        os.getenv(f'{self.PROFILE_PASSWORD_PREFIX}{suffix}')
                    ))
                else:
                    logger.error(f'Profile PHONE NUMBER env var doesnt match with PASSWORD (different suffix)')

        self._accounts = accounts

    def next_account(self):
        result = None, None
        if self._accounts:
            result = self._accounts.pop(0)
            self._accounts.append(result)
        return result

    def auth(self, username=None):
        try:
            if username:
                username, password = [(acc, passw) for acc, passw in self._accounts if acc == username][0]
            else:
                username, password = self.next_account()
            self._session = vk_api.VkApi(username, password)
            self._session.auth()
            self.set_proxy_obj(self._session.get_api())
            logger.info(f'Successfully authenticated as {username}!')
            # self.config = Config(**self.config.data)
        except Exception as ex:
            self.direct_auth(
                username=username,
                password=password,
                app_id=os.getenv('VK_APP_ID'),
                client_secret=os.getenv('VK_APP_SECRET')
            )

    def direct_auth(self, username, password, **kw_args):
        # username, password = self.next_account()
        app_id, client_secret = kw_args.get('app_id'), kw_args.get('client_secret')
        self._session = vk_api.VkApi(username, password, **kw_args)
        AUTH_URL = f'https://oauth.vk.com/token?grant_type=password&client_id={app_id}&client_secret={client_secret}&'
        resp = requests.get(AUTH_URL + f'username={username}&password={password}')
        if resp.status_code != 200:
            logger.info(f'Couldn\'t authenticate as {username}!')
            raise RuntimeError(f'Not authenticated {resp.status_code}, {resp.text}')
        else:
            logger.info(f'Successfully authenticated as {username}!')
        self._session.token = resp.json()
        self.set_proxy_obj(self._session.get_api())

    def get_params(self, extra_params=None):
        params = {'count': self.config.search_count}
        if extra_params:
            params.update(extra_params)
        return params