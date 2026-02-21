from setuptools import find_packages, setup

setup(
    packages=find_packages(),
    entry_points={"console_scripts": ["artiq_cored = artiq_cored.cli:main"]},
)
