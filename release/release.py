#!/usr/bin/env python
# encoding: utf-8
"""
release.py

Created by Mahmood Ali on 2010-02-25.
Copyright (c) 2010 Jude LLC. All rights reserved.
"""

import sys
import getopt
import urllib2
import re
import subprocess
import os
import pwd

DEFAULT_SITE = "http://types.cs.washington.edu/jsr308/"
# OPENJDK_RELEASE_SITE = 'http://download.java.net/openjdk/jdk7/'
OPENJDK_RELEASE_SITE = 'http://jdk8.java.net/download.html'

def current_distribution(site=DEFAULT_SITE):
    """
    Returns the version of the current release of the checker framework

    """
    ver_re = re.compile(r"<!-- checkers-version -->(.*),")
    text = urllib2.urlopen(url=site).read()
    result = ver_re.search(text)
    return result.group(1)

def latest_openjdk(site=OPENJDK_RELEASE_SITE):
    ver_re = re.compile(r"Build b(\d+)")
    text = urllib2.urlopen(url=site).read()
    result = ver_re.search(text)
    return result.group(1)

def increment_version(version):
    """
    Returns a recommendation of the next incremental version based on the
    passed one.

    >>> increment_version('1.0.3')
    '1.0.4'
    >>> increment_version('1.0.9')
    '1.1.0'
    >>> increment_version('1.1.9')
    '1.2.0'
    >>> increment_version('1.3.1')
    '1.3.2'

    """
    parts = [int(x) for x in version.split('.')]
    parts[2] += 1
    if parts[2] > 9:
        parts[2] -= 10
        parts[1] += 1
    if parts[1] > 9:
        parts[1] -= 10
        parts[0] += 1
    return ".".join([str(x) for x in parts])

def site_copy(ant_args):
    execute("ant -e -f release.xml %s site-copy" % ant_args)

def site_copy_if_needed(ant_args):
    if not os.path.exists(DRY_PATH):
        return site_copy(ant_args)
    return True

def check_command(command):
    p = execute(['which', command], halt_if_fail=False)
    if p:
        raise AssertionError('command not found: %s' % command)

DEFAULT_PATHS = (
#    '/homes/gws/mernst/research/invariants/scripts',
    '/homes/gws/mernst/bin/share',
#    '/homes/gws/mernst/bin/share-plume',
    '/homes/gws/mernst/bin/Linux-i686',
    '/uns/bin',
    '/homes/gws/mali/local/share/maven/bin',
    '.',
)

def append_to_PATH(paths=DEFAULT_PATHS):
    current_PATH = os.getenv('PATH')
    new_PATH = current_PATH + ':' + ':'.join(paths)
    os.environ['PATH'] = new_PATH

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
JSR308_LANGTOOLS = os.path.join(REPO_ROOT, '..', 'jsr308-langtools')

# Is PLUME_LIB even necessary?
PLUME_LIB = os.path.join(os.getenv('HOME'), 'plume-lib')

# Do not include PLUME_LIB in PROJECT_ROOTS, because this script
# commits to all repositories in PROJECT_ROOTS.
# TODO: WMD changed this and requires explicit commits; this
# array is only used to update the projects.
PROJECT_ROOTS = (
    REPO_ROOT,                  # Checker Framework
    JSR308_LANGTOOLS,
)

def update_projects(paths=PROJECT_ROOTS):
    for path in paths:
        execute('hg -R %s pull' % path)
        execute('hg -R %s update' % path)
        print("Checking changes")
        # execute('hg -R %s outgoing' % path)

def commit_and_push(version, path, tag_prefix):
    execute('hg -R %s commit -m "new release %s"' % (path, version))
    execute('hg -R %s tag %s%s' % (path, tag_prefix, version))
    execute('hg -R %s push' % path)

def ensure_group_access(path="/cse/www2/types/"):
    # Errs for any file not owned by this user.
    # But, the point is to set group writeability of any *new* files.
    execute('chmod -f -R g+w %s' % path, halt_if_fail=False)

def file_contains(path, text):
    f = open(path, 'r')
    contents = f.read()
    f.close()
    return text in contents

