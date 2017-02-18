# -*- coding: utf-8 -*-
import urllib2
#验证码的处理#
#验证码生成页面的地址#
im_url = 'http://bbs.hzu.edu.cn:8080/jwweb/sys/ValidateCode.aspx'
#读取验证码图片#
im_data = urllib2.urlopen(im_url).read()
print im_data
#打开一个Code.PNG文件在D盘，没有的话自动生成#
f=open('code.png','wb')
#写入图片内容#
f.write(im_data)
#关闭文件#
f.close()

#http://www.th7.cn/Program/Python/201506/462836.shtml
#http://www.cnblogs.com/zhongtang/p/5560361.html
