from setuptools import setup
from dotfiles import __version__


setup(
    name='dotfiles',
    version=__version__,
    author='Jon Bernard',
    author_email='jbernard@jbernard.io',
    description='Easily manage your dotfiles',
    url='https://github.com/jbernard/dotfiles',
    long_description=(open('README.rst').read() + '\n\n' +
                      open('LICENSE.rst').read() + '\n\n' +
                      open('HISTORY.rst').read()),
    license='ISC',
    packages=['dotfiles'],
    setup_requires=[
        'pytest-runner',
        'flake8',
    ],
    install_requires=[
        'click',
        'py',
    ],
    tests_require=[
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'dotfiles=dotfiles.cli:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)'
    ],
)
