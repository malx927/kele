#-*-coding:utf-8-*-
import qrcode

__author__ = 'malxin'
import string
import random
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

def mergeImage(imgdst, imgsrc):

    imgdst = imgdst.convert('RGBA')
    imgsrc = imgsrc.convert("RGBA")

    w , h = imgdst.size
    logo_w , logo_h = imgsrc.size
    factor = 4

    s_w = int(w / factor)
    s_h = int(h / factor)

    if logo_w > s_w or logo_h > s_h:
        logo_w = s_w
        logo_h = s_h

    imgsrc = imgsrc.resize((logo_w, logo_h), Image.ANTIALIAS)
    l_w = int((w - logo_w) / 2)
    l_h = int((h - logo_h) / 2)

    imgdst.paste(imgsrc, (l_w, l_h), imgsrc)

    return imgdst


def random_number(length=6):
    rule =  string.digits
    rand_list = random.sample(rule, length)
    return ''.join(rand_list)


# 创建二维码
def create_qrcode(content):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image()
    return img