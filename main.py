#!/usr/bin/python3
# -*- coding:utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import traceback
import time

import logging
from bs4 import BeautifulSoup
import sys
import os
import urllib.request
import random
import numpy as np

picdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "e-Paper/RaspberryPi_JetsonNano/python/pic",
)
libdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "e-Paper/RaspberryPi_JetsonNano/python/lib",
)
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd3in7

logging.basicConfig(level=logging.DEBUG)

RSS_FEED = "https://backend.deviantart.com/rss.xml?type=deviation&q=pixelart"
XML_FILE = "/tmp/feed.xml"
IMAGE = "/tmp/image.png"
# IMAGE_BMP = "/tmp/image.bmp"

try:
    logging.info("Start")

    urllib.request.urlretrieve(RSS_FEED, XML_FILE)
    with open(XML_FILE, "r") as f:
        data = BeautifulSoup(f.read(), "xml")
        items = data.find_all("media:content")
        choice = random.randrange(0, len(items))
        media_url = items[choice].get("url")
        print(media_url)
        urllib.request.urlretrieve(media_url, IMAGE)

        epd = epd3in7.EPD()
        logging.info("init and Clear")
        epd.init(0)
        epd.Clear(0xFF, 0)

        # Resize image to fit screen:
        img = Image.open(IMAGE)
        width, height = img.size
        if width < height:
            img = img.rotate(90)

        x = y = 0
        target_width = width
        target_height = height
        if width / height < 12 / 7:
            target_height = width * 7 / 12
            x = 0
            y = (height - target_height) / 2
        else:
            target_width = height * 12 / 7
            x = (width - target_width) / 2
            y = 0
        img = img.crop((x, y, target_width, target_height))
        img = img.resize((480, 280))
        
        # Convert to bitmap
        # ary = np.array(img)
        # # Split the three channels
        # r,g,b = np.split(ary,3,axis=2)
        # r=r.reshape(-1)
        # g=r.reshape(-1)
        # b=r.reshape(-1)
        # # Standard RGB to grayscale
        # bitmap = list(map(lambda x: 0.299*x[0]+0.587*x[1]+0.114*x[2],
        # zip(r,g,b)))
        # bitmap = np.array(bitmap).reshape([ary.shape[0], ary.shape[1]])
        # bitmap = np.dot((bitmap > 128).astype(float),255)
        # im = Image.fromarray(bitmap.astype(np.uint8))
        
        epd.display_4Gray(epd.getbuffer_4Gray(img))
        time.sleep(5)

        logging.info("Goto Sleep...")
        epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd3in7.epdconfig.module_exit()
    exit()
