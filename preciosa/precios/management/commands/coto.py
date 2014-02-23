# -*- coding: utf-8 -*-
import logging
import requests
import pyquery
import re

from datetime import date
from django.core.management.base import BaseCommand
from tools.utils import UnicodeCsvWriter

logger = logging.getLogger('coto')


class Command(BaseCommand):
    help = 'Scrap de cotodigital'

    def handle(self, *args, **options):
        browser = requests.Session()
        user_agent = {'User-agent': 'Mozilla/5.0'}

        BASE_URL = "http://www.cotodigital.com.ar"
        HOME = "/novedades.asp"

        browser.get(BASE_URL, headers=user_agent)

        # La web guarda tus datos de configuracion
        # Es probable que haga falta modificar el parametro azar, de manera
        # aleatoria
        MAGIC_LINK = "/entrada_guardarconfig.asp?scw=1366&sch=768&nav=NS6&an=Netscape&av=5.0%20%28X11%3B%20Linux%20x86_64%29%20AppleWebKit/537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome/28.0.1500.71%20Safari/537.36&srb=24&ac=&flash=0&referer=&azar=163352140"

        browser.get(BASE_URL + MAGIC_LINK)

        resp = browser.get(BASE_URL + HOME)
        # Se extraen todos los Codigos de los diferentes rubros
        codigos = re.findall("(?<=new Array\()\d+", resp.text)

        # Abrimos el csv donde vamos a guardar los datos
        fp = open("coto.csv", "wb")
        cotowriter = UnicodeCsvWriter(fp)
        cotowriter.writerow(["desc", "precio", "plu", "precio x unidad",
                             "link", "rubro", "fecha"])

        for codigo in codigos:
            # Con el codigo obtenemos el Nombre del Rubro
            rubro = re.findall(
                "(?<=new Array\(%s,')[a-zA-z ]*" %
                codigo,
                resp.text)[0]
            logger.info(u'Descargando rubro:  %s' % rubro)
            resp = browser.get(BASE_URL + "/l.asp",
                               params={"cat": codigo, "id": codigo})
            # existen algunos rubros que muestran un mensaje cuando estan
            # vacios
            if "No hay art" in resp.text:
                continue

            # Los datos vienen adentro de un Script que esta dentro de un form
            f = pyquery.PyQuery(resp.text).find("form#thisForm")[0]

            nombres = re.findall(
                "(?<=desc = new Array\().*?\);",
                f.getchildren()[1].text)
            nombres = nombres[0].strip(",'');").replace("'",
                "").replace("<B>", "").replace( "</B>", "").split(",")

            precios = re.findall("(?<=cart = new Array\().*?\);",
                                 f.getchildren()[1].text)
            precios = precios[0].strip(",0);")
            # Si no hay precios, entonces no hay productos para este rubro
            if not precios:
                continue
            precios = precios.split(",")

            plu = re.findall("(?<=cod  = new Array\().*?\);",
                             f.getchildren()[1].text)
            plu = plu[0].strip(",0);").split(",")

            # Obtenemos el Precio unitario de referecia y lo arreglamos para
            # que quede usable
            precu = re.findall("(?<=precU = new Array\().*?\);",
                               f.getchildren()[1].text)
            precu = precu[0].strip(");").replace("''", "")
            precu = precu.replace("'<font size = -3 color=gray>(",
                "").replace(")</font>'", "").replace("&nbsp;", "  ")

            # Siempre va a tener un elemento mas pero lo ignoramos
            precu = precu.split(",")[:-1]

            for row in zip(nombres, precios, plu, precu):
                row = list(row)
                row.append(
                    "http://www.cotodigital.com.ar/s.asp?id=%s" %
                    row[2])
                row.append(rubro)
                row.append(date.today().isoformat())
                cotowriter.writerow(row)

