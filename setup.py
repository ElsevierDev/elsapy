from distutils.core import setup
from setuptools import find_packages
from elsapy.__init__ import version

setup(
    name = 'elsapy',
    version = version,
    description = "A Python module for use with Elsevier's APIs: Scopus, ScienceDirect, others - see https://api.elsevier.com",
    long_description = "See https://github.com/ElsevierDev/elsapy for the latest information / background to this project.",
    author = 'Elsevier, Inc.',
    author_email = 'integrationsupport@elsevier.com',
    url = 'https://github.com/ElsevierDev/elsapy',
    license = 'License :: OSI Approved :: BSD License',
    download_url = 'https://www.github.com/ElsevierDev/elsapy/archive/0.4.6.tar.gz',
    keywords = ['elsevier api', 'sciencedirect api', 'scopus api'], # arbitrary keywords
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
    packages = find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires = ['requests']
)