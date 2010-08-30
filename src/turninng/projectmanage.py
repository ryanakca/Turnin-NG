# Turnin-NG, an assignment submitter and manager. --- Project manager
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

import os
import os.path
import pwd
import re
import shutil
import subprocess
import sys
import tarfile

from turninng.configparser import ProjectCourse, ProjectProject
from turninng.fileperms import chown

def create_project(config_file, course, project):
    """
    Create the project 'project'.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @type project: string
    @param project project name
    @rtype: None

    """
    project_obj = ProjectProject(config_file, course, project)
    user = project_obj.course['user']
    group = project_obj.course['group']
    directory = project_obj.project['directory']
    os.makedirs(directory)
    os.chmod(directory, 0733)
    chown(directory, user, group)
    description = raw_input("[Optional] Project description: ")
    project_obj.write(True, description)

def delete_project(config_file, course, project):
    """
    Delete the project 'project'

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @type project: string
    @param project: project name
    @rtype: None
    @raise ValueError: The user enters anything but 'YES' at the prompt.
    @raise valueError: The project doesn't exist.

    """
    if ProjectCourse(config_file, course).course.has_key(project):
        project_obj = ProjectProject(config_file, course, project)
        if raw_input("If you really want to delete this project and all " +
                "associated files, enter 'yes' in capital letters: ") == 'YES':
            shutil.rmtree(project_obj.project['directory'], ignore_errors=True)
            if project_obj.course['default'] == project:
                project_obj.course['default'] = ''
            del project_obj.course[project]
            project_obj.config.write()
        else:
            raise ValueError("Aborting and keeping project.")
    else:
        raise ValueError("%s is not an existing project in the course %s" %
                (project, course))

def compress_project(config_file, course, project):
    """
    Compress the project 'project'.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @type project: string
    @param project: project name
    @rtype: None
    @raise ValueError: The project is enabled / accepting submissions
    @raise ValueError: The project is already compressed
    @raise ValueError: The project doesn't exist.

    """
    if ProjectCourse(config_file, course).course.has_key(project):
        project_obj = ProjectProject(config_file, course, project)
        if project_obj.project['enabled']:
            raise ValueError("Project %s is enabled, please disable it first." %
                    project)
        # We need to check that it has a key before checking if it's Null or
        # not. If we skipped straight to checking if Null, and the key didn't
        # exist,  we would get a KeyError.
        elif (project_obj.project.has_key('tarball') and
                            project_obj.project['tarball']):
            raise ValueError("Project %s is already compressed." % project)
        archive_name = os.path.join(project_obj.course['directory'],
                project_obj.name + '.tar.gz')
        tar = tarfile.open(archive_name, 'w:gz')
        tar.add(project_obj.project['directory'], project_obj.name)
        tar.close() # This writes the tarball
        project_obj.project['tarball'] = archive_name
        os.chmod(archive_name, 0600)
        project_obj.config.write()
        shutil.rmtree(project_obj.project['directory'], ignore_errors=True)
    else:
        raise ValueError("%s is not an existing project in the course %s" %
                (project, course))

def extract_project(config_file, course, project):
    """
    Uncompress the project 'project'.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @type project: string
    @param project: project name
    @rtype: None
    @raise ValueError: The project is not compressed
    @raise ValueError: The project does not exist.

    """
    if ProjectCourse(config_file, course).course.has_key(project):
        project_obj = ProjectProject(config_file, course, project)
        # We need to check that it has a key before checking if it's Null or
        # not. If we skipped straight to checking if Null, and the key didn't
        # exist,  we would get a KeyError.
        if (project_obj.project.has_key('tarball') and not
                                        project_obj.project['tarball']):
            raise ValueError("This project is not compressed.")
        print project_obj.project['tarball']
        tar = tarfile.open(project_obj.project['tarball'], 'r:gz')
        # Extract it to the course directory instead of to '.'
        if sys.version_info[1] >= 5:
            # extractall was added in Python 2.5
            tar.extractall(path=project_obj.course['directory'])
        else:
            for member in tar.getmembers():
                tar.extract(member, path=project_obj.course['directory'])
        tar.close()
        os.remove(project_obj.project['tarball'])
        project_obj.project['tarball'] = ''
        project_obj.config.write()
    else:
        raise ValueError("%s is not an existing project in the course %s" %
                (project, course))

