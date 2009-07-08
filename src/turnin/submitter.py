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
    """
    Checks if the user / runner belongs to the group 'group'.

    @type group: string
    @param group: UNIX group name
    @rtype: Bool
    @return: True if the user belongs to the group, False otherwise.

    """
    # Gets the group database entry, selects [2] from the tuple (gr_name,
    # gr_passwd, gr_gid, gr_mem). Checks if the gid is in the process owner's
    # groups list.
    if grp.getgrnam(group)[2] in os.getgroups():
        return True
    return False

def submit_files(course_name, project, files):
    """
    Submits the files to the project.

    @type course_name: string
    @param course_name: course name
    @type project: TurninProject
    @param project: Project to which we should submit the files
    @type files: list
    @param files: Python list of files.
    @rtype: list
    @return: Python list of submitted files

    """
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
    """
    Lists available projects for the course.

    @type config: string
    @param config: configuration file
    @type course: string
    @param course: course name
    @rtype: list
    @return: List of (Enabled/Disabled, Project_name) tuples

    """
    projects = ['(Enabled, Project)']
    course_obj = TurninCourse(config, course)
    for i in course_obj.course.__dict__['sections']:
        projects.append((course_obj.course[i]['enabled'], i))
    return projects
