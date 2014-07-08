import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('dotfiles/core.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='dotfiles',
    author='Jon Bernard',
    author_email='jbernard@tuxion.com',
    version=version,
    url='https://github.com/jbernard/dotfiles',
    packages=['dotfiles'],
    description='Easily manage your dotfiles',
    long_description=open('README.rst').read() + '\n\n' +
                     open('LICENSE.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
    entry_points = '''
        [console_scripts]
        dotfiles=dotfiles.cli:main
    ''',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)'
    ],
)
