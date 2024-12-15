from setuptools import setup, find_packages

setup(
    name="steamwebapi_prices",
    version="0.5",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
        "numpy",
    ],
)
