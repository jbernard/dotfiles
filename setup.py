from setuptools import setup
from dotfiles import __version__


setup(
    name='dotfiles',
    version=__version__,
    author='Jon Bernard',
    author_email='jbernard@tuxion.com',
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
            'dotfiles=dotfiles.dotfiles:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: ISC License (ISCL)'
    ],
)
