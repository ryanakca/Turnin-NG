#!/usr/bin/python2.5

from optparse import OptionParser, OptionGroup
import os.path
import sys

from turnin.configparser import TurninGlobal, TurninCourse, TurninProject
from turnin.submitter import submit_files, check_group, list_projects

if __name__ == '__main__':
    usage = '%prog [options] [project name]'
    parser = OptionParser(version='0.1_pre-alpha', usage=usage)
    parser.add_option('-c', '--course', help='Set the course to submit the ' +
            'assignment to.')
    parser.add_option('-l', '--list', help='Lists projects for the course. ' +
            'also displays wether or not the project is open.',
            action='set_true')
    parser.add_option('-p', '--project', help='Set the project to submit the '+
            'assigmnent to.')
    parser.add_option('-C', '--config', help='Set a custom configuration ' +
            'file.')
    parser.add_option('-v', '--verbose', action='store_true', help='Print ' +
            'a list of submitted files.')

    (options, args) = parser.parse_args()

    # If we're listing projects, it's obvious we won't be submitting to one.
    if not options.list and not args:
        sys.exit(ValueError("Error, please submit at least one document."))
    if not options.course:
        sys.exit(ValueError("Error, please specify a course."))
    try:
        # We're nesting this in a try: because we might find out the requested
        # course or project doesn't exist.
        if options.config:
            config = options.config
        else:
            config = os.path.join("/srv/submit", options.course, "turnin.cf")
        # We're listing the courses:
        if options.list:
            projects = list_projects(config, options.course)
            for i in projects:
                print i
            sys.exit()
    except ValueError, e:
        sys.exit(e)

    try:
        # We're creating after having run list because if the user is asking for
        # a list of projects, the user won't be passing a project.
        if options.project:
            project = TurninProject(config, options.course, options.project)
        else:
            project = TurninProject(config, options.course, TurninCourse(config,
                options.course).course['default'])
    except ValueError, e:
        sys.exit(e)


    # We have checked that the user has provided a course, a project and
    # assignments. We can now proceed to submit them.
    # Check that the current user is in the submitter group.
    if check_group(project.course['group']):
        files = submit_files(options.course, project, args)
        if options.verbose:
            print "Submitted files:"
            for file in files:
                print file
            sys.exit()
    else:
        sys.exit("You need to be in the group %s to submit files" %
                project.course['group'])
