# -*- coding: utf-8 -*-

import os
import shutil


class Dotfile(object):

    def __init__(self, name, target):
        if name.startswith('/'):
            self.name = name
        else:
            self.name = os.path.expanduser('~/.%s' % name.strip('.'))
        self.basename = os.path.basename(self.name)
        self.target = target.rstrip('/')
        self.status = ''
        if not os.path.lexists(self.name):
            self.status = 'missing'
        elif os.path.realpath(self.name) != self.target:
            self.status = 'unmanged'

    def sync(self):
        if self.status == 'missing':
            os.symlink(self.target, self.name)

    def add(self):
        if self.status == 'missing':
            print "Skipping \"%s\", file not found" % self.basename
            return
        if self.status == '':
            print "Skipping \"%s\", already managed" % self.basename
            return
        print "Adding \"%s\"" % self.basename
        shutil.move(self.name, self.target)
        os.symlink(self.target, self.name)

    def remove(self):
        if self.status != '':
            print "Skipping \"%s\", file is %s" % (self.basename, self.status)
            return
        os.remove(self.name)
        shutil.move(self.target, self.name)

    def __str__(self):
        return '%-18s %-s' % (self.name.split('/')[-1], self.status)


class Dotfiles(object):

    def __init__(self, location, prefix, ignore, externals):
        self.location = location
        self.dotfiles = []
        contents = [x for x in os.listdir(self.location)
                    if x not in ignore]
        for file in contents:
            self.dotfiles.append(Dotfile(file,
                os.path.join(self.location, file)))
        for file in externals.keys():
            self.dotfiles.append(Dotfile(file, externals[file]))

    def list(self, **kwargs):
        for dotfile in sorted(self.dotfiles,
                key=lambda dotfile: dotfile.name):
            if dotfile.status or kwargs.get('verbose', True):
                print dotfile

    def check(self, **kwargs):
        self.list(verbose=False)

    def sync(self, **kwargs):
        for dotfile in self.dotfiles:
            dotfile.sync()

    def add(self, **kwargs):
        for file in kwargs.get('files', None):
            if os.path.basename(file).startswith('.'):
                Dotfile(file,
                        os.path.join(self.location,
                                    os.path.basename(file).strip('.'))).add()
            else:
                print "Skipping \"%s\", not a dotfile" % file

    def remove(self, **kwargs):
        for file in kwargs.get('files', None):
            if os.path.basename(file).startswith('.'):
                Dotfile(file,
                        os.path.join(self.location,
                            os.path.basename(file).strip('.'))).remove()
            else:
                print "Skipping \"%s\", not a dotfile" % file
