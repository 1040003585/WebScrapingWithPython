
import Image
import pytesseract
#from PIL import Image

rep={'$':'8','i':'1'};

def main():
	img=Image.open('test3.jpg')
	gray = img.convert('L')
	gray.save('test_gray.png')
	bw = gray.point(lambda x: 0 if x < 178 else 255, '1')
	bw.save('test_bw.png')
	text = pytesseract.image_to_string(bw)
	
	for r in rep:
		text = text.replace(r,rep[r])

	print text

if __name__=='__main__':
	main()
