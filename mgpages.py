#!/usr/bin/python
"""
MGPages
=======

A post-receive githook which updates static html files from Markdown text files
pushed to the repository.

This script is run after receive-pack has accepted a pack and the repository 
has been updated.  It is passed arguments in through stdin in the form
    <oldrev> <newrev> <refname>
For example:
    aa453216d1b3e49e7f6f98441fa56946ddcd6a20 68f7abf4e6f922807889f52bc043ecd31b79f814 refs/heads/master

Copyright (c) 2009, Waylan Limberg
All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this 
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, 
  this list of conditions and the following disclaimer in the documentation 
  and/or other materials provided with the distribution.
* Neither the name of the <ORGANIZATION> nor the names of its contributors may 
  be used to endorse or promote products derived from this software without 
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
from git import Repo 
from sets import Set
import markdown
import ConfigParser
import StringIO

# GLOBAL SETTINGS
# ===============

SERVER_ROOT = '/path/to/server/root'
REPO = '/path/to/repo.git'
CONFIG_FILE = 'settings.conf'

# DEFAULT CONFIG
# ==============
# These are the basic defaults when no settings file is provided in the repo.

DEFAULT_CONFIG = {
    'template': 'template.html',
    'output_format': 'html4',
    'source_extension': 'txt',
    'branch': 'master'
}

repo = Repo(REPO)
tree = repo.tree()


def get_config():
    """ Return config settings. """
    blob = tree/CONFIG_FILE
    config = ConfigParser.SafeConfigParser(DEFAULT_CONFIG)
    if blob:
        config.readfp(StringIO.StringIO(blob.data))
    print "No settings file. Using defaults."
    return config

CONFIG = get_config()

def get_files(refs):
    """ Return a list of changed file names given a list of git refs. """
    updates = Set()
    for ref in refs:
        old, new, name = ref.split(' ')
        #print old, new, name # TODO remove debug line
        # Only run in master branch
        if name.strip() == 'refs/heads/%s' % CONFIG.get('DEFAULT', 'branch'):
            commits = repo.commits_between(old, new)
            for commit in commits: 
                # Get diffs for commit
                for diff in commit.diffs:
                    # Get file path from diff 
                    # TODO: detect file move and better delete handleing
                    if diff.b_path.endswith( \
                            '.%s' % CONFIG.get('DEFAULT', 'source_extension')):
                        updates.add(diff.b_path)
        #print updates # TODO remove remove debug line
    return updates


def get_html_path(path):
    """ Return full path to html file given corresponding txt file name. """
    ext = '.%s' % CONFIG.get('DEFAULT', 'source_extension')
    if path.endswith(ext):
        return os.path.join(SERVER_ROOT, '%s.html' % (path[:-len(ext)]))


def update(files):
    """ Given a list of txt files, update corresponding html files. """
    if files: 
        print 'Updating %d HTML files...' % len(files)
    for file in files:
        # get file and run through markup
        print '    Examining file: "%s"' % file # TODO remove debug line
        html_file = get_html_path(file)
        if html_file:
            blob = tree/file
            if blob:
                print '    Writing file: "%s"' % html_file
                out = build_html(blob.data)
                # output html
                f = open(html_file, 'w')
                f.write(out)
                f.close()
            else:
                print '    Deleting file: "%s"' % html_file
                try:
                    os.remove(html_file)
                except OSError:
                    # File doesn't exist - fail silently.
                    pass


def build_html(text):
    """ Pass text through Markdown and template and return result. """
    md = markdown.Markdown(
        extensions = ['extra', 'meta'], 
        output_format = CONFIG.get('DEFAULT', 'output_format'),
    )
    body = md.convert(text)
    temp = tree/CONFIG.get('DEFAULT', 'template')
    if temp:
        #print 'Using template: "%s"' % temp.name # TODO remove debug line
        return temp.data % {'body': body, 'title': md.Meta['title'][0]}
    return body


if __name__ == '__main__':
    update(get_files(sys.stdin.readlines()))
