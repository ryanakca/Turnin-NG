import os
import os.path

from project.configparser import ProjectCourse, ProjectProject
from project.sys import chown

def create_project(config_file, course, project):
    project = ProjectProject(config_file, course, project)
    user = project.course['user']
    group = project.course['group']
    directory = os.path.join(project.course['directory'], project)
    os.makedirs(directory)
    os.chmod(directory, 0730)
    chown(directory, user, group)
    description = raw_input("[Optional] Project description: ")
    course.write(True, description)
