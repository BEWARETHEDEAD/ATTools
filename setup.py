from setuptools import setup, find_packages

setup(
    name="ATools",
    version="0.1.2",
    packages=["ATools"],
    install_requires=[
        'asyncio',
        'aiohttp',
        'tonconnect',
        'dedust',
        'xjet',
        'tontools',     
    ],
    python_requires='>=3.7',
)
