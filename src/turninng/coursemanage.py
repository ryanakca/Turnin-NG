# Turnin-NG, an assignment submitter and manager. --- Course manager
# Copyright (C) 2009-2010  Ryan Kavanagh <ryanakca@kubuntu.org>
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

import datetime
import errno
import grp
import os
import os.path
import pwd
import shutil
import sys
import tarfile

from turninng.configparser import ProjectGlobal, ProjectAdminCourse
from turninng.fileperms import chown

def create_course(config_file, course):
    """
    Create the course 'course'.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @rtype: None
    @raise ValueError: The course already exists.

    """
    config_obj = ProjectGlobal(config_file)
    if not config_obj.config.has_key(course):
        course = ProjectAdminCourse(config_file, course)
        # Don't die if we get an invalid user
        while True:
            user = raw_input("Managing username [usually your UNIX login]: ")
            try:
                pwd.getpwnam(user)
            except KeyError, e:
                print "User does not exist. Please try again."
            else:
                break
        directory = raw_input("Full path to the course directory: ")
        group_managed = '?'
        # Don't check if "in 'UuGg'" because we don't want 'uGg' to match
        while group_managed not in ('U', 'u', 'G', 'g'):
            group_managed = raw_input("Managed by a User or Group [U/G]: ")
        # Don't die if we get an invalid group
        while True:
            if group_managed in ('G', 'g'):
                group_managed = True
                group = raw_input("Managing group: ")
            else:
                group_managed = False
                group = raw_input("Student group: ")
            try:
                grp.getgrnam(group)
            except KeyError, e:
                print "Group does not exist. Please try again."
            else:
                break
        try:
            try:
                os.makedirs(directory) # We could supply the mode here, but it might get
                                       #ignored on some systems. We'll do it here instead
            except OSError, e:
                # We don't want to abort of the directory already exists
                if e.errno == errno.EEXIST:
                    print e
                    print 'Continuing'
                else:
                    sys.exit(e)
            chown(directory, user, group)
            chown(config_file, user, group)
            if group_managed:
                os.chmod(directory, 0775)
            else:
                os.chmod(directory, 0755)
                print "Please make sure the account %s" % user +\
                      " is a member of the group %s." % group
        except OSError, e:
            print e
        course.write(user, directory, group, group_managed)
        # We want to set the default course for the per course config.
        global_course_conf = ProjectGlobal(course.course['projlist'])
        global_course_conf.set_default(course.course.name)
        chown(course.course['projlist'], user, group)
        if group_managed:
            os.chmod(course.course['projlist'], 0664)
        else:
            os.chmod(course.course['projlist'], 0644)
    else:
        raise ValueError ('The course %s already exists, aborting' % course)

def delete_course(config_file, course):
    """
    Delete the course 'course'.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @rtype: None
    @raise ValueError: The user enters anything but 'YES' at the prompt.
    @raise ValueError: The course does not exist.

    """
    config_obj = ProjectGlobal(config_file)
    if config_obj.config.has_key(course):
        course_obj = ProjectAdminCourse(config_file, course)
        if raw_input("If you really want to delete this course and all " +
                "files in the course directory  %s , " % (
                course_obj.course['directory'] ) + "enter 'yes' in capital" +
                " letters: ") == 'YES':
            shutil.rmtree(course_obj.course['directory'], ignore_errors=True)
            del course_obj.config[course]
            # We need to check that Global has the key 'default', otherwise we
            # get a KeyError if it doesn't.
            if ((course_obj.config['Global'].has_key('default')) and
                    (course_obj.config['Global']['default'] == course)):
                course_obj.config['Global']['default'] = ''
            course_obj.config.write()
        else:
            raise ValueError("Aborting and keeping course %s" % course)
    else:
        raise ValueError("%s is not an existing course" % course)

def archive_course(config_file, course, ret_path=False):
    """
    Archive the course in .tar.gz format.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @type ret_path: bool
    @param ret_path: Do we return the archive's path?
    @rtype: string
    @return: Path to the archive.
    @raise ValueError: The user enters anything but 'YES' at the prompt.
    @raise ValueError: The course does not exist.

    """
    config_obj = ProjectGlobal(config_file)
    if config_obj.config.has_key(course):
        config_obj = ProjectAdminCourse(config_file, course)
        if raw_input("If you really want to archive this course and erase it "+
                "from the configuration file, enter 'yes' in capital " +
                "letters: ") == 'YES':
            archive_path = os.path.normpath(os.path.join(
                    config_obj.course['directory'],
                    os.pardir,
                    course + '-' + str(datetime.datetime.now().year) +
                             '.tar.gz'))
            tar = tarfile.open(archive_path, 'w:gz')
            tar.add(config_obj.course['directory'], course + '-' +
                    str(datetime.datetime.now().year))
            tar.close()
            if config_obj.course['group_managed']:
                os.chmod(archive_path, 0660)
            else:
                os.chmod(archive_path, 0600)
            chown(archive_path, config_obj.course['user'], config_obj.course['group'])
            shutil.rmtree(config_obj.course['directory'], ignore_errors=True)
            del config_obj.config[course]
            # We need to check that Global has the key 'default', otherwise we
            # get a KeyError if it doesn't.
            if ((config_obj.config['Global'].has_key('default')) and
                    (config_obj.config['Global']['default'] == course)):
                config_obj.config['Global']['default'] = ''
            config_obj.config.write()
            if ret_path:
                return archive_path
        else:
            raise ValueError("Aborting and keeping course %s unarchived" %
                    course)
