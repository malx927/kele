#-*-coding:utf-8-*-
__author__ = 'malxin'

from PIL import Image

def changeImage(im):
    image = Image.open(im)
    try:
        image.load()
    except IOError:
        pass
    image.load()

    try:
        exif = image._getexif()
    except Exception:
        exif = None

    if exif:
        orientation = exif.get(0x0112)
        if orientation == 2:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            image = image.transpose(Image.ROTATE_180)
        elif orientation == 4:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            image = image.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            image = image.transpose(Image.ROTATE_270)
        elif orientation == 7:
            image = image.transpose(Image.ROTATE_90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            image = image.transpose(Image.ROTATE_90)
    return  image