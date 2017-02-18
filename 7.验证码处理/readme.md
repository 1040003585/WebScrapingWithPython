# 验证码处理
[TOC]

**验证码（CAPTCHA）**全称为**全自动区分计算机和人类的公开图灵测试（Completely Automated Public Turing test to tell Computersand Humans Apart）**。从其全称可以看出，验证码用于测试用户是真实的人类还是计算机机器人。
# 1.获得验证码图片
每次加载注册网页都会显示不同的验证验图像，为了了解表单需要哪些参数，我们可以复用上一章编写的parse_form()函数。
```python
>>> import cookielib,urllib2,pprint
>>> import form
>>> REGISTER_URL = 'http://127.0.0.1:8000/places/default/user/register'
>>> cj=cookielib.CookieJar()
>>> opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
>>> html=opener.open(REGISTER_URL).read()
>>> form=form.parse_form(html)
>>> pprint.pprint(form)
{'_formkey': 'a67cbc84-f291-4ecd-9c2c-93937faca2e2',
 '_formname': 'register',
 '_next': '/places/default/index',
 'email': '',
 'first_name': '',
 'last_name': '',
 'password': '',
 'password_two': '',
 'recaptcha_response_field': None}
>>> 
```
上面`recaptcha_response_field`是存储验证码的值，其值可以用`Pillow`从验证码图像获取出来。先安装`pip install Pillow`，其它安装Pillow的方法可以参考http://pillow.readthedocs.org/installation.html 。Pillow提价了一个便捷的Image类，其中包含了很多用于处理验证码图像的高级方法。下面的函数使用注册页的HTML作为输入参数，返回包含验证码图像的Image对象。
```python
>>> import lxml.html
>>> from io import BytesIO
>>> from PIL import Image
>>> tree=lxml.html.fromstring(html)
>>> print tree
<Element html at 0x7f8b006ba890>
>>> img_data_all=tree.cssselect('div#recaptcha img')[0].get('src')
>>> print img_data_all
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAABgCAIAAAB9kzvfAACAtklEQVR4nO29Z5gcZ5ku3F2dc865
...
rkJggg==
>>> img_data=img_data_all.partition(',')[2]
>>> print img_data
iVBORw0KGgoAAAANSUhEUgAAAQAAAABgCAIAAAB9kzvfAACAtklEQVR4nO29Z5gcZ5ku3F2dc865
...
rkJggg==
>>> 
>>> binary_img_data=img_data.decode('base64')
>>> file_like=BytesIO(binary_img_data)
>>> print file_like
<_io.BytesIO object at 0x7f8aff6736b0>
>>> img=Image.open(file_like)
>>> print img
<PIL.PngImagePlugin.PngImageFile image mode=RGB size=256x96 at 0x7F8AFF5FAC90>
>>> 
```
在本例中，这是一张进行了Base64编码的PNG图像，这种格式会使用ASCII编码表示二进制数据。我们可以通过在第一个逗号处分割的方法移除该前缀。然后，使用Base64解码图像数据，回到最初的二进制格式。要想加载图像，PIL需要一个类似文件的接口，所以在传给Image类之前，我们以使用了BytesIO对这个二进制数据进行了封装。
完整代码:
```python
# -*- coding: utf-8 -*-form.py

import urllib
import urllib2
import cookielib
from io import BytesIO
import lxml.html
from PIL import Image

REGISTER_URL = 'http://127.0.0.1:8000/places/default/user/register'
#REGISTER_URL = 'http://example.webscraping.com/user/register'

def extract_image(html):
    tree = lxml.html.fromstring(html)
    img_data = tree.cssselect('div#recaptcha img')[0].get('src')
    # remove data:image/png;base64, header
    img_data = img_data.partition(',')[-1]
    #open('test_.png', 'wb').write(data.decode('base64'))
    binary_img_data = img_data.decode('base64')
    file_like = BytesIO(binary_img_data)
    img = Image.open(file_like)
    #img.save('test.png')
    return img

def parse_form(html):
    """extract all input properties from the form
    """
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data

def register(first_name, last_name, email, password, captcha_fn):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(REGISTER_URL).read()
    form = parse_form(html)
    form['first_name'] = first_name
    form['last_name'] = last_name
    form['email'] = email
    form['password'] = form['password_two'] = password
    img = extract_image(html)#
    captcha = captcha_fn(img)#
    form['recaptcha_response_field'] = captcha
    encoded_data = urllib.urlencode(form)
    request = urllib2.Request(REGISTER_URL, encoded_data)
    response = opener.open(request)
    success = '/user/register' not in response.geturl()
    #success = '/places/default/user/register' not in response.geturl()
    return success
```
# 2.光学字符识别验证码
**光学字符识别（Optical Character Recognition, OCR）**用于图像中抽取文本。本节中，我们将使用开源的Tesseract OCR引擎，该引擎最初由惠普公司开发的，目前由Google主导。Tesseract的安装说明可以从http://code.google.com/p/tesseract-ocr/wiki/ReadMe 获取。然后可以使用pip安装其Python封装版本pytesseract`pip install pytesseract`。
下面我们用光学字符识别图像验证码：
```python
>>> import pytesseract
>>> import form
>>> img=form.extract_image(html)
>>> pytesseract.image_to_string(img)
''
>>> 
```
如果直接把验证码原始图像传给pytesseract，一般不能解析出来。这是因为Tesseract是抽取更加典型的文本，比如背景统一的书页。下面我们进行去除背景噪音，只保留文本部分。验证码文本一般都是黑色的，背景则会更加明亮，所以我们可以通过检查是否为黑色将文本分离出来，该处理过程又被称为**阈值化**。
```python
>>> 
>>> img.save('2captcha_1original.png')
>>> gray=img.convert('L')
>>> gray.save('2captcha_2gray.png')
>>> bw=gray.point(lambda x:0 if x<1 else 255,'1')
>>> bw.save('2captcha_3thresholded.png')
>>> 
```
这里只有阈值小于1的像素（全黑）都会保留下来，分别得到三张图像：原始验证码图像、转换后的灰度图和阈值化处理后的黑白图像。最后我们将阈值化处理后黑白图像再进行Tesseract处理，验证码中的文字已经被成功抽取出来了。
```python
>>> pytesseract.image_to_string(bw)
'language'
>>> 
>>> import Image,pytesseract
>>> img=Image.open('2captcha_3thresholded.png')
>>> pytesseract.image_to_string(img)
'language'
>>> 

```
我们通过示例样本测试，100张验证码能正确识别出90张。
```python
>>> import ocr
>>> ocr.test_samples()
Accuracy: 90/100
>>> 
```
下面是注册账号完整代码：
```python
# -*- coding: utf-8 -*-

import csv
import string
from PIL import Image
import pytesseract
from form import register

def main():
    print register('Wu1', 'Being1', 'Wu_Being001@qq.com', 'example', ocr)

def ocr(img):
    # threshold the image to ignore background and keep text
    gray = img.convert('L')
    #gray.save('captcha_greyscale.png')
    bw = gray.point(lambda x: 0 if x < 1 else 255, '1')
    #bw.save('captcha_threshold.png')
    word = pytesseract.image_to_string(bw)
    ascii_word = ''.join(c for c in word if c in string.letters).lower()
    return ascii_word

if __name__ == '__main__':
    main()
```
我们可以进一步改善OCR性能：
- 实验不同阈值
- 腐蚀阈值文本，突出字符形状
- 调整图像大小
- 根据验证码字体训练ORC工具
- 限制结果为字典单词

