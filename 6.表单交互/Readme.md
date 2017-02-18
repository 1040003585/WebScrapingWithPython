# 表单交互
[TOC]
严格来说，本篇表单交互和下一篇验证码处理不算是网络爬虫，而是广义上的网络机器人。使用网络机器人可以减少提取数据时需要表单交互的一道门槛。
# 1.手工处理发送POST请求提交登录表单
我们先在示例网站手工注册一个账号，注册这个账号需要验证码，下一篇会介绍处理验证码问题。
## 1.1分析表单内容
我们在登录网址http://127.0.0.1:8000/places/default/user/login 获得如下表单。在下面登录表单中包括几个重要的组成部分：
- form标签的action属性：用于设置表单数据提交的地址，本例中为`#`，也就是和登录表单同一个URL；
- form标签的enctype属性：用于设置数据提交的编码，本例中为`application/x-www-form-urlencoded`，表示所有非字母数字的字符都需要转换为十六进制的ASCII值；上传二进程文件最好用`multipart/form-data`编码类型，这种编码不会对输入进行编码从而不会影响效率，而是使用MIME协议将其作为多个部分进行发送，和邮件的传输标准相同。文档：http://www.w3.org/TR/html5/forms.html#selecting-a-form-submission-encoding 
- form标签的method属性：本例中`post`表示通过请求体向服务器提交表单数据；
- imput标签的name属性：用于设定提交到服务器端时某个域的名称。

