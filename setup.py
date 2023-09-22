from setuptools import setup, find_packages

setup(
    name="ATTools",
    version="0.2.0",
    packages=["ATTools"],
    install_requires=[
        'asyncio',
        'aiohttp',
        'tonconnect',
        'dedust',
        'xjet',
        'tontools',
        'tonsdk'     
    ],
    project_urls={
        'Documentation': 'https://github.com/BEWARETHEDEAD/ATTools/tree/main'
    },
    python_requires='>=3.7',
)
