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

keywords = ["total", "otal", "tota", "numerar", "umerar", "numera", "nunerar", "$", "lei", "euro", "pay", "amount", "suma", "plata"]

text = image_to_string(Image.open('receipt3.jpg'))
text = text.rstrip().lower()
i = -1
totalPay = 0
paymentString = ""
kwfound = ""

def isNumber(c):
	try:
		int(c)
		return True
	except ValueError:
		return False

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
	else:
		print("No match for keyword " + kwd) 
print(float(paymentString) )