def verify_sig(project_obj):
    """
    Verify the signatures of the projects with a signature.

    @type project_obj: ProjectProject
    @param project_obj: Project for which we'll verify the signatures
    @rtype: list
    @return: unsigned submissions
    @raise subprocess.CalledProcessError: gpg encounters an issue when verifying

    """
    # We need to sort so that we get ['archive.tar.gz', 'archive.tar.gz.sig']
    submissions = os.listdir(project_obj.project['directory'])
    if not submissions:
        raise ValueError("No assignments have been submitted yet.")
    signatures = []
    submissions.sort()
    for file in submissions:
        if file.endswith('.tar.gz'):
            if file + '.sig' in submissions:
                signatures.append(file + '.sig')
                submissions.remove(file)
                submissions.remove(file + '.sig')
    for sig in signatures:
        print "Verifying %s" % sig[:-4]
        retcode = subprocess.call(['gpgv',
            os.path.join(project_obj.project['directory'], sig)])
        if retcode < 0:
            raise subprocess.CalledProcessError(retcode, ' '.join(cargs))
    ret = ['Unsigned submissions: ']
    if len(submissions) == 0:
        ret.append('None')
    else:
        ret += submissions
    return ret

def strip_random_suffix(project_obj):
    """
    Remove the 16 byte suffixes of the style username-XXXXXXXXXXXXXXXX.tar.gz

    @type project_obj: ProjectProject
    @param project_obj: Project for which we will strip the suffixes
    @rtype: None
    @raise ValueError: No assignments have been submitted.

    """
    files = os.listdir(project_obj.project['directory'])
    if not files:
        raise ValueError("No assignments have been submitted yet. Not " +
                "stripping suffixes")
    # They need to be sorted since there is no guarantee that os.listdir will
    # read files in alphabetical order.
    submissions = {}
    rejects = []
    for submission in files:
        if re.match('^(?P<username>\w+)-\w{16}\.tar\.gz(|.sig)$', submission):
            username = re.match('^(?P<username>\w+)-\w{16}\.tar\.gz(|.sig)$',
                submission).group('username')
            if not submissions.has_key(username):
                submissions[username] = []
            submissions[username].append(submission)
        else:
            rejects.append(submission)

    for user, subs in submissions.items():
        if len(subs) != 1:
            # Let's get rid of assignments other people submitted for the user
            for submission in subs:
                owner = pwd.getpwuid(os.stat(os.path.join(
                    project_obj.project['directory'],
                    submission)).st_uid).pw_name
                if owner != user:
                    print Warning('Warning: Student %s submitted an ' % owner +
                        'assignment for the student %s. Skipping file %s.' %
                        (user, submission))
                    submissions[user].remove(submission)
            # It might still be that the user submitted more than one
            # assignment, but at least we know that the student submitted them.
            if len(submissions[user]) > 1:
                print Warning('Warning: Student %s submitted ' % user +
                    'more than one assignment, skipping the files: %s' %
                    ' '.join(submissions.pop(user)))
            # We don't want to print the above error if we are out of
            # submissions, but we don't want to match a nonexistent submission
            # later on
            if not submissions[user]:
                submissions.pop(user)
        owner = pwd.getpwuid(os.stat(os.path.join(project_obj.project['directory'],
                            subs[0])).st_uid).pw_name

        if owner != user:
            print Warning('Warning: Student %s submitted an ' % owner +
                    'assignment for the student %s. Skipping file %s.' % (user,
                        submissions.pop(user)[0]))
    if rejects:
        print ValueError("Warning: The following file(s) do not have the " +
            "the format username-XXXXXXXXXXXXXXXX.tar.gz or " +
            "username-XXXXXXXXXXXXXXX.tar.gz.sig, skipping: %s" %
            '\n'.join(rejects))

    for user, submission in submissions.items():
        format = re.match(user +
                '-\w{16}(?P<format>(\.tar\.gz|\.tar\.gz\.sig))$',
                submission[0]).group('format')
        if user + format in rejects:
            print ValueError("Warning: Stripping the file %s" % submission[0] +
                    " would cause the file %s to be" % (user + format) +
                    " overwritten. Skipping.")
        else:
            os.rename(
                os.path.join(project_obj.project['directory'], submission[0]),
                os.path.join(project_obj.project['directory'], user + format))
