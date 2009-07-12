# Turnin-NG, an assignment submitter and manager. --- Submission utilities
# Copyright (C) 2009  Ryan Kavanagh <ryanakca@kubuntu.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import grp
import os
import os.path
import pwd
import shutil
import subprocess
import tarfile
import tempfile

from turnin.sys import chown, chgrp
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

def submit_files(course_name, project, files, gpg_key=''):
    """
    Submits the files to the project.

    @type course_name: string
    @param course_name: course name
    @type project: TurninProject
    @param project: Project to which we should submit the files
    @type files: list
    @param files: Python list of files.
    @type gpg_key: string
    @param gpg_key: GnuPG public-key ID
    @rtype: list
    @return: Python list of submitted files
    @raise subprocess.CalledProcessError: GnuPG fails to sign

    """
    temparchive = tempfile.NamedTemporaryFile(suffix='.tar.gz')
    filename =  '%(username)s.tar.gz' % \
        {'username': pwd.getpwuid(os.getuid())[0]} # This is the username that
                                                   # that owns the process
    tempdir = tempfile.mkdtemp()
    for file in files:
        if os.path.isdir(file):
            shutil.copytree(file, os.path.join(tempdir, file))
        else:
            shutil.copy(file, tempdir)
    tar = tarfile.open(temparchive.name, 'w:gz')
    # We want the uncompressed directory to have the username in it so the
    # professor can easily find a student's assignment.
    tar.add(tempdir, '%(projectname)s-%(username)s' %
                           {'projectname': project.name,
                            'username': pwd.getpwuid(os.getuid())[0]})
    submitted_files = tar.members
    tar.close()
    if gpg_key:
        cargs = ['gpg', '--sign', '-u ' + gpg_key, '-b', temparchive.name]
        retcode = subprocess.call(cargs)
        chown(temparchive.name + '.sig', project.course['user'],
                project.course['group'])
        if retcode < 0:
            raise subprocess.CalledProcessError(retcode, ' '.join(cargs))
    shutil.copy(temparchive.name,
            os.path.join(project.project['directory'], filename))
    chgrp(os.path.join(project.project['directory'], filename),
            project.course['group'])
    os.chmod(os.path.join(project.project['directory'], filename), 0644)
    # We want the signature's timestamp to be more recent than the archive's.
    if gpg_key:
        shutil.copy(temparchive.name + '.sig',
                os.path.join(project.project['directory'], filename + '.sig'))
        os.remove(temparchive.name + '.sig')
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
    @return: List of (Enabled/Disabled, Project_name, Description) tuples

    """
    projects = [['Enabled', 'Project', 'Description']]
    course_obj = TurninCourse(config, course)
    default = course_obj.course['default']
    for i in course_obj.course.__dict__['sections']:
        if default == i:
            projects.append(['Default', i, course_obj.course[i]['description']])
        else:
            projects.append([course_obj.course[i]['enabled'], i,
                course_obj.course[i]['description']])
    maxlen = [0,0,0]
    for p, project in enumerate(projects):
        for i, item in enumerate(project):
            # We need to convert item to string since item might be a bool.
            projects[p][i] = str(item)
            if len(str(item)) > maxlen[i]:
                maxlen[i] = len(str(item))
    for p, project in enumerate(projects):
        new_line = ''
        for i, item in enumerate(project):
            # We need the space difference + 1 so that we don't get "item|"
            new_line += '| ' + item + (maxlen[i] - len(item) + 1) * ' '
        new_line += '|'
        projects[p] = new_line
    # Let's insert the top, the header seperater and the bottom
    projects.insert(0, len(projects[0]) * '-')
    projects.insert(2, projects[0])
    projects.append(projects[0])
    return projects
