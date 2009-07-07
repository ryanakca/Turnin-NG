#!/usr/bin/python2.5

from optparse import OptionParser, OptionGroup
import os.path
import sys

from turnin.configparser import TurninGlobal, TurninCourse, TurninProject
from turnin.submitter import submit_files, check_group

if __name__ == '__main__':
    usage = '%prog [options] [project name]'
    parser = OptionParser(version='0.1_pre-alpha', usage=usage)
    parser.add_option('-c', '--course', help='Set the course to submit the ' +
            'assignment to.')
    parser.add_option('-l', '--list', help='Lists projects for the course. ' +
            'also displays wether or not the project is open.',
            action='store_true')
    parser.add_option('-p', '--project', help='Set the project to submit the '+
            'assigmnent to.')
    parser.add_option('-C', '--config', help='Set a custom configuration ' +
            'file.')
    #parser.add_option('-v', '--verbose', action='store_true', help='Print ' +
    #        'a list of submitted files.')

    (options, args) = parser.parse_args()

    if not args:
        sys.exit(ValueError("Error, please submit at least one document."))
    if not options.course:
        sys.exit(ValueError("Error, please specify a course."))
    if options.config:
        config = options.config
    else:
        config = os.path.join("/srv/submit", options.course, "turnin.cf")
    if options.project:
        project = TurninProject(config, options.course, options.project)
    else:
        project = TurninProject(config, options.course, TurninCourse(config,
            options.course).course['default'])

    if check_group(project.course['group']): # Check that the current user is in
                                             # the submitter group.
        submit_files(options.course, project, args)
