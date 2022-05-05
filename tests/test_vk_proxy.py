import os
import random

from vk_api import VkUserPermissions

from vk_common.models import VkClientProxy

from dotenv import load_dotenv

load_dotenv()
#
# def test_auth():
#     vk_client = VkClientProxy()
#     vk_client.load_accounts()
#     vk_client.auth()


# def test_auth_as():
#     vk_client = VkClientProxy()
#     vk_client.load_accounts()
#     vk_client.auth(username='+380679372129')
#
#
# def test_auth_the_same_account():
#     vk_client = VkClientProxy()
#     vk_client.load_accounts()
#     vk_client.auth(username='+380679372129')
#
#     assert vk_client._session.login == '+380679372129'
#
#
# def test_direct_auth():
#     vk_client = VkClientProxy()
#     vk_client.load_accounts()
#
#     vk_client.direct_auth(
#         *vk_client.next_account(),
#         app_id=os.getenv('VK_APP_ID'),
#         client_secret=os.getenv('VK_APP_SECRET')
#     )


# def test_num_calls_exceeded():
#     vk_client = VkClientProxy(num_calls_threshold=3, call_domain='messages')
#     vk_client.load_accounts()
#     vk_client.auth()
#
#     prev_account = vk_client._session.login
#
#     for i in range(4):
#         res = vk_client.messages.send(
#             user_id=708328483,
#             random_id=random.randint(100, 100000000),
#             message='test message'
#         )
#         print(i, res)
#
#     assert prev_account != vk_client._session.login
#     assert vk_client.num_accounts == 1


def _test_auth_until_success():
    vk_client = VkClientProxy()
    vk_client.load_accounts()
    vk_client.auth_until_success()

    res = vk_client.groups.getMembers(
        group_id=20799970
    )

    res = vk_client.messages.send(
        user_id=708328483,
        random_id=random.randint(100, 100000000),
        message='test message'
    )
    print(vk_client)

def _test_direct_auth_until_success():
    vk_client = VkClientProxy()
    vk_client.load_accounts()
    vk_client.direct_auth_until_success()

    res = vk_client.groups.getMembers(
        group_id=20799970
    )

    res = vk_client.messages.send(
        user_id=708328483,
        random_id=random.randint(100, 100000000),
        message='test message'
    )
    print(vk_client)


def test_accounts_exceeded():
    vk_client = VkClientProxy(num_calls_threshold=3, call_domain='messages', num_accounts_threshold=2)
    vk_client.load_accounts()
    # vk_client.auth(scope=(VkUserPermissions.MESSAGES + VkUserPermissions.WALL))
    # vk_client.auth_until_success(reauth=True)
    vk_client.direct_auth_until_success()
    # username, password = vk_client.next_account()
    # vk_client.direct_auth(
    #     username=username,
    #     password=password,
    #     app_id=os.getenv('VK_APP_ID'),
    #     client_secret=os.getenv('VK_APP_SECRET')
    # )

    prev_account = vk_client._session.login

    try:
        for i in range(7):
            res = vk_client.messages.send(
                user_id=708328483,
                random_id=random.randint(100, 100000000),
                message='test message'
            )
            print(i, res)
    except Exception as ex:
        raise
    # assert prev_account != vk_client._session.login
    assert vk_client.num_accounts == 0
    assert vk_client.num_calls == 1



def test_iter_method():
    vk_client = VkClientProxy()
    vk_client.load_accounts()
    vk_client.auth_until_success()

    city_params = {'country_id': 1, 'need_all': 0}
    for city in vk_client.get_iter('database.getCities', params=city_params):
        assert (city)
