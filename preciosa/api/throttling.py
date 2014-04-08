# -*- coding: utf-8 -*-
"""
este módulo define clases para regular y/o validar
un uso "buena leche" de la API
"""

from django.conf import settings
from rest_framework.throttling import UserRateThrottle


class UserRateOrMagicThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        if request.auth and request.auth.key in settings.MAGIC_TOKENS:
            # vip user
            return True
        return super(UserRateOrMagicThrottle, self).allow_request(request, view)


class AntiAnsiososThrottle(UserRateOrMagicThrottle):
    """este scope limita contra los picos de consumo
    Por ejemplo limitando a 40 consultas por minuto"""
    scope = 'anti_ansiosos'


class AntiPerseverantesThrottle(UserRateOrMagicThrottle):
    """este scope limita al consumo constante de largo plazo
    por ejemplo, limitando a 1000 consultas por dia"""
    scope = 'anti_perseverantes'
