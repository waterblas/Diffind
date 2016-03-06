try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    print 'Auto install requires failed'

setup(
    name='CrawlServer',
    version='0.1dev',
    author='Donovan Liang',
    author_email='me@forldy.com',
    packages=['crawlstuff', 'commonstuff'],
    package_dir={
        'crawlstuff': '../crawlstuff', 
        'commonstuff': '../commonstuff'
    },
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Useful crawl-related stuff.'
)