# 3.用API处理复杂验证码
为了处理更加复杂的图像，我们将使用验证处理服务，也叫**打码平台**。
## 3.1 9kw打码平台
- 先到9kw打码平台注册一个个人账号https://www.9kw.eu/register.html 
- 登录后，定位到https://www.9kw.eu/usercaptcha.html 手工处理其他用户验证码获得积分
- 创建API key https://www.9kw.eu/index.cgi?action=userapinew&source=api 

### 3.1.1 提交验证码
提交验证码参数：
- URL： https://www.9kw.eu/index.cgi（POST）
- action：POST必须设为：'usercaptchaupload'
- apikey：个人的API key
- file-upload-01：需要处理的图像（文件、url 或字符串）
- base64：如果输入的是Base64编码，则设为“1”
- maxtimeout：等待处理的最长时间（60～3999）
- selfsolve：如果自己处理该验证码，则设为“1”

返回值：
- 该验证码的ID

```python
    API_URL： https://www.9kw.eu/index.cgi
    def send(self, img_data):
        """Send CAPTCHA for solving
        """
        print 'Submitting CAPTCHA'
        data = {
            'action': 'usercaptchaupload',
            'apikey': self.api_key,
            'file-upload-01': img_data.encode('base64'),
            'base64': '1',
            'selfsolve': '1',
            'maxtimeout': str(self.timeout)
        }
        encoded_data = urllib.urlencode(data)
        request = urllib2.Request(API_URL, encoded_data)
        response = urllib2.urlopen(request)
        return response.read()
```
API文档地址https://www.9kw.eu/api.html#apisubmit-tab 
### 3.1.2 请求已提交验证码结果
请求结果的参数：
- URL： https://www.9kw.eu/index.cgi（GET）
- action：GET必须设为：'usercaptchacorrectdata'
- apikey：个人的API key
- id：要检查的验证码ID
- info：若设为“1”，没有得到结果时返回“NO DATA”（默认返回空）

