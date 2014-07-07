import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('dotfiles/core.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(name='dotfiles',
      version=__version__,
      description='Easily manage your dotfiles',
      long_description=open('README.rst').read() + '\n\n' +
                       open('LICENSE.rst').read() + '\n\n' +
                       open('HISTORY.rst').read(),
      author='Jon Bernard',
      author_email='jbernard@tuxion.com',
      url='https://github.com/jbernard/dotfiles',
      packages=['dotfiles'],
      license='ISC',
      classifiers=(
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: ISC License (ISCL)'
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.0',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
      ),
    entry_points = '''
        [console_scripts]
        dotfiles=dotfiles.cli:main
    ''',
)
