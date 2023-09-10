from setuptools import setup, find_packages

setup(
    name="ATools",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'tontools',
        'xjet',
        'dedust',
        'tonconnect',
        'aiohttp',
        'asyncio',
    ],
)
