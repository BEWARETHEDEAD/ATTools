from setuptools import setup, find_packages

setup(
    name="ATTools",
    version="0.1.5",
    packages=["ATTools"],
    install_requires=[
        'asyncio',
        'aiohttp',
        'tonconnect',
        'dedust',
        'xjet',
        'tontools',     
    ],
    project_urls={
        'Documentation': 'https://github.com/BEWARETHEDEAD/ATTools/tree/main'
    },
    python_requires='>=3.7',
)
