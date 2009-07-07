#!/usr/bin/python2.5

from optparse import OptionParser, OptionGroup
import os.path
import sys

from project.configparser import ProjectGlobal, ProjectCourse, ProjectProject
from project.coursemanage import create_course, delete_course, switch_course
from project.projectmanage import create_project, delete_project

if __name__ == '__main__':
    usage = '%prog [options] [project name]'
    parser = OptionParser(version='0.1_pre-alpha', usage=usage)
    parser.add_option('-d', '--disable', action='store_false', dest='enabled',
            help='Disable submissions for the current project.')
    parser.add_option('-e', '--enable', action='store_true', dest='enabled',
            help='Enable submissions for the current project and make it ' +
            'the default project.')
    parser.add_option('-l', dest='enabled_nodefault', action='store_true',
            help="Enable submissions for the current project but don't make " +
            "it default")
    parser.add_option('-r', '--remove', action='store_true', dest='remove',
            help='Remove all files associated with the current project.')
    parser.add_option('-i', '--init', action='store_true', dest='init',
            help='Initialize this project')
#    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
#            help='Verbose. Print shell commands as they are executed.')
    parser.add_option('--config', help='Use an alternate config file')
    admin = OptionGroup(parser, "Administrative options",
            "These options can add or remove courses, etc.")
    admin.add_option('--create-course', help='Creates a course')
    admin.add_option('--delete-course', help='Deletes a course')
    parser.add_option('-c', '--switch', help='Switch between the course you ' +
        'are currently administering.')
    parser.add_option_group(admin)
    (options, args) = parser.parse_args()

    if len(args) > 1:
        raise ValueError("Error, please pass one project name at a time.")
    if options.config:
        config = options.config
    else:
        config = os.path.join(os.path.expanduser('~'), 'turnin.cf')

    # Administrative functions :
    if options.create_course:
        create_course(config, options.create_course) 
        sys.exit("Successfully created the course %s" % options.create_course)
    if options.delete_course:
        try:
            delete_course(config, options.delete_course)
            sys.exit("Successfully deleted the course %s" % options.delete_course)
        except ValueError, e:
            sys.exit(e)
    if options.switch:
        try:
            switch_course(config, options.switch)
            sys.exit("Successfully switched the default course to %s" %
                    options.switch)
        except ValueError, e:
            sys.exit(e)


    # End user functions :
    default_course = ProjectGlobal(config).config['Global']['default']
    if not default_course:
        sys.exit("Please set the default course using the '-c course' or " +
            "'--switch=COURSE' options.")

    # Create or delete the project if needed before creating an object
    if options.init:
        create_project(config, default_course, args[0])
        sys.exit("Successfully created the project %s in the course %s" %
                (args[0], default_course))
    elif options.remove:
        try:
            delete_project(config, default_course, args[0])
            sys.exit("Successfully deleted the project %s" % args[0])
        except ValueError, e:
            sys.exit(e)


    project = ProjectProject(config, default_course, args[0])
    # Enable submissions for a project
    if options.enabled:
        project.write(True, default=True)
        sys.exit("Successfully enabled and set default the project %s" % args[0])
    elif options.enabled == False: # Disable it. I know, using '== False' is
        # bad according to PEP 8. However, using 'elif not options.enabled' will
        # return true even if the user didn't pass the option since
        # options.enabled will be None. We could check for != None, but I'd
        # rather be explicit than implicit ;)
        project.write(False)
        sys.exit("Successfully disabled the project %s" % args[0])
    elif options.enabled_nodefault:
        project.write(True)
        sys.exit("Successfully enabled the project %s" % args[0])
   #  print options, args
