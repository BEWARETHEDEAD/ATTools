from setuptools import setup, find_packages

setup(
    name="ATTools",
    version="0.1.4",
    packages=["ATTools"],
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
