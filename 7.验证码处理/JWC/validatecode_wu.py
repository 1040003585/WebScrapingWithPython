
#import Image
import string
from PIL import Image
import pytesseract

def main():
	img=Image.open('test3.jpg')
	string=pytesseract.image_to_string(img)
	print string

if __name__ == '__main__':
    main()