```html
<form action="#" enctype="application/x-www-form-urlencoded" method="post">
	<table>
		<tr id="auth_user_email__row">
			<td class="w2p_fl"><label class="" for="auth_user_email" id="auth_user_email__label">E-mail: </label></td>
			<td class="w2p_fw"><input class="string" id="auth_user_email" name="email" type="text" value="" /></td>
			<td class="w2p_fc"></td>
		</tr>
		<tr id="auth_user_password__row">
			<td class="w2p_fl"><label class="" for="auth_user_password" id="auth_user_password__label">Password: </label></td>
			<td class="w2p_fw"><input class="password" id="auth_user_password" name="password" type="password" value="" /></td>
			<td class="w2p_fc"></td>
		</tr>
		<tr id="auth_user_remember_me__row">
			<td class="w2p_fl"><label class="" for="auth_user_remember_me" id="auth_user_remember_me__label">Remember me (for 30 days): </label></td>
			<td class="w2p_fw"><input class="boolean" id="auth_user_remember_me" name="remember_me" type="checkbox" value="on" /></td>
			<td class="w2p_fc"></td>
		</tr>
		<tr id="submit_record__row">
			<td class="w2p_fl"></td><td class="w2p_fw">
				<input type="submit" value="Log In" />
				<button class="btn w2p-form-button" onclick="window.location=&#x27;/places/default/user/register&#x27;;return false">Register</button>
			</td>
			<td class="w2p_fc"></td>
		</tr>
	</table>
	<div style="display:none;">
		<input name="_next" type="hidden" value="/places/default/index" />
		<input name="_formkey" type="hidden" value="7b1add4b-fa91-4301-975e-b6fbf7def3ac" />
		<input name="_formname" type="hidden" value="login" />
	</div>
</form>
```
## 1.2手工测试post请求提交表单
如果登录成功则跳到主页，否则回到登录页。下面是尝试自动登录的初始版本代码。显然登录失败！
```python
>>> import urllib,urllib2
>>> LOGIN_URL='http://127.0.0.1:8000/places/default/user/login'
>>> LOGIN_EMAIL='1040003585@qq.com'
>>> LOGIN_PASSWORD='wu.com'
>>> data={'email':LOGIN_EMAIL,'password':LOGIN_PASSWORD}
>>> encoded_data=urllib.urlencode(data)
>>> request=urllib2.Request(LOGIN_URL,encoded_data)
>>> response=urllib2.urlopen(request)
>>> response.geturl()
'http://127.0.0.1:8000/places/default/user/login'
>>> 
```
因为登录时还需要添加隐藏的`_formkey`属性，这个唯一的ID用来避免表单多次提交。每次加载网页时，都会产生不同的ID，然后服务器端就可以通过这个给定的ID来判断表单是否已经通过提交过。下面是获得该属性值：
```python
>>> 
>>> import lxml.html
>>> def parse_form(html):
...     tree=lxml.html.fromstring(html)
...     data={}
...     for e in tree.cssselect('form input'):
...             if e.get('name'):
...                     data[e.get('name')]=e.get('value')
...     return data
... 
>>> import pprint
>>> html=urllib2.urlopen(LOGIN_URL).read()
>>> form=parse_form(html)
>>> pprint.pprint(form)
{'_formkey': '437e4660-0c44-4187-af8d-36487c62ffce',
 '_formname': 'login',
 '_next': '/places/default/index',
 'email': '',
 'password': '',
 'remember_me': 'on'}
>>> 
```
下面是通过`_formkey`和其他隐藏域的新版本自动登录代码。发现还是不成功！ 
```python
>>> 
>>> html=urllib2.urlopen(LOGIN_URL).read()
>>> data=parse_form(html)
>>> data['email']=LOGIN_EMAIL
>>> data['password']=LOGIN_PASSWORD
>>> encoded_data=urllib.urlencode(data)
>>> request=urllib2.Request(LOGIN_URL,encoded_data)
>>> response=urllib2.urlopen(request)
>>> response.geturl()
'http://127.0.0.1:8000/places/default/user/login'
>>> 
```
因为我们缺失了一个重要的组成部分——**cookie**。当普通用户加载登录表单时，`_formkey`的值将会保存在cookie中，然后该值会与提交的登录表单数据中的`_formkey`的值进行对比。下面是使用`urllib2.HTTPCookieProcessor`类增加了cookie支持之后的代码。最后登录成功了！
```python
>>> 
>>> import cookielib
>>> cj=cookielib.CookieJar()
>>> opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
>>> 
>>> html=opener.open(LOGIN_URL).read()		#opener
>>> data=parse_form(html)
>>> data['email']=LOGIN_EMAIL
>>> data['password']=LOGIN_PASSWORD
>>> encoded_data=urllib.urlencode(data)
>>> request=urllib2.Request(LOGIN_URL,encoded_data)
>>> response=opener.open(request)		#opener
>>> response.geturl()
'http://127.0.0.1:8000/places/default/index'
>>> 
```
## 1.3手工处理post请求登录的完整源代码：
```python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import lxml.html

LOGIN_EMAIL = '1040003585@qq.com'
LOGIN_PASSWORD = 'wu.com'
#LOGIN_URL = 'http://example.webscraping.com/user/login'
LOGIN_URL = 'http://127.0.0.1:8000/places/default/user/login'


def login_basic():
    """fails because not using formkey
    """
    data = {'email': LOGIN_EMAIL, 'password': LOGIN_PASSWORD}
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = urllib2.urlopen(request)
    print response.geturl()

def login_formkey():
    """fails because not using cookies to match formkey
    """
    html = urllib2.urlopen(LOGIN_URL).read()
    data = parse_form(html)
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
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
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
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

def main():
    #login_basic()
    #login_formkey()
    login_cookies()

if __name__ == '__main__':
    main()
```
# 2.从FF浏览器加载cookie登录网站
我们先用手工执行登录，我们先在FF浏览器用手工执行登录，然后关闭FF浏览器，然后用python脚本复用之前得到的cookie，从而实现自动登录。
## 2.1session文件位置
FireFox在sqlist数据库中存储cookie，在json文件中存储session，这两种存储方式都可以直接通过Python获取。对于登录操作而言，我们只需要获致session即可。对于不同的操作系统，FireFox存储的session文件的位置不同：
- Linux系统：`~/.mozilla/firefox/*.default/sessionstore.js`
- OS X系统：`~/Library/Application Support/Firefox/Profiles/*.default/sessionstore.js`
- Windows Vista及以上版本系统：`%APPDATA%/Roaming/Mozilla/Firefox/Profiles/*.default/sessionstore.js`