返回值：
- 要处理的验证码文本或错误码

错误码：
- 0001：API key不存在
- 0002：没有找到API key
- 0003：没有找到激活的API key
......
- 0031：账号被系统禁用24小时
- 0032：账号没有足够的权限
- 0033：需要升级插件

```python
    def get(self, captcha_id):
        """Get result of solved CAPTCHA
        """
        data = {
            'action': 'usercaptchacorrectdata',
            'id': captcha_id,
            'apikey': self.api_key,
            'info': '1'
        }
        encoded_data = urllib.urlencode(data)
        response = urllib2.urlopen(self.url + '?' + encoded_data)
        return response.read()
```
### 3.1.2与注册功能集成
```python
# -*- coding: utf-8 -*-

import sys
import re
import urllib2
import urllib
import time
from io import BytesIO

from PIL import Image
from form import register

def main(api_key, filename):
    captcha = CaptchaAPI(api_key)
    print register('wu101', 'being101', 'wu_being101@qq.com', 'password.com', captcha.solve)

class CaptchaError(Exception):
    pass

class CaptchaAPI:
    def __init__(self, api_key, timeout=60):
        self.api_key = api_key
        self.timeout = timeout
        self.url = 'https://www.9kw.eu/index.cgi'

    def solve(self, img):
        """Submit CAPTCHA and return result when ready
        """
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_data = img_buffer.getvalue()
        captcha_id = self.send(img_data)
        start_time = time.time()
        while time.time() < start_time + self.timeout:
            try:
                text = self.get(captcha_id)
            except CaptchaError:
                pass # CAPTCHA still not ready
            else:
                if text != 'NO DATA':
                    if text == 'ERROR NO USER':
                        raise CaptchaError('Error: no user available to solve CAPTCHA')
                    else:
                        print 'CAPTCHA solved!'
                        return text
            print 'Waiting for CAPTCHA ...'
        raise CaptchaError('Error: API timeout')

    def send(self, img_data):
        """Send CAPTCHA for solving
        """
        print 'Submitting CAPTCHA'
        data = {
            'action': 'usercaptchaupload',
            'apikey': self.api_key,
            'file-upload-01': img_data.encode('base64'),
            'base64': '1',
            'selfsolve': '1',
            'maxtimeout': str(self.timeout)
        }
        encoded_data = urllib.urlencode(data)
        request = urllib2.Request(self.url, encoded_data)
        response = urllib2.urlopen(request)
        result = response.read()
        self.check(result)
        return result

    def get(self, captcha_id):
        """Get result of solved CAPTCHA
        """
        data = {
            'action': 'usercaptchacorrectdata',
            'id': captcha_id,
            'apikey': self.api_key,
            'info': '1'
        }
        encoded_data = urllib.urlencode(data)
        response = urllib2.urlopen(self.url + '?' + encoded_data)
        result = response.read()
        self.check(result)
        return result

    def check(self, result):
        """Check result of API and raise error if error code detected
        """
        if re.match('00\d\d \w+', result):
            raise CaptchaError('API error: ' + result)

if __name__ == '__main__':
    try:
        api_key = sys.argv[1]
        filename = sys.argv[2]
    except IndexError:
        print 'Usage: %s <API key> <Image filename>' % sys.argv[0]
    else:
        main(api_key, filename)

```

