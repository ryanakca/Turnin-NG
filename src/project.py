#!/usr/bin/python2.5

from optparse import OptionParser, OptionGroup
import os.path

from project.configparser import ProjectGlobal, ProjectCourse, ProjectProject
from project.coursemanage import create_course #, switch_course

# from project.projectmanage import create_project 

if __name__ == '__main__':
    usage = '%prog [options] [project name]'
    parser = OptionParser(version='0.1_pre-alpha', usage=usage)
    parser.add_option('-c', '--course', help='Change the course you are ' +
        'currently administering.')
    parser.add_option('-d', '--disable', action='store_false', dest='enabled',
            help='Disable submissions for the current project.')
    parser.add_option('-e', '--enable', action='store_true', dest='enabled',
            help='Enable submissions for the current project.')
    parser.add_option('-r', '--remove', action='store_true', dest='remove',
            help='Remove all files associated with the current project.')
    parser.add_option('-i', '--init', action='store_true', dest='init',
            help='Initialize this project')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
            help='Verbose. Print shell commands as they are executed.')
    parser.add_option('--config', help='Use an alternate config file')
    admin = OptionGroup(parser, "Administrative options",
            "These options can add or remove courses, etc.")
    admin.add_option('--create-course', help='Creates a course')
    admin.add_option('--delete-course', help='Deletes a course')
    parser.add_option_group(admin)
    (options, args) = parser.parse_args()

    if len(args) > 1:
        raise ValueError("Error, please pass one project name at a time.")
    if options.config:
        config = options.config
    else:
        config = os.path.join(os.path.expanduser('~'), 'turnin.cf')

    if options.create_course:
        create_course(config, options.create_course) 
        break

    default_course = ProjectGlobal(config).config.default
    project = ProjectProject(config, default_course, args[0])
    if options.enabled:
        project.write(True)
    elif not options.enabled:
        project.write(False)
    print options, args
