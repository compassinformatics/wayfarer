import re
from setuptools import setup
from io import open

(__version__,) = re.findall('__version__ = "(.*)"', open("wayfarer/__init__.py").read())


def readme():
    with open("README.rst", "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="wayfarer",
    version=__version__,
    description="A library to add spatial functions to networkx",
    long_description=readme(),
    classifiers=[
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
    ],
    url="http://www.compass.ie",
    author="Seth Girvin",
    author_email="sgirvin@compass.ie",
    license="MIT",
    packages=["wayfarer"],
    install_requires=["networkx>=3.0"],
    zip_safe=False,
)
