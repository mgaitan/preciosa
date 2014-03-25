# -*- coding: utf-8 -*-
from rest_framework.authentication import TokenAuthentication


class QueryTokenAuthentication(TokenAuthentication):
    """Igual que token, pero se puede pasar como parámetro
    en query de la petición"""

    def authenticate(self, request):
        if 'token' in request.QUERY_PARAMS:
            return self.authenticate_credentials(request.QUERY_PARAMS['token'])
        return super(QueryTokenAuthentication, self).authenticate(request)
