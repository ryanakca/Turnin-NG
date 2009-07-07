import os
import os.path

from project.configparser import ProjectCourse, ProjectProject
from project.sys import chown

def create_project(config_file, course, project):
    project_obj = ProjectProject(config_file, course, project)
    user = project_obj.course['user']
    group = project_obj.course['group']
    directory = os.path.join(project_obj.course['directory'], project)
    os.makedirs(directory)
    os.chmod(directory, 0730)
    chown(directory, user, group)
    description = raw_input("[Optional] Project description: ")
    project_obj.write(True, description)

def delete_project(config_file, course, project):
    project_obj = ProjectProject(config_file, course, project)
    if project_obj.course.has_key[project]:
        certain = raw_input("If you really want to delete this course and " +
                "all associated files, enter 'yes' in capital letters: ")
        if certain == 'YES':
            directory = os.path.join(project.course['directory'], project)
            shutil.rmtree(directory, ignore_errors=True)
            del project_obj.course[project]
        else:
            raise ValueError("Aborting and keeping project.")
    else:
        raise ValueError("%s is not an existing project in the course %s" %
                (project, course))
