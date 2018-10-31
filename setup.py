from __future__ import with_statement
from setuptools import setup

setup(
    name='xml_search',
    version='0.1',
    description="xml search with XPath that doesn't fill me with inhuman rage",
    url='https://github.com/ryantownshend/xml_search',
    author='Ryan Townshend',
    author_email='citizen.townshend@gmail.com',
    install_requires=[
        'click>=7.0',
        'click-log>=0.3.2',
        'lxml>=3.7.3',
    ],
    py_modules=['xml_search'],
    packages=['xml_search'],
    entry_points={
        'console_scripts': [
            'xml_search = xml_search.xml_search:cli',
        ],
    },
)
