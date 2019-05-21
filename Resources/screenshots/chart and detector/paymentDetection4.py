# -*- coding: utf-8 -*-
from __future__ import unicode_literals
print("Detection mechanism started...");

'''
pip install pillow
pip install pytesseract
pip install tesseract
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev

modulele PIL, pytesseract si tesseract in folderul cu detectingMechanism.py

'''

from PIL import Image
from pytesseract import image_to_string
#import cv2 as cv
import sys


keywords = ["total", "otal", "tota", "numerar", "umerar", "numera", "nunerar", "$", "lei", "euro", "pay", "amount", "suma", "plata"]
companyKeywords = ["s.r.l", u"§.r.l", "$.r.l", "s.a", "firma", "company"]

#im = cv.imread("receipt3.jpg", cv.IMREAD_COLOR)


text = image_to_string('image.jpg')
text = text.rstrip().lower()
i = -1
totalPay = 0
paymentString = ""
kwfound = ""
company = ""

def isNumber(c):
	try:
		int(c)
		return True
	except ValueError:
		return False

def hasText(index):
	if index < 0 or text[index] == '\n':
		return False
	return True

def getCompany():
	for kwd in companyKeywords:
		i = text.find(kwd)
		if i != 0 and i != -1:
			i = i - 1
			while hasText(i):
				global company
				company += text[i]
				i = i - 1
			company = company[::-1]
			

i = -1


def getPayment():
	global paymentString
	for kwd in keywords:
		i = text.find(kwd)
		if i != 0 and i != -1:
			while isNumber(text[i]) == False:
				i = i + 1
			while isNumber(text[i]) or text[i] == '.' or text[i] == ',':
				paymentString += text[i]
				i = i + 1
			if text[i] == '%' or text[i + 1] == '%':
				paymentString = ""
				continue
			kwfound = kwd
			break

getPayment()
getCompany()

print("Total payment -> " + paymentString)
print("Company name -> " + company)

