try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    print 'Auto install requires failed'
# yum install python-devel for missing #include "Python.h"
setup(
    name='CrawlClient',
    version='0.1dev',
    author='Donovan Liang',
    author_email='me@forldy.com',
    packages=['crawlstuff', 'commonstuff'],
    package_dir={
        'crawlstuff': '../crawlstuff', 
        'commonstuff': '../commonstuff'
    },
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Useful crawl-related stuff.',
    install_requires=[
        "requests >= 2.8.1",
        "robotexclusionrulesparser == 1.6.2",
        "beautifulsoup4 >= 4.4.1",
        "pymongo >= 3.1.1",
        "pybloom >= 1.1"
    ]
)