def file_prepend(path, text):
    f = open(path)
    contents = f.read()
    f.close()

    f = open(path, 'w')
    f.write(text)
    f.write(contents)
    f.close()

def retrieve_changes(root, prev_version, prefix):
    return execute(
            "hg -R %s log -r %s%s:tip --template ' * {desc}\n'" %
                (root, prefix, prev_version),
                capture_output=True)

EDITOR = os.getenv('EDITOR')
if EDITOR == None:
    raise Exception('EDITOR environment variable is not set')
CHECKERS_CHANGELOG = os.path.join(REPO_ROOT, 'checkers', 'changelog-checkers.txt')

def edit_checkers_changelog(version, changes="", path=CHECKERS_CHANGELOG):
    edit = raw_input("Edit the Checker Framework changelog? [Y/n] ")
    if not (edit == "n"):
        if not file_contains(path, version):
            import datetime
            today = datetime.datetime.now().strftime("%d %b %Y")
            file_prepend(path,"""Version %s, %s


%s

----------------------------------------------------------------------
""" % (version, today, changes))
        execute([EDITOR, path])

def changelog_header_checkers(file=CHECKERS_CHANGELOG):
    return changelog_header(file)

LANGTOOLS_CHANGELOG = os.path.join(JSR308_LANGTOOLS, 'doc', 'changelog-jsr308.txt')

def edit_langtools_changelog(version, changes="", path=LANGTOOLS_CHANGELOG):
    latest_jdk = latest_openjdk()
    print("Latest OpenJDK release is b%s" % latest_jdk)
    edit = raw_input("Edit the JSR308 langtools changelog? [Y/n] ")
    if not (edit == "n"):
        if not file_contains(path, version):
            import datetime
            today = datetime.datetime.now().strftime("%d %b %Y")
            file_prepend(path, """Version %s, %s

Base build
  Updated to OpenJDK langtools build b%s

%s

----------------------------------------------------------------------
""" % (version, today, latest_jdk, changes))
        execute([EDITOR, path])

def changelog_header_langtools(file=LANGTOOLS_CHANGELOG):
    return changelog_header(file)

def make_release(version, ant_args, real=False, sanitycheck=True):
    command = 'ant -e -f release.xml %s -Drelease.ver=%s %s clean web %s' % (
        '-Drelease.is.real=true' if real else '',
        version,
        ant_args,
        'sanitycheck' if sanitycheck else '',
    )
    print("Actually making the release")
    return execute(command)

def checklinks(site_url=None):
    os.putenv('jsr308_www_online', site_url) # set environment var for subshell
    return execute('make -f %s checklinks' %
                     os.path.join(JSR308_LANGTOOLS, 'doc', 'Makefile'),
                   halt_if_fail=False)

MAVEN_GROUP_ID = 'types.checkers'
MAVEN_REPO = 'file:///cse/www2/types/m2-repo'

def mvn_deploy(name, binary, version, dest_repo=MAVEN_REPO, ):
    command = """
    mvn deploy:deploy-file
        -DartifactId=%s
        -Dfile=%s
        -Dversion=%s
        -Durl=%s
        -DgroupId=%s
        -Dpackaging=jar
        -DgeneratePom=true
    """ % (name, binary, version, dest_repo, MAVEN_GROUP_ID)
    return execute(command)

CHECKERS_BINARY = os.path.join(REPO_ROOT, 'checkers', 'binary', 'jsr308-all.jar')

def mvn_deploy_jsr308_all(version, binary=CHECKERS_BINARY, dest_repo=MAVEN_REPO):
    return mvn_deploy('jsr308-all', binary, version, dest_repo)


CHECKERS_QUALS = os.path.join(REPO_ROOT, 'checkers', 'checkers-quals.jar')

def mvn_deploy_quals(version, binary=CHECKERS_QUALS, dest_repo=MAVEN_REPO):
    return mvn_deploy('checkers-quals', binary, version, dest_repo)


def execute(command_args, halt_if_fail=True, capture_output=False):
    print("Executing: %s" % (command_args))
    import shlex
    args = shlex.split(command_args) if isinstance(command_args, str) else command_args

    if capture_output:
        return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    else:
        r = subprocess.call(args)
        if halt_if_fail and r:
            raise Exception('Error %s while executing %s' % (r, command_args))
        return r

