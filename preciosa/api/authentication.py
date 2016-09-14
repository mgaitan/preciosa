# -*- coding: utf-8 -*-
from rest_framework.authentication import TokenAuthentication


class QueryTokenAuthentication(TokenAuthentication):
    """Igual que token, pero se puede pasar como parámetro
    en query de la petición"""

    def authenticate(self, request):
        if 'token' in request.query_params:
            return self.authenticate_credentials(request.query_params['token'])
        return super(QueryTokenAuthentication, self).authenticate(request)
