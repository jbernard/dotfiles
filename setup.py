from setuptools import setup, find_packages
from dotfiles import __version__

setup(
    name='dotfiles',
    version=__version__,
    description='Easily manage your dotfiles',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Jon Bernard',
    author_email='jbernard@jbernard.io',
    license='ISC',
    url='https://github.com/jbernard/dotfiles',
    packages=find_packages(),
    tests_require=[
        'pytest',
        'pytest-flake8',
    ],
    setup_requires=['pytest-runner'],
    entry_points={
        'console_scripts': [
            'dotfiles=dotfiles.cli:cli',
        ],
    },
    install_requires=['click'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)'
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/jbernard/dotfiles/issues',
        'Source': 'https://github.com/jbernard/dotfiles',
    },
)
