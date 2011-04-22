Dotfile management made easy
============================

``dotfiles`` is a tool to make managing your dotfile symlinks in ``$HOME``
easy,  allowing you to keep all your dotfiles in a single directory.

Hosting is left to you. Yes, I've seen `<http://dotfiles.org>`_ and I don't
believe in that model. If you're advanced enough to need dotfile management,
then you probably already know how you want to host them.  Using whatever VCS
you prefer, or even rsync, you can easily distribute your dotfiles repository
across multiple hosts.

Installation
------------

To install dotfiles, simply: ::

    $ pip install dotfiles

Or, if you absolutely must: ::

    $ easy_install dotfiles

But, you really shouldn't do that.

If you want to work with the latest version, you can install it from `the
repository`_::

    $ git clone https://github.com/jbernard/dotfiles
    $ cd dotfiles
    $ ./bin/dotfiles --help

Examples
--------

To install your dotfiles on a new machine, you might do this: ::

  $ git clone https://github.com/me/my-dotfiles Dotfiles
  $ dotfiles --sync

To add '~/.vimrc' to your repository: ::

  $ dotfiles --add ~/.vimrc     (relative paths work also)

To make it available to all your hosts: ::

  $ cd ~/Dotfiles
  $ git add vimrc
  $ git commit -m "Added vimrc, welcome aboard!"
  $ git push

You get the idea.

License
-------

GPL License. ::

    Copyright (C) 2011  Jon Bernard

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Contribute
----------

If you'd like to contribute, simply fork `the repository`_, commit your changes
and send a pull request.

.. _`the repository`: https://github.com/jbernard/dotfiles
