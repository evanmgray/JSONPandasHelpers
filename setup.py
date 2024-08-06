from setuptools import setup, find_packages

setup(
    name='JSONPandasHelpers',
    version='0.1',
    packages=find_packages(),
    install_requires=['pandas>=1.2.0','json>=2.0.0'],
    description='A collection of useful JSON functions',
    author='Evan Gray',
    author_email='evanmgray94@gmail.com',
    url='https://github.com/evanmgray/JSONPandasHelpers', 
)