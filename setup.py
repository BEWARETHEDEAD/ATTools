from setuptools import setup, find_packages

setup(
    name="ATools",
    version="0.1",
    packages=["ATools"],
    install_requires=[
        'tontools',
        'xjet',
        'dedust',
        'tonconnect',
        'aiohttp',
        'asyncio',
    ],
    python_requires='>=3.7',
)