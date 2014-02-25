from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.db import models
from django.contrib.flatpages.models import FlatPage


class FlatPageX(FlatPage, TimeStampedModel):
    STATUS = Choices('borrador', 'publicado')
    POSICION = Choices(*xrange(11))
    status = models.CharField(choices=STATUS,
                              default=STATUS.borrador,
                              max_length=20)
    posicion = models.PositiveIntegerField(choices=POSICION, default=1)
