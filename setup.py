from setuptools import setup, find_packages

setup(
    name='hyggepowermeter',
    version='1.0-1',
    description='A program for reading power meter data',
    author='Julian Arroyave',
    author_email='julian@hygge.energy',
    url='www.hygge.energy',
    packages=find_packages(),
    install_requires=[
        'pymodbus==2.5.3',
        'paho-mqtt~=1.6.1',
    ],
    entry_points={
        'console_scripts': [
            'hyggepowermeter = hyggepowermeter.main:main'
        ]
    }
)