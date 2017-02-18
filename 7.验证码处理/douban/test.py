
import Image
import pytesseract
#from PIL import Image

def main():
	img=Image.open('captcha (10).jpg')
	gray = img.convert('L')
	gray.save('test_gray.png')
	bw = gray.point(lambda x: 0 if x < 20 else 255, '1')
	bw.save('test_bw.png')
	text = pytesseract.image_to_string(bw)

	print text

if __name__=='__main__':
	main()
