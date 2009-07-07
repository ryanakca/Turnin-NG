from os.path import join
from configobj import ConfigObj

class TurninGlobal(object):
    """ This class is in case we ever decide we want global configurations. """

    def __init__(self, config_file):
        self.config = ConfigObj()
        self.config.filename = config_file
        self.config.indent_type = '    '
        self.config.unrepr = True
        self.config.reload()
        if not self.config.has_key('Global'):
            raise ValueError("Invalid config file")

class TurninCourse(TurninGlobal):
    """ This class represents a turnin course object. """

    def __init__(self, config_file, course):
        super(TurninCourse, self).__init__(config_file)
        if not self.config.has_key(course):
            raise ValueError("Course %s does not exists!" % course)
        self.course = self.config[course]


    def read(self):
        """ Reads the self.course section in the config file. """
        self.config.reload()
        self.user = self.course['user']
        self.directory = self.course['directory']
        self.group = self.course['group']
        self.sections = self.course['sections']

class TurninProject(TurninCourse):
    """ This class represents a turnin course's project object. """

    def __init__(self, config_file, course, project):
        super(TurninProject, self).__init__(config_file, course)
        if not self.course.has_key(project):
            self.config[course][project] = {}
            self.config[course][project]['enabled'] = False
            self.config.write()
        self.project = self.course[project]
        self.project['directory'] = os.path.join(self.course['directory'],
                project)
        self.name = project

    def read(self):
        """ Reads the project from the config file. """
        self.config.reload()
        self.description = self.project['description']
        self.enabled = self.project['enabled']
        self.directory = self.project['directory']
