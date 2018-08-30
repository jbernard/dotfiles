from setuptools import setup
from dotfiles import __version__


setup(
    name='dotfiles',
    version=__version__,
    author='Jon Bernard',
    author_email='jbernard@jbernard.io',
    description='Easily manage your dotfiles',
    url='https://github.com/jbernard/dotfiles',
    long_description_content_type='text/markdown',
    long_description=(open('README.md').read() + '\n\n' +
                      open('LICENSE.md').read() + '\n\n' +
                      open('HISTORY.md').read()),
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
