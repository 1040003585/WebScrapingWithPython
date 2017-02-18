# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import lxml.html
from io import BytesIO
from PIL import Image
import string
import pytesseract
import urlparse

LOGIN_XUEHAO = '1314080903133'
LOGIN_PASSWORD = 'WCB1314080903133'
LOGIN_URL = 'http://bbs.hzu.edu.cn:8080/jwweb/_data/home_login.aspx'


def login_basic():
    """fails because not using formkey
    """
    data = {'txt_asmcdefsddsd': LOGIN_XUEHAO, 'txt_pewerwedsdfsdff': LOGIN_PASSWORD}
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = urllib2.urlopen(request)
    print response.geturl()

def login_formkey():
    """fails because not using cookies to match formkey
    """
    html = urllib2.urlopen(LOGIN_URL).read()
    data = parse_form(html)
    data['txt_asmcdefsddsd'] = LOGIN_XUEHAO
    data['txt_pewerwedsdfsdff'] = LOGIN_PASSWORD
    data['txt_sdertfgsadscxcadsads'] = 'YANZHENGMA'
    data['Sel_Type'] = 'STU'
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = urllib2.urlopen(request)
    print response.geturl()

def login_cookies():
    """working login
    """
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(LOGIN_URL).read()
    data = parse_form(html)
    data['txt_asmcdefsddsd'] = LOGIN_XUEHAO
    data['txt_pewerwedsdfsdff'] = LOGIN_PASSWORD
    data['txt_sdertfgsadscxcadsads'] = ocr(extract_image(html))
    data['Sel_Type'] = 'STU'
    print data
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = opener.open(request)
    print response.geturl()
    return opener

def parse_form(html):
    """extract all input properties from the form
    """
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data

def ocr(img):
    # threshold the image to ignore background and keep text
    gray = img.convert('L')
    gray.save('captcha_greyscale.png')
    bw = gray#.point(lambda x: 0 if x < 1 else 255, '1')
    #bw.save('captcha_threshold.png')
    word = pytesseract.image_to_string(bw)
    ascii_word = ''.join(c for c in word if c in string.letters).lower()
    return ascii_word

def extract_image(html):
    tree = lxml.html.fromstring(html)
    img_data = urlparse.urljoin('http://bbs.hzu.edu.cn:8080/jwweb/','jwweb/'+tree.cssselect('#imgCode')[0].get('src'))
    print img_data
    # remove data:image/png;base64, header
    #img_data = img_data.partition(',')[-1]
    #binary_img_data = img_data.decode('base64')
    #file_like = BytesIO(img_data)
    img = Image.open(img_data)
    img.save('captcha_original.png')
    return img

def main():
    #login_basic()
    #login_formkey()
    login_cookies()

if __name__ == '__main__':
    main()
