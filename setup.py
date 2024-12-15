from setuptools import setup, find_packages

setup(
    name="steam_prices",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
        "numpy",
    ],
)
