from setuptools import setup, find_packages

setup(
    name='ActivityWatch',
    version='1.0',
    packages=find_packages(),
    install_requires=[ 'Django', 'matplotlib' ]
)