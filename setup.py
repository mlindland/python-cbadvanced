#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    "requests>=2.20",
    "PyJWT>=2.10.1",
    "cryptography==45.0.4",
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="cbadvanced",
    version="2.0.0",
    author="Magnus Lindland",
    author_email="magnuslindland@proton.me",
    license="MIT",
    url="https://github.com/mlindland/python-cbadvanced.git",
    packages=find_packages(),
    install_requires=install_requires,
    description="The unofficial Python client for the Coinbase Advanced Trade API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url="https://github.com/mlindland/python-cbadvanced/archive/refs/heads/master.zip",
    keywords=[
        "orderbook",
        "trade",
        "bitcoin",
        "ethereum",
        "BTC",
        "ETH",
        "client",
        "api",
        "wrapper",
        "exchange",
        "crypto",
        "currency",
        "trading",
        "trading-api",
        "coinbase",
        "advanced",
        "prime",
        "coinbaseadvanced",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
)
