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
        "Programming Language :: Python :: 3.10",  # minimum required due to use of annotations
        "Intended Audience :: Developers",
    ],
    url="https://github.com/compassinformatics/wayfarer/",
    author="Seth Girvin",
    author_email="sgirvin@compass.ie",
    license="MIT",
    package_data={"wayfarer": ["py.typed"]},
    packages=["wayfarer"],
    install_requires=["networkx>=3.0", "geojson"],
    zip_safe=False,
)