下面是返回session文件路径的辅助函数代码：
```python
def find_ff_sessions():
    paths = [
        '~/.mozilla/firefox/*.default',
        '~/Library/Application Support/Firefox/Profiles/*.default',
        '%APPDATA%/Roaming/Mozilla/Firefox/Profiles/*.default'
    ]
    for path in paths:
        filename = os.path.join(path, 'sessionstore.js')
        matches = glob.glob(os.path.expanduser(filename))
        if matches:
            return matches[0]
```
注：`glob`模块会返回指定路径中所有匹配的文件。
## 2.2FF浏览器cookie内容
下面是Linux系统火狐浏览器session文件内容：
```
wu_being@ubuntukylin64:~/.mozilla/firefox/78n340f7.default$ ls
addons.json           datareporting       key3.db             prefs.js                      storage
blocklist.xml         extensions          logins.json         revocations.txt               storage.sqlite
bookmarkbackups       extensions.ini      mimeTypes.rdf       saved-telemetry-pings         times.json
cert8.db              extensions.json     minidumps           search.json.mozlz4            webapps
compatibility.ini     features            permissions.sqlite  secmod.db                     webappsstore.sqlite
containers.json       formhistory.sqlite  places.sqlite       sessionCheckpoints.json       xulstore.json
content-prefs.sqlite  gmp                 places.sqlite-shm   sessionstore-backups
cookies.sqlite        gmp-gmpopenh264     places.sqlite-wal   sessionstore.js
crashes               healthreport        pluginreg.dat       SiteSecurityServiceState.txt
wu_being@ubuntukylin64:~/.mozilla/firefox/78n340f7.default$ more sessionstore.js 
{"version":["sessionrestore",1],
"windows":[{
	...
	"cookies":[
		{"host":"127.0.0.1",
		"value":"127.0.0.1-aabe0222-d083-44ee-94c8-e9343eefb2e5",
		"path":"/",
		"name":"session_id_welcome",
		"httponly":true,
		"originAttributes":{"addonId":"","appId":0,"inIsolatedMozBrowser":false,"privateBrowsingId":0,"signedPkg":"","userContextId":0}},
		{"host":"127.0.0.1",
		"value":"True",
		"path":"/",
		"name":"session_id_places",
		"httponly":true,
		"originAttributes":{"addonId":"","appId":0,"inIsolatedMozBrowser":false,"privateBrowsingId":0,"signedPkg":"","userContextId":0}},
		{"host":"127.0.0.1",
		"value":"\":oJoAPvH-ODMFDXwk3U...su0Dxr7doAgu9yQiSEmgQiSy98Ga7C6K2tIQoZwzY0_4wBO0qHm-FlcBf-cPRk7GPAhix8yS4roOVIvMqP5I7ZB_uIA==\"",
		"path":"/",
		"name":"session_data_places",
		"originAttributes":{"addonId":"","appId":0,"inIsolatedMozBrowser":false,"privateBrowsingId":0,"signedPkg":"","userContextId":0}}
	],
	"title":"Example web scraping website",
	"_shouldRestore":true,
	"closedAt":1485228738310
}],
"selectedWindow":0,
"_closedWindows":[],
"session":{"lastUpdate":1485228738927,"startTime":1485226675190,"recentCrashes":0},
"global":{}
}

wu_being@ubuntukylin64:~/.mozilla/firefox/78n340f7.default$ 
```
根据seesion存储结构，我们用下面代码把session解析到CookieJar对象中。
```python
def load_ff_sessions(session_filename):
    cj = cookielib.CookieJar()
    if os.path.exists(session_filename):  
        try: 
            json_data = json.loads(open(session_filename, 'rb').read())
        except ValueError as e:
            print 'Error parsing session JSON:', str(e)
        else:
            for window in json_data.get('windows', []):
                for cookie in window.get('cookies', []):
                    import pprint; pprint.pprint(cookie)
                    c = cookielib.Cookie(0, cookie.get('name', ''), cookie.get('value', ''), 
                        None, False, 
                        cookie.get('host', ''), cookie.get('host', '').startswith('.'), cookie.get('host', '').startswith('.'), 
                        cookie.get('path', ''), False,
                        False, str(int(time.time()) + 3600 * 24 * 7), False, 
                        None, None, {})
                    cj.set_cookie(c)
    else:
        print 'Session filename does not exist:', session_filename
    return cj
```
## 2.3使用cookie测试加载登录
```python
session_filename = find_ff_sessions()
cj = load_ff_sessions(session_filename)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
html = opener.open(COUNTRY_URL).read()

tree = lxml.html.fromstring(html)
print tree.cssselect('ul#navbar li a')[0].text_content()
```
如果得到的结果是`Login`则说明没能正确加载。如果出现这样情况，你就需要确认一下FireFox中是否已经成功登录救命网站。如果得到下面结果，有`Welcome 用户的first name`，则登录表示成功。
```json
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/6.表单交互$ python 2login_firefox.py 
{u'host': u'127.0.0.1',
 u'httponly': True,
 u'name': u'session_id_welcome',
 u'originAttributes': {u'addonId': u'',
                       u'appId': 0,
                       u'inIsolatedMozBrowser': False,
                       u'privateBrowsingId': 0,
                       u'signedPkg': u'',
                       u'userContextId': 0},
 u'path': u'/',
 u'value': u'127.0.0.1-406df419-ed33-4de5-bc46-cd2d9f3c431b'}
Log In
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/6.表单交互$ 
```
```json
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/6.表单交互$ python 2login_firefox.py 
{u'host': u'127.0.0.1',
 u'httponly': True,
 u'name': u'session_id_welcome',
 u'originAttributes': {u'addonId': u'',
                       u'appId': 0,
                       u'inIsolatedMozBrowser': False,
                       u'privateBrowsingId': 0,
                       u'signedPkg': u'',
                       u'userContextId': 0},
 u'path': u'/',
 u'value': u'127.0.0.1-aabe0222-d083-44ee-94c8-e9343eefb2e5'}
{u'host': u'127.0.0.1',
 u'httponly': True,
 u'name': u'session_id_places',
 u'originAttributes': {u'addonId': u'',
                       u'appId': 0,
                       u'inIsolatedMozBrowser': False,
                       u'privateBrowsingId': 0,
                       u'signedPkg': u'',
                       u'userContextId': 0},
 u'path': u'/',
 u'value': u'True'}
{u'host': u'127.0.0.1',
 u'name': u'session_data_places',
 u'originAttributes': {u'addonId': u'',
                       u'appId': 0,
                       u'inIsolatedMozBrowser': False,
                       u'privateBrowsingId': 0,
                       u'signedPkg': u'',
                       u'userContextId': 0},
 u'path': u'/',
 u'value': u'"ef34329782d4efe136522cb44fc4bd21:oJoAPvH-ODM...QiSy98Ga7C6K2tIQoZwzY0_4wBO0qHm-FlcBf-cPRk7GPAhix8yS4roOVIvMqP5I7ZB_uIA=="'}
Welcome Wu
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/6.表单交互$ 
```
如果你想从其他浏览器的cookie，可以使用`browsercookie`模块。通过`pip install browsercookie`命令进行安装，文档：https://pypi.python.org/pypi/browsercookie 
## 2.4使用cookie登录源代码
```python
# -*- coding: utf-8 -*-
import urllib2
import glob
import os
import cookielib
import json
import time
import lxml.html

COUNTRY_URL = 'http://127.0.0.1:8000/places/default/edit/China-47'

def login_firefox():
    """load cookies from firefox
    """
    session_filename = find_ff_sessions()
    cj = load_ff_sessions(session_filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(COUNTRY_URL).read()

    tree = lxml.html.fromstring(html)
    print tree.cssselect('ul#navbar li a')[0].text_content()
    return opener

def load_ff_sessions(session_filename):
    cj = cookielib.CookieJar()
    if os.path.exists(session_filename):  
        try: 
            json_data = json.loads(open(session_filename, 'rb').read())
        except ValueError as e:
            print 'Error parsing session JSON:', str(e)
        else:
            for window in json_data.get('windows', []):
                for cookie in window.get('cookies', []):
                    import pprint; pprint.pprint(cookie)
                    c = cookielib.Cookie(0, cookie.get('name', ''), cookie.get('value', ''), 
                        None, False, 
                        cookie.get('host', ''), cookie.get('host', '').startswith('.'), cookie.get('host', '').startswith('.'), 
                        cookie.get('path', ''), False,
                        False, str(int(time.time()) + 3600 * 24 * 7), False, 
                        None, None, {})
                    cj.set_cookie(c)
    else:
        print 'Session filename does not exist:', session_filename
    return cj

def find_ff_sessions():
    paths = [
        '~/.mozilla/firefox/*.default',
        '~/Library/Application Support/Firefox/Profiles/*.default',
        '%APPDATA%/Roaming/Mozilla/Firefox/Profiles/*.default'
    ]
    for path in paths:
        filename = os.path.join(path, 'sessionstore.js')
        matches = glob.glob(os.path.expanduser(filename))
        if matches:
            return matches[0]

def main():
    login_firefox()

if __name__ == '__main__':
    main()
```
# 3.使用高级模块Mechanize自动化处理表单提交
使用Mechanize模块可以简化表单提交，先如下安装：`pip install mechanize`
## 3.1用高级模块Mechanize自动化处理表单提交并支持登录后网页内容更新
```python
# -*- coding: utf-8 -*-
import mechanize
import login

#COUNTRY_URL = 'http://example.webscraping.com/edit/United-Kingdom-239'
COUNTRY_URL = 'http://127.0.0.1:8000/places/default/edit/China-47'

def mechanize_edit():
    """Use mechanize to increment population
    """
    # login
    br = mechanize.Browser()
    br.open(login.LOGIN_URL)
    br.select_form(nr=0)
    print br.form
    br['email'] = login.LOGIN_EMAIL
    br['password'] = login.LOGIN_PASSWORD
    response = br.submit()

    # edit country
    br.open(COUNTRY_URL)
    br.select_form(nr=0)
    print 'Population before:', br['population']
    br['population'] = str(int(br['population']) + 1)
    br.submit()

    # check population increased
    br.open(COUNTRY_URL)
    br.select_form(nr=0)
    print 'Population after:', br['population']

if __name__ == '__main__':
    mechanize_edit()
```
```xml
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/6.表单交互$ python 3mechanize_edit.py 
<POST http://127.0.0.1:8000/places/default/user/login# application/x-www-form-urlencoded
  <TextControl(email=)>
  <PasswordControl(password=)>
  <CheckboxControl(remember_me=[on])>
  <SubmitControl(<None>=Log In) (readonly)>
  <SubmitButtonControl(<None>=) (readonly)>
  <HiddenControl(_next=/places/default/index) (readonly)>
  <HiddenControl(_formkey=72282515-8f0d-4af1-9500-f7ac6f0526a4) (readonly)>
  <HiddenControl(_formname=login) (readonly)>>
Population before: 1330044000
Population after: 1330044001
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/6.表单交互$ 

```
文档：http://www.search.sourceforge.net/mechanize/ 
## 3.2用普通方法支持登录后网页内容更新

