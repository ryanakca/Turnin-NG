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

    """
    course = ProjectCourse(config_file, course)
    user = raw_input("Username [usually your UNIX login]: ")
    directory = raw_input("Full path to project directory: ")
    group = raw_input("Group: ")
    sections = raw_input("Sections: ")
    os.makedirs(directory) # We could supply the mode here, but it might get
                           #ignored on some systems. We'll do it here instead
    os.chmod(directory, 0730)
    chown(directory, user, group)
    course.write(user, directory, group, sections) 

def delete_course(config_file, course):
    """
    Delete the course 'course'.

    @type config_file: string
    @param config_file: path to the configuration file
    @type course: string
    @param course: course name
    @raise ValueError: The user decides enters anything but 'YES at the prompt.
    @raise ValueError: The course does not exist.

    """
    course_obj = ProjectCourse(config_file, course)
    if course_obj.config.has_key(course):
        certain = raw_input("If you really want to delete this course and all " +
                "associated files, enter 'yes' in capital letters: ")
        if certain == 'YES':
            shutil.rmtree(course_obj.course['directory'], ignore_errors=True)
            del course_obj.config[course]
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

    """
    global_obj = ProjectGlobal(config_file)
    global_obj.set_default(course)
