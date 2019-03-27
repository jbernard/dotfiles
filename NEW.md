# Things to know about the next version

* arbitrary nesting levels are supported, which means only the files
  themselves are stored in the repository at whatever level of nesting
  they’re found. This makes the whole packages feature completely go
  away.  For example, if you add `~/.config/nvim/init.vim`, this file
  get’s linked and the directory structure is mirrored in the
  repository. So some files in a directory can be managed while others
  are either unmanaged or members of a different repository.

* multiple repositories are supported. You can use the -r flag (see
  dotfiles -h) to define repository locations (or use DOTFILES_REPOS
  environment variable). It’s a colon-separated string, so you can
  define and use multiple repositories by placing a : between them. The
  status command will show you everything, the other commands will ask
  you to specify one repository if multiple a given. This will improve
  soon, if a particular file is a member of exactly one of the available
  repositories, it can be assumed that that’s the one you meant (but
  this isn’t coded yet).

* Support for symlink or copies is nearly done. When you add or enable a
  dotfile, you can specify —copy and the file will be copied instead of
  symlinked. Symlink is the default. I still need to commit this, but
  status support is there. For status of a copied file, dotfiles will
  compare the contents of the two files and tell you in the output if
  the contents are different (a conflict).

* External symlinks are supported, no more external configuration, it
  does the right thing. So if you you add ~/.xsession-errors and that
  file is symlinked to /dev/null, that’s fine, dotfiles will handle that
  without needing to know any more.

* There is no configuration file. I tried to either implement the
  features transparently or remove them to reduce the complexity.
  Generally there are less tunables, but dotfiles is smarter where
  possible.

* The UI has changed, I’m using click now, so the command line is more
  similar to git-style. See dotfiles -h. There are 5 commands: status,
  add, remove, enable, and disable. Each one of them has a few specific
  flags, which you can see by typing dotfiles add -h, for example.
  Global commands should be given before the action, so something like
  this would define a repository and ask status to show everything:
  dotfiles -r ~/my-repo status -a.

* If you want to perform an action on all files within a certain sub
  directory, you can use that directory as an argument and dotfiles will
  expand it internally. So, dotfiles add ~/.ssh will add all files below
  the .ssh directory. And dotfiles enable ~/.config/nvim will create
  links for all neovim configuration files. I’m working on a few corner
  cases here, so there may be some bugs at the moment.

* Every action accepts a debug flag -d, —debug that will show you want
  commands dotifiles would execute without actually executing anything.
  This is helpful to see what’s going to happen and identify logic flaws
  if something doesn’t look right. For example, dotfiles add -d
  ~/.gitconfig will print commands without making any changes to the
  file system.

* The tests are really broken right now from the refactoring, I need to
  fix them, don’t be too alarmed by pytest’s complaints.
 
* Click supports shell completions for bash and zsh, I need to test and
  document that.  The status command has colors if you like colors
  (disabled by default).

# Installation

* Install using pip into a virtual env
 - create a virtual environment pip install
 - git+https://github.com/jbernard/dotfiles
 
* install using pip from a local checkout:
 - create a virtual environment
 - cd dotfiles
 - pip install -e .
 
* Run from a local checkout without a venv:
 - clone the repository
 - git submodule update —init
 - execute bin/dotfiles (it will look for the click submodule)
