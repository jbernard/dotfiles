import io
import re
from setuptools import setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("dotfiles/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = \'(.*?)\'", f.read()).group(1)

setup(
    name='dotfiles',
    version=version,
    url='https://github.com/jbernard/dotfiles',
    project_urls={
        'Code': 'https://github.com/jbernard/dotfiles',
        'Issues': 'https://github.com/jbernard/dotfiles/issues',
    },
    license='ISC',
    author='Jon Bernard',
    author_email='jbernard@jbernard.io',
    description='Easily manage your dotfiles',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=["dotfiles"],
    python_requires=">=3.6",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)'
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
    install_requires=['click'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-flake8'],
    entry_points={
        'console_scripts': [
            'dotfiles=dotfiles.cli:cli',
        ],
    },
)
