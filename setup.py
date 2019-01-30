from setuptools import setup

setup(
    name='rulebook',
    version='0.0.1',
    packages=['rulebook'],
    url='https://github.com/hmelberg/rulebook',
    license='MIT',
    author='Hans Olav Melberg',
    author_email='hans.melberg@gmail.com',
    description='Validate and revise Pandas dataframes',
    install_requires=['pandas']
)
