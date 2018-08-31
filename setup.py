import io
from setuptools import setup
from dotfiles import __version__


with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='dotfiles',
    version=__version__,
    author='Jon Bernard',
    author_email='jbernard@jbernard.io',
    url='https://github.com/jbernard/dotfiles',
    description='Easily manage your dotfiles',
    long_description_content_type='text/markdown',
    long_description=readme,
    license='ISC',
    packages=['dotfiles'],
    extras_require={
        'dev': [
            'pytest',
            'flake8',
        ],
    },
    # setup_requires=[
    #     'pytest-runner',
    #     'flake8',
    # ],
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
