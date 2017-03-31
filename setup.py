from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent/"README.rst").read_text()

setup(
    name='clux',
    version='1.0',

    description='Command-Line User Experience',
    long_description=long_description,
    url='https://github.com/pypa/sampleproject',
    author='S.Lott',
    author_email='slott56@gmail.com',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    py_modules=["clux"],
)
