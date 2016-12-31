# WebScrapingWithPython
# 1.网络爬虫简介/ 
介绍了网络爬虫，并讲解了爬取网站的方法。


# Install
This app relies on the web2py framework, which can be downloaded here and is documented here.
In the shell the installation instructions are as follows:

```
    # first download web2py
    wget http://www.web2py.com/examples/static/web2py_src.zip
    unzip web2py_src.zip
    # now download the app
    cd web2py/applications
    hg clone ssh://hg@bitbucket.org/wswp/places
    # now start the web2py server with a password for the admin interface
    cd ..
    python web2py.py --password=<password>
```
The places app can now be accessed in your web browser at http://127.0.0.1:8000/places.
