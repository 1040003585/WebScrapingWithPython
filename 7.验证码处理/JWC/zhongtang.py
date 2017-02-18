#-*-coding=utf-8-*-
__author__='zhongtang'

import urllib
import urllib2
import cookielib
import math
import random
import time
import os
import htmltool
from pytesseract import *
from PIL import Image
from PIL import ImageEnhance
import re

class orclnypcg:
    def __init__(self):
        self.baseUrl='http://jbywcg.****.com.cn'
        self.ht=htmltool.htmltool()
        self.curPath=self.ht.getPyFileDir()
        self.authCode=''
        
    def initUrllib2(self):
        try:
            cookie = cookielib.CookieJar()
            cookieHandLer = urllib2.HTTPCookieProcessor(cookie)
            httpHandLer=urllib2.HTTPHandler(debuglevel=0)
            httpsHandLer=urllib2.HTTPSHandler(debuglevel=0)
        except:
            raise
        else:
             opener = urllib2.build_opener(cookieHandLer,httpHandLer,httpsHandLer)
             opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')]
             urllib2.install_opener(opener)
             
    def urllib2Navigate(self,url,data={}):           #定义连接函数，有超时重连功能
        tryTimes = 0
        while True:
            if (tryTimes>20):
                print u"多次尝试仍无法链接网络，程序终止"
                break
            try:
                if (data=={}):
                    req = urllib2.Request(url)
                else:
                    req = urllib2.Request(url,urllib.urlencode(data))
                response =urllib2.urlopen(req)
                bodydata = response.read()
                headerdata = response.info()
                if headerdata.get('Content-Encoding')=='gzip':
                    rdata = StringIO.StringIO(bodydata)
                    gz = gzip.GzipFile(fileobj=rdata)
                    bodydata = gz.read()
                    gz.close()
                tryTimes = tryTimes +1
            except urllib2.HTTPError, e:
              print 'HTTPError[%s]\n' %e.code                
            except urllib2.URLError, e:
              print 'URLError[%s]\n' %e.reason    
            except socket.error:
                print u"连接失败，尝试重新连接"
            else:
                break
        return bodydata,headerdata
    
    def randomCodeOcr(self,filename):
        image = Image.open(filename)
        #使用ImageEnhance可以增强图片的识别率
        #enhancer = ImageEnhance.Contrast(image)
        #enhancer = enhancer.enhance(4)
        image = image.convert('L')
        ltext = ''
        ltext= image_to_string(image)
        #去掉非法字符，只保留字母数字
        ltext=re.sub("\W", "", ltext)
        print u'[%s]识别到验证码:[%s]!!!' %(filename,ltext)
        image.save(filename)
        #print ltext
        return ltext

    def getRandomCode(self):
        #开始获取验证码
        #http://jbywcg.****.com.cn/CommonPage/Code.aspx?0.9409255818463862
        i = 0 
        while ( i<=100):
            i += 1 
            #拼接验证码Url
            randomUrlNew='%s/CommonPage/Code.aspx?%s' %(self.baseUrl,random.random())
            #拼接验证码本地文件名
            filename= '%s.png' %(i)
            filename=  os.path.join(self.curPath,filename)
            jpgdata,jpgheader = self.urllib2Navigate(randomUrlNew)
            if len(jpgdata)<= 0 :
                print u'获取验证码出错！\n'
                return False
            f = open(filename, 'wb')
            f.write(jpgdata)
            #print u"保存图片:",fileName
            f.close()
            self.authCode = self.randomCodeOcr(filename)


#主程序开始
orcln=orclnypcg()
orcln.initUrllib2()
orcln.getRandomCode()
