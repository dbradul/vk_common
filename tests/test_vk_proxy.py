import os
import random

from vk_common.models import VkClientProxy

#
# def test_auth():
#     vk_client = VkClientProxy()
#     vk_client.load_accounts()
#     vk_client.auth()
#
#
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
#
#
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


def test_accounts_exceeded():
    vk_client = VkClientProxy(num_calls_threshold=3, call_domain='messages', num_accounts_threshold=2)
    vk_client.load_accounts()
    vk_client.auth()

    prev_account = vk_client._session.login

    for i in range(7):
        res = vk_client.messages.send(
            user_id=708328483,
            random_id=random.randint(100, 100000000),
            message='test message'
        )
        print(i, res)

    # assert prev_account != vk_client._session.login
    assert vk_client.num_accounts == 2
    assert vk_client.num_calls == 1
