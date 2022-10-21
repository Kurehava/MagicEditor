import base64
import re
from re import findall
from os import path, system, walk, makedirs, rename
from platform import system as psystem
from random import sample
from shutil import rmtree, copy
from string import ascii_letters, digits
from time import strftime, localtime, sleep

import svgwrite
import fitz
from PIL import Image, UnidentifiedImageError
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


def entry():
    pass
