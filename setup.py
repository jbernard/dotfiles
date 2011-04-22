from distutils.core import setup
import dotfiles

setup(name='dotfiles',
      version=dotfiles.__version__,
      description='Easily manage your dotfiles',
      long_description=open('README.rst').read(),
      author='Jon Bernard',
      author_email='jbernard@tuxion.com',
      url='https://github.com/jbernard/dotfiles',
      packages=['dotfiles'],
      license='GPL',
      classifiers=(
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Programming Language :: Python',
      ),
      scripts=['bin/dotfiles'],
)
