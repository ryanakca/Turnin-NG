import os

from project.configparser import ProjectGlobal, ProjectCourse

def create_course(config_file, course):
    course = ProjectCourse(config_file, course)
    user = raw_input("Username [usually your UNIX login]: ")
    directory = raw_input("Full path to project directory: ")
    group = raw_input("Group: ")
    sections = raw_input("Sections: ")
    course.write(user, directory, group, sections) 
    print "Successfully created the course %s." % course

def delete_course(config_file, course):
    course_obj = ProjectCourse(config_file, course)
    if course_obj.config.has_key(course):
        certain = raw_input("If you really want to delete this course and all " +
                "associated files, enter 'yes' in capital letters: ")
        if certain == 'YES':
            sh.rmtree(course_obj.course.directory, ignore_errors=True)
            course_obj.config.sections.remove(course)
    else:
        raise ValueError("%s is not an existing course" % course)
