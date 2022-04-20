import urllib.parse

from vk_api import AuthError, AccountBlocked
from vk_api.utils import search_re
from vk_api.vk_api import RE_TOKEN_URL, get_unknown_exc_str


def _api_login(self):
    """ Получение токена через Desktop приложение """

    if not self._sid:
        raise AuthError('API auth error (no remixsid)')

    # for cookie_name in ['p', 'l']:
    #     if not self.http.cookies.get(cookie_name, domain='.login.vk.com'):
    #         raise AuthError('API auth error (no login cookies)')

    for cookie_name in ['p']:
        if not self.http.cookies.get(cookie_name, domain='.login.vk.com'):
            raise AuthError('API auth error (no login cookies)')

    response = self.http.get(
        'https://oauth.vk.com/authorize',
        params={
            'client_id': self.app_id,
            'scope': self.scope,
            'response_type': 'token'
        }
    )

    if 'act=blocked' in response.url:
        raise AccountBlocked('Account is blocked')

    if 'access_token' not in response.url:
        url = search_re(RE_TOKEN_URL, response.text)

        if url:
            response = self.http.get(url)

    if 'access_token' in response.url:
        parsed_url = urllib.parse.urlparse(response.url)
        parsed_query = urllib.parse.parse_qs(parsed_url.query)

        if 'authorize_url' in parsed_query:
            url = parsed_query['authorize_url'][0]

            if url.startswith('https%3A'):  # double-encoded
                url = urllib.parse.unquote(url)

            parsed_url = urllib.parse.urlparse(url)

        parsed_query = urllib.parse.parse_qs(parsed_url.fragment)

        token = {k: v[0] for k, v in parsed_query.items()}

        if not isinstance(token.get('access_token'), str):
            raise AuthError(get_unknown_exc_str('API AUTH; no access_token'))

        self.token = token

        self.storage.setdefault(
            'token', {}
        ).setdefault(
            'app' + str(self.app_id), {}
        )['scope_' + str(self.scope)] = token

        self.storage.save()

        self.logger.info('Got access_token')

    elif 'oauth.vk.com/error' in response.url:
        error_data = response.json()

        error_text = error_data.get('error_description')

        # Deletes confusing error text
        if error_text and '@vk.com' in error_text:
            error_text = error_data.get('error')

        raise AuthError('API auth error: {}'.format(error_text))

    else:
        raise AuthError('Unknown API auth error')
