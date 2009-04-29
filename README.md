MGPages (Markdown-Git-Pages)
===========================

A post-receive githook which updates static html files on a webserver when 
Markdown text files are pushed to the remote repository on that same server.

Get the Code
------------

The code is maintained on github at <http://github.com/waylan/MGPages/tree>. To clone the repo, do:

    git clone git://github.com/waylan/MGPages.git

Installation and Setup
----------------------

MGPages is only a script which is called by git when a remote push is received.
Therefore, there is no need to run a setup script. However, as the script is
written in Python, a recent version of [Python][] (2.5 or 2.6) will need to be 
installed on your system.

You will also need the Python wrapper for git; [GitPython][]. The easiest way 
to install GitPython is to use setuptools:

    sudo easy_install gitpython

Now you will want to place a copy of the script in a place where your git repo 
can find it. As the script is specific to each repo (as it includes settings 
specific to its repo), I would suggest placing it in the hooks directory of the
repo (i.e.: /path/to/myrepo.git/hooks/mgpages.py).

Note that in the example above the repo is "myrepo.git" rather than 
"myrepo/.git". It is assumed that the repo will be a remote repo with no 
working tree. Although it could contain a working tree, the script will not
update that tree, so you will need to provide an additional script to update 
the working tree as well. That may be a convenient way to provide both the 
source text files and html files to your sites users, but is left as an 
exercise for the reader.

After copying the mgpages.py script, ensure that it is executable:

    chmod +x mgpages.py

Due to the need to unset the GITDIR environment variable, the mgpages.py script 
needs to be called by a shell/bash script. If you do not have any post-receive 
hook in your repo yet, you can simply copy the "sample-post-receive" script
to "hooks/post-receive", check that the paths are set correctly in the script,
and make it executable. If you already have a post-receive script, you can 
either copy the contents of the sample script into your script, or have one call
the other. See the comments in the sample for how to do that.

The final step in setting the script up is to open mgpages.py in your favorite
text editor and adjust the global settings to point to your repo and server 
root.

You are now ready to use your repo.

Usage
-----

Once the repo is set up, simply make a clone of that repo, edit/add/delete text
files in Markdown format and commit to the clone as normal. Once you are ready,
push those changes to the remote server as normal (`git push <remote> <branch>`)
and the text files will automatically be run through Markdown and written to the
server root as html files while maintaining the same directory structure as the
text files in the repo.

Settings
--------

For more fine grained control, you can also commit a "settings.conf" file to the
root directory of the repo. That way, any changes to your settings will be
tracked by version control as well.

The settings file should use the ini format. All currently supported settings
should be under the "[DEFAULT]" (all caps) section. The supported settings are:

* __"template"__: The name of the template file. Defaults to "template.html".
* __"output_format"__: Markdown's output format. One of "html4" (default) or
  "xhtml".
* __"source_extension"__: File extension for source text files. Defaults to 
  "txt".
* __"branch"__: Branch of the repo to use. Defaults to "master".

Templates
---------

You will also need an html template that at least contains html header and 
body sections. Currently, only python formated strings are permitted, with the
named variables "title" and "body" passed in. The simplest template would look
something like this:

    <html>
      <head>
        <title>%(title)s</title>
      </head>
      <body>
        %(body)s
      </body>
    </html>

The template should be committed to the root directory of your repo in a file 
named "template.html", although the name can be overridden in the settings file.

[Python]: http://python.org
[GitPython]: http://pypi.python.org/pypi/GitPython/
