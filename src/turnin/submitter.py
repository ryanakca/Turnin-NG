import grp
import os
import os.path
import pwd
import shutil
import tarfile
import time
import tempfile

from turnin.sys import chown

def check_group(group):
    # Gets the group database entry, selects [2] from the tuple (gr_name,
    # gr_passwd, gr_gid, gr_mem). Checks if the gid is in the process owner's
    # groups list.
    if grp.getgrnam(group)[2] in os.getgroups():
        return True
    return False

def submit_files(course_name, project, files):
    # Maybe we should use pwd.getpwuid(os.getuid())[4].replace(' ', '') ---
    # that's to say, their full name stored in GECOS.
    tempdir = tempfile.mkdtemp()
    filename =  '%(username)s-%(timestamp)s.tar.gz' % \
        {'username': pwd.getpwuid(os.getuid())[0],
         'timestamp': time.strftime("%Y-%m-%d-%H%M%S")}
    archive = os.path.join(tempdir, filename )
    tar = tarfile.open(archive, 'w:gz')
    for file in files:
        tar.add(file)
    submitted_files = tar.list(verbose=True)
    tar.close()
    chown(archive, project.course['user'], project.course['group'])
    shutil.move(archive, os.path.join(project.project['directory'], filename))
    shutil.rmtree(tempdir, ignore_errors=True)
    return submitted_files
