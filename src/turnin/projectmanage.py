import os
import os.path
import shutil
import tarfile

from turnin.configparser import ProjectCourse, ProjectProject
from turnin.sys import chown

def create_project(config_file, course, project):
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
    if ProjectCourse(config_file, course).course.has_key(project):
        project_obj = ProjectProject(config_file, course, project)
        certain = raw_input("If you really want to delete this project and " +
                "all associated files, enter 'yes' in capital letters: ")
        if certain == 'YES':
            directory = project_obj.project['directory']
            shutil.rmtree(directory, ignore_errors=True)
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
    if ProjectCourse(config_file, course).course.has_key(project):
        project_obj = ProjectProject(config_file, course, project)
        if project_obj.project['enabled']:
            raise ValueError("Project %s is enabled, please disable it first." %
                    project)
        archive_name = os.path.join(project_obj.course['directory'],
                project_obj.name + '.tar.gz')
        print archive_name
        tar = tarfile.open(archive_name, 'w:gz')
        tar.add(project_obj.project['directory'])
        tar.close()
        project_obj.project['tarball'] = archive_name
        shutil.rmtree(project_obj.project['directory'], ignore_errors=True)
    else:
        raise ValueError("%s is not an existing project in the course %s" %
                (project, course))
