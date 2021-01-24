# Turnin-NG, an assignment submitter and manager. --- Submission utilities
# Copyright (C) 2009-2020  Ryan Kavanagh <rak@rak.ac>
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

import errno
import os
import os.path
import pwd
import random
import shutil
import string
import subprocess
import tarfile
import tempfile

from turninng.configparser import TurninCourse, TurninList

def submit_files(project, files, tlist='', gpg_key=''):
    """
    Submits the files to the project.

    @type project: TurninProject
    @param project: Project to which we should submit the files
    @type files: list
    @param files: Python list of files.
    @type tlist: TurninList
    @param tlist: list of submitted files
    @type gpg_key: string
    @param gpg_key: GnuPG public-key ID
    @rtype: list
    @return: Python list of submitted files
    @raise subprocess.CalledProcessError: GnuPG fails to sign
    @raise EnvironmentError: tlist exists and is not a file

    """
    if not tlist:
        tlist = os.path.join(os.path.expanduser('~'), '.turnin-ng',
                'submissions')
        # We don't want something like /home/ryan/.turning-ng/submissions../
        if not os.path.isdir(os.path.normpath(os.path.join(tlist, os.pardir))):
            os.makedirs(os.path.normpath(os.path.join(tlist, os.pardir)))
        # Create the TurninList if it doesn't exist:
        if not os.path.isfile(tlist):
            if os.path.exists(tlist):
                raise EnvironmentError(
                    "Path for list of submissions %s exists " % tlist +
                    "but is not a file.")
            else:
                open(tlist, 'w').close()
        # We don't want other people to be able to read out submitted file
        # suffixes and messing with our files!
        os.chmod(tlist, 0o600)
    list_file = TurninList(tlist)
    random_suffix = ''
    if project.course.name in list_file.config:
        if project.project['uuid'] in list_file.config[project.course.name]:
            random_suffix = list_file.config[project.course.name][
                    project.project['uuid']]
    if not random_suffix:
        chars = string.ascii_letters + string.digits
        for i in range(16):
            random_suffix += random.choice(chars)
        list_file.write(project, random_suffix)
    temparchive = tempfile.NamedTemporaryFile(suffix='.tar.gz')
    filename =  '%(username)s-%(suffix)s.tar.gz' % \
        {'username': pwd.getpwuid(os.getuid())[0], # This is the username that
                                                   # that owns the process
         'suffix': random_suffix}
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
        if retcode < 0:
            raise subprocess.CalledProcessError(retcode, ' '.join(cargs))
            print("An error occured when calling GPG, not submitting signature")
            # It's important that we set gpg_key to False. Otherwise,
            # shutil.copy below will fail because it can't find the .sig file
            # and Turnin-NG will crash.
            gpg_key = False
    shutil.copyfile(temparchive.name,
            os.path.join(project.project['directory'], filename))
    try:
        os.chmod(os.path.join(project.project['directory'], filename), 0o666)
    except OSError as e:
        if e.errno == e.EPERM:
            # We've got an error on our hands:
            # OSError: [Errno 1] Operation not permitted
            #
            # Probable cause:
            #
            # We've previously submitted. A managing user has since
            # disabled/enabled the project and is now the owner of our archive.
            # Since we aren't the owner, we don't have permisisons to run chmod.
            # In any case, unless we have a malicious TA, since we've already
            # submitted, the permissions on our file should already be correct.
            pass
    # We want the signature's timestamp to be more recent than the archive's.
    if gpg_key:
        shutil.copyfile(temparchive.name + '.sig',
                os.path.join(project.project['directory'], filename + '.sig'))
        os.remove(temparchive.name + '.sig')
        # GPG signatures are 644 by default
        os.chmod(os.path.join(project.project['directory'], filename + '.sig'),
                 0o666)
    else:
        submitted_sig = os.path.join(project.project['directory'],
                                     filename + '.sig')
        if os.path.exists(submitted_sig):
            # We've already submitted our project and we had signed it. Since
            # we're resubmitting, our old signature won't match. Delete it.
            os.remove(submitted_sig)
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
    @return: List of '| Enabled/Disabled/Default | Project name | Description |'
    strings

    """
    projects = [['Enabled', 'Project', 'Description']]
    course_obj = TurninCourse(config, course)
    default = ''
    if 'default' in course_obj.course:
        default = course_obj.course['default']
    for i in course_obj.course.__dict__['sections']:
        if default == i:
            projects.append(['Default', i, course_obj.course[i]['description']])
        else:
            projects.append([course_obj.course[i]['enabled'], i,
                course_obj.course[i]['description']])
    maxlen = [0, 0, 0]
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
