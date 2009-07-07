import grp
import os
import os.path
import pwd
import shutil
import tarfile
import time
import tempfile

from turnin.sys import chown
from turnin.configparser import TurninCourse

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
    temparchive = tempfile.NamedTemporaryFile()
    filename =  '%(username)s-%(timestamp)s.tar.gz' % \
        {'username': pwd.getpwuid(os.getuid())[0],
         'timestamp': time.strftime("%Y-%m-%d-%H%M%S")}
    tempdir = tempfile.mkdtemp()
    for file in files:
        if os.path.isdir(file):
            shutil.copytree(file, os.path.join(tempdir, file))
        else:
            shutil.copy(file, tempdir)
    os.listdir(tempdir)
    tar = tarfile.open(temparchive.name, 'w:gz')
    tar.add(tempdir, '%(projectname)s-%(username)s' %
                           {'projectname': project.name,
                            'username': pwd.getpwuid(os.getuid())[0]})
    submitted_files = tar.members # tar.list(verbose=True)
    tar.close()
    chown(temparchive.name, project.course['user'], project.course['group'])
    shutil.copy(temparchive.name,
            os.path.join(project.project['directory'], filename))
    temparchive.close()
    shutil.rmtree(tempdir, ignore_errors=True)
    for j, file in enumerate(submitted_files):
        submitted_files[j] = file.name
    return submitted_files

def list_projects(config, course):
    projects = ['(Enabled, Project)']
    course_obj = TurninCourse(config, course)
    for i in course_obj.course.__dict__['sections']:
        projects.append((course_obj.course[i]['enabled'], i))
    return projects
