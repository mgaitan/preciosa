from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class MovilInfo(models.Model):
    """
    ver

    http://docs.phonegap.com/es/1.0.0/phonegap_device_device.md.html
    """
    uuid = models.CharField(max_length=200, primary_key=True)
    user = models.ForeignKey(get_user_model(), related_name='movil_info')
    nombre = models.CharField(max_length=200, null=True, blank=True)
    phonegap = models.CharField(max_length=100, null=True, blank=True)
    plataforma = models.CharField(max_length=200, null=True, blank=True)
    plataforma_version = models.CharField(max_length=200, null=True, blank=True)
    preciosa_version = models.CharField(max_length=200, null=True, blank=True)


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