```python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import login

#COUNTRY_URL = 'http://example.webscraping.com/edit/United-Kingdom-239'
COUNTRY_URL = 'http://127.0.0.1:8000/places/default/edit/China-47'
	
def edit_country():
    opener = login.login_cookies()
    country_html = opener.open(COUNTRY_URL).read()
    data = login.parse_form(country_html)
    import pprint; pprint.pprint(data)
    print 'Population before: ' + data['population']
    data['population'] = int(data['population']) + 1
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(COUNTRY_URL, encoded_data)
    response = opener.open(request)

    country_html = opener.open(COUNTRY_URL).read()
    data = login.parse_form(country_html)
    print 'Population after:', data['population']

if __name__ == '__main__':
    edit_country()
```
```json
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/6.表单交互$ python 3edit_country.py 
http://127.0.0.1:8000/places/default/index
{'_formkey': '3773506a-ef5e-4c4a-871d-084cb8451659',
 '_formname': 'places/5087',
 'area': '9596960.00',
 'capital': 'Beijing',
 'continent': 'AS',
 'country': 'China',
 'currency_code': 'CNY',
 'currency_name': 'Yuan Renminbi',
 'id': '5087',
 'iso': 'CN',
 'languages': 'zh-CN,yue,wuu,dta,ug,za',
 'neighbours': 'LA,BT,TJ,KZ,MN,AF,NP,MM,KG,PK,KP,RU,VN,IN',
 'phone': '86',
 'population': '1330044001',
 'postal_code_format': '######',
 'postal_code_regex': '^(\\d{6})$',
 'tld': '.cn'}
Population before: 1330044001
Population after: 1330044002
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/6.表单交互$ 
```

