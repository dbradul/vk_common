import os

from vk_common.models import VkClientProxy
from vk_common.utils import login_retrier, repack_exc, login_retrier_gen, repack_exc_gen


@login_retrier
@repack_exc
def get_user_id_by_name(client, user_name):
    users = client.users.get(
        user_ids=[user_name]
    )
    if not users:
        raise RuntimeError(f'User not found: {user_name}')

    return users[0]['id']


@login_retrier_gen
@repack_exc_gen
def get_group_members_by_id(client, group_id):
    members = client.groups.getMembers(
        group_id=group_id
    )

    for member in members.get('items'):
        yield member


def test_auth():
    vk_client = VkClientProxy()
    vk_client.load_accounts()
    vk_client.auth()


def test_decorated_func():
    vk_client = VkClientProxy()
    vk_client.load_accounts()
    vk_client.auth()

    user_id = get_user_id_by_name(vk_client, user_name='id708328483')
    assert user_id is not None

    members = list(get_group_members_by_id(vk_client, group_id='20799970'))
    assert len(members) > 0