def changelog_header(filename):
    f = open(filename, 'r')
    header = []

    for line in f:
        if '-------' in line:
            break
        header.append(line)

    return ''.join(header)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

## Define DRY_RUN_LINK
# "USER = os.getlogin()" does not work; see http://bugs.python.org/issue584566
# Another alternative is: USER = os.getenv('USER')
USER = pwd.getpwuid(os.geteuid())[0]
DRY_RUN_LINK_HTTP = "http://homes.cs.washington.edu/~%s/jsr308test/jsr308/" % USER
DRY_PATH = os.path.join(os.environ['HOME'], 'www', 'jsr308test')
DRY_RUN_LINK_FILE = "file://%s/jsr308/" % DRY_PATH
DRY_RUN_LINK = DRY_RUN_LINK_HTTP


TO = 'jsr308-discuss@googlegroups.com, checker-framework-discuss@googlegroups.com'

def format_email(version, checkers_header=None, langtools_header=None, to=TO):
    if checkers_header == None:
        checkers_header = changelog_header_checkers()
    if langtools_header == None:
        langtools_header = changelog_header_langtools()

    template = """
=================== BEGINING OF EMAIL =====================

To:  %s
Subject: Release %s of the Checker Framework and Type Annotations compiler

We have released a new version of the Type Annotations (JSR 308) compiler,
the Checker Framework, and the Eclipse plugin for the Checker Framework.
 * The Type Annotations compiler supports the type annotation syntax that is
   planned for a future version of the Java language.
 * The Checker Framework lets you create and/or run pluggable type-checkers,
   in order to detect and prevent bugs in your code.  
 * The Eclipse plugin makes it more convenient to run the Checker Framework.

You can find documentation and download links for these projects at:
http://types.cs.washington.edu/jsr308/

Notable changes include:
[[ FILL ME HERE ]]

Changes for the Checker Framework
%s
Changes for the Type Annotations Compiler
%s

=================== END OF EMAIL ==========================
    """ % (to, version, checkers_header, langtools_header,)
    return template



def main(argv):
    append_to_PATH()
    print("Making a new release of the Checker Framework!")

    # Infer version
    curr_version = current_distribution()
    print("Current release is %s" % curr_version)
    suggested_version = increment_version(curr_version)
    next_version = raw_input("Suggested next release: (%s): " % suggested_version)
    if not next_version:
        next_version = suggested_version
    print next_version

    # Update repositories
    update_projects()

    checkers_changes = retrieve_changes(REPO_ROOT, curr_version, "checkers-")
    edit_checkers_changelog(version=next_version,changes=checkers_changes)
    langtools_changes = retrieve_changes(JSR308_LANGTOOLS, curr_version, "jsr308-")
    edit_langtools_changelog(version=next_version,changes=langtools_changes)

    # Making the first release
    ant_args = ""
    for arg in argv[1:]:      # everything but the first element
        ant_args = ant_args + " '" + arg + "'"
    site_copy_if_needed(ant_args)
    make_release(next_version, ant_args)
    checklinks(DRY_RUN_LINK)

    print("Pushed to %s" % DRY_RUN_LINK)
    raw_input("Please check the site.  Press ENTER to continue.")
    print("\n\n\n\n\n")

    # Making the real release
    make_release(next_version, ant_args, real=True)

    # Make Maven release
    mvn_deploy_jsr308_all(next_version)
    mvn_deploy_quals(next_version)

    checklinks(DEFAULT_SITE)

    print("Pushed to %s" % DEFAULT_SITE)
    raw_input("Please check the site.  DONE?  Press ENTER to continue.")
    print("\n\n\n\n\n")

    commit_and_push(next_version, REPO_ROOT, "checkers-")
    commit_and_push(next_version, JSR308_LANGTOOLS, "jsr308-")

    ensure_group_access()

    print("You have just made the release.  Please announce it to the world")
    print("Here is an email template:")
    print format_email(next_version)

# The entry point to the Python script.
if __name__ == "__main__":
    sys.exit(main(sys.argv))