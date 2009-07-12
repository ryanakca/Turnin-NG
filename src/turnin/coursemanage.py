# Turnin-NG, an assignment submitter and manager. --- Course manager
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
import shutil

from turnin.configparser import ProjectGlobal, ProjectCourse
from turnin.sys import chown

def create_course(config_file, course):
    """
    Create the course 'course'.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @rtype: None

    """
    course = ProjectCourse(config_file, course)
    user = raw_input("Username [usually your UNIX login]: ")
    directory = raw_input("Full path to the course directory: ")
    group = raw_input("Group: ")
    os.makedirs(directory) # We could supply the mode here, but it might get
                           #ignored on some systems. We'll do it here instead
    os.symlink(config_file, os.path.join(directory, 'turnin.cf'))
    os.chmod(directory, 0750)
    chown(directory, user, group)
    os.chmod(config_file, 0640)
    chown(config_file, user, group)
    course.write(user, directory, group)

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
    course_obj = ProjectCourse(config_file, course)
    if course_obj.config.has_key(course):
        if raw_input("If you really want to delete this course and all " +
                "associated files, enter 'yes' in capital letters: ") == 'YES':
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

def switch_course(config_file, course):
    """
    Sets the default course in the configuration file.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @rtype: None

    """
    global_obj = ProjectGlobal(config_file)
    global_obj.set_default(course)
