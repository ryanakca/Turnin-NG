from optparse import OptionParser

usage = '%prog [options] [name]'
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

if __name__ == '__main__':
    (options, args) = parser.parse_args()
