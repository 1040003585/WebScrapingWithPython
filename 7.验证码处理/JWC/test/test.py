# coding:utf

import Image
import pytesseract
#from PIL import Image
import ImageEnhance

rep={'$':'8','i':'1'};

def main():
	img=Image.open('21.jpg')
	'''
	img.save('test_.png')
	enhancer=ImageEnhance.Color(img)
	enhancer=enhancer.enhance(255)
	img.save('test_1Color0.png')
	enhancer=ImageEnhance.Brightness(enhancer)
	enhancer=enhancer.enhance(255)
	img.save('test_2Brigtness0.png')
	enhancer=ImageEnhance.Contrast(enhancer)
	enhancer=enhancer.enhance(255)
	img.save('test_3Contrast0.png')
	enhancer=ImageEnhance.Sharpness(enhancer)
	enhancer=enhancer.enhance(255)
	img.save('test_4Sharpness20.png')
	'''
	gray = img.convert('L')
	gray.save('test_5gray.png')
	bw = gray.point(lambda x: 0 if x < 130 else 255, '1')
	bw.save('test_6bw.png')
	text = pytesseract.image_to_string(bw,lang="eng",config="-psm 6")
	text=text.upper()
	text=text.strip()

	for r in rep:
		text = text.replace(r,rep[r])

	print text

if __name__=='__main__':
	main()

"""
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/7.验证码处理/JWC/test
$ tesseract
Usage:
  tesseract --help | --help-psm | --version
  tesseract --list-langs [--tessdata-dir PATH]
  tesseract --print-parameters [options...] [configfile...]
  tesseract imagename|stdin outputbase|stdout [options...] [configfile...]

OCR options:
  --tessdata-dir PATH   Specify the location of tessdata path.
  --user-words PATH     Specify the location of user words file.
  --user-patterns PATH  Specify the location of user patterns file.
  -l LANG[+LANG]        Specify language(s) used for OCR.
  -c VAR=VALUE          Set value for config variables.
                        Multiple -c arguments are allowed.
  -psm NUM              Specify page segmentation mode.
NOTE: These options must occur before any configfile.

Page segmentation modes:
  0    Orientation and script detection (OSD) only.
  1    Automatic page segmentation with OSD.
  2    Automatic page segmentation, but no OSD, or OCR.
  3    Fully automatic page segmentation, but no OSD. (Default)
  4    Assume a single column of text of variable sizes.
  5    Assume a single uniform block of vertically aligned text.
  6    Assume a single uniform block of text.
  7    Treat the image as a single text line.
  8    Treat the image as a single word.
  9    Treat the image as a single word in a circle.
 10    Treat the image as a single character.

Single options:
  -h, --help            Show this help message.
  --help-psm            Show page segmentation modes.
  -v, --version         Show version information.
  --list-langs          List available languages for tesseract engine.
  --print-parameters    Print tesseract parameters to stdout.
"""
