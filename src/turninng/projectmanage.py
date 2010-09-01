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
    submissions = os.listdir(project_obj.project['directory'])
    if not submissions:
        raise ValueError("No assignments have been submitted yet.")
    signatures = []
    # We need to work with a copy of submissions since we should never mutate a
    # list in place. Don't go submissions_copy = submissions , submissions_copy
    # would point to the same list submissions is pointing to.
    submissions_copy = list(submissions)
    for file in submissions_copy:
        if file.endswith('.tar.gz'):
            if file + '.sig' in submissions:
                signatures.append(file + '.sig')
                submissions.remove(file)
                submissions.remove(file + '.sig')
    for sig in signatures:
        print "Verifying %s" % sig[:-4]
        cargs = ['gpg', '--verify',
                 os.path.join(project_obj.project['directory'], sig)]
        retcode = subprocess.call(cargs)
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
    rejects = set()
    filename_format = re.compile(
            '^(?P<username>\w+)-\w{16}(?P<format>\.tar\.gz(|.sig))$')
    for submission in files:
        if filename_format.match(submission):
            username = filename_format.match(submission).group('username')
            format = filename_format.match(submission).group('format')
            if not submissions.has_key(username):
                submissions[username] = {'tarfiles': set(), 'sigfiles': set()}
            if format.endswith('.tar.gz'):
                submissions[username]['tarfiles'].add(submission)
            else:
                submissions[username]['sigfiles'].add(submission)
        else:
            rejects.add(submission)

    if rejects:
        print ValueError("Warning: The following file(s) do not have the " +
            "the format username-XXXXXXXXXXXXXXXX.tar.gz or " +
            "username-XXXXXXXXXXXXXXX.tar.gz.sig, skipping: %s" %
            '\n'.join(rejects))

    def get_owner(project, submission):
        """
        Which user owns the submission

        @type project: ProjectProject
        @param project: current project
        @type submission: str
        @param submission: file in the submission directory
        @rtype: string
        @return: the owner of the submission

        """
        owner = pwd.getpwuid(os.stat(os.path.join(
            project.project['directory'], submission)).st_uid).pw_name
        return owner

    for user in submissions.keys():
        # Make copies of the sets to iterate through since we'll be modifying
        # them and can't mutate sets while iterating through them
        submissions_user_tarfiles = set(submissions[user]['tarfiles'])
        for tar in submissions_user_tarfiles:
            owner = get_owner(project_obj, tar)
            if not owner == user:
                # Let's get rid of assignments other people submitted for the
                # user
                print Warning('Warning: Student %s submitted an ' % owner +
                    'assignment for the student %s. Skipping file %s.' %
                    (user, tar))
                submissions[user]['tarfiles'].discard(tar)
                if tar + '.sig' in submissions[user]['sigfiles']:
                    print Warning('Also skipping associated signature file' +
                        ' %s.' % (tar + '.sig'))
                    submissions[user]['sigfiles'].discard(tar + '.sig')
        # Make the sigfiles copy here since we may have modified sigfiles in the
        # tar checking loop
        submissions_user_sigfiles = set(submissions[user]['sigfiles'])
        for sig in submissions_user_sigfiles:
            owner = get_owner(project_obj, sig)
            if not owner == user:
                # Let's get rid of signatures other people submitted for the
                # user. This should probably never get called unless we have
                # really really stupidsilly people who are
                # desperately trying to get caught.
                print Warning('Warning: Student %s submitted a ' % owner +
                    'signature for the student %s. Skipping file %s.' %
                    (user, sig))
                submissions[user]['sigfiles'].discard(sig)
            elif sig[:-4] not in submissions[user]['tarfiles']:
                # Remove hanging signature files so that
                # len(submissions[user]['sigfiles']) <=
                # len(submissions[user]['tarfiles)
                print Warning('Warning: Signature file %s' % sig +
                    ' has no associated archive. Skipping file %s.' % sig)
                submissions[user]['sigfiles'].discard(sig)

        if len(submissions[user]['tarfiles']) > 1:
                print Warning('Warning: Student %s submitted ' % user +
                    'more than one assignment, skipping the files: %s' %
                    ' '.join(submissions[user].pop('tarfiles') |
                             submissions[user].pop('sigfiles')))
                submissions.pop(user)
        elif len(submissions[user]['tarfiles']) == 0:
            # If a user doesn't have any valid assignments associated with him,
            # take him out of the to-stip queue
            submissions.pop(user)

    for user in submissions.keys():
        submitted_files = submissions[user]['tarfiles'] | \
                          submissions[user]['sigfiles']
        # Any overwrites?
        overwrites = set([user + '.tar.gz', user + '.tar.gz.sig']) & rejects
        if overwrites:
            print ValueError("Warning: Stripping the user %s's" % user +
                " file(s) (%s) would either cause the files %s" % (
                ', '.join(submitted_files), ', '.join(overwrites)) +
                " to be overwritten or would break signatures. Skipping" +
                " the files: %s" % ' '.join(submitted_files))
        else:
            for submission in submitted_files:
                format = filename_format.match(submission).group('format')
                os.rename(
                    os.path.join(project_obj.project['directory'], submission),
                    os.path.join(project_obj.project['directory'],
                                 user + format))
