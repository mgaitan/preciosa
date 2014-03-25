# -*- coding: utf-8 -*-
"""
este módulo define clases para regular y/o validar
un uso "buena leche" de la API
"""


from rest_framework.throttling import UserRateThrottle


class AntiAnsiososThrottle(UserRateThrottle):
    """este scope limita contra los picos de consumo
    Por ejemplo limitando a 40 consultas por minuto"""
    scope = 'anti_ansiosos'


class AntiPerseverantesThrottle(UserRateThrottle):
    """este scope limita al consumo constante de largo plazo
    por ejemplo, limitando a 1000 consultas por dia"""
    scope = 'anti_perseverantes'
