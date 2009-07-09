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
import shutil
import tarfile

from turnin.configparser import ProjectCourse, ProjectProject
from turnin.sys import chown

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
    os.chmod(directory, 0730)
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
        tar.extractall(path=project_obj.course['directory'])
        tar.close()
        os.remove(project_obj.project['tarball'])
        project_obj.project['tarball'] = ''
        project_obj.config.write()
    else:
        raise ValueError("%s is not an existing project in the course %s" %
                (project, course))
