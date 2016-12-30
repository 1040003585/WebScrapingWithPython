# -*- coding: utf-8 -*-

import csv
import string
from PIL import Image
import pytesseract
from form import register


REGISTER_URL = 'http://example.webscraping.com/user/register'


def main():
    print register('Test Account', 'Test Account', 'example@webscraping.com', 'example', ocr)


def ocr(img):
    # threshold the image to ignore background and keep text
    gray = img.convert('L')
    #gray.save('captcha_greyscale.png')
    bw = gray.point(lambda x: 0 if x < 1 else 255, '1')
    #bw.save('captcha_threshold.png')
    word = pytesseract.image_to_string(bw)
    ascii_word = ''.join(c for c in word if c in string.letters).lower()
    return ascii_word


def test_samples():
    """Test accuracy of OCR on samples images
    """
    correct = total = 0
    for filename, text in csv.reader(open('samples/samples.csv')):
        img = Image.open('samples/' + filename)
        if ocr(img) == text:
            correct += 1
        total += 1
    print 'Accuracy: %d/%d' % (correct, total)


if __name__ == '__main__':
    main()
