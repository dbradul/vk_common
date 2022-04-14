import os

from vk_common.models import VkClientProxy


def test_auth():
    vk_client = VkClientProxy()
    vk_client.load_accounts()
    vk_client.auth()


def test_auth_as():
    vk_client = VkClientProxy()
    vk_client.load_accounts()
    vk_client.auth(username='79648355961')


def test_direct_auth():
    vk_client = VkClientProxy()
    vk_client.load_accounts()

    vk_client.direct_auth(
        *vk_client.next_account(),
        app_id=os.getenv('VK_APP_ID'),
        client_secret=os.getenv('VK_APP_SECRET')
    )


def test_method_call():
    vk_client = VkClientProxy()
    vk_client.load_accounts()
    vk_client.auth()

    users = vk_client.users.get(
        user_ids=['id708328483']
    )

    assert users is not None
