from configobj import ConfigObj

class ProjectGlobalConfig(object):
    """ This class is in case we ever decide we want global configurations. """
    
    def __init__(self, config_file):
        self.config = ConfigObj()
        self.config.filename = config_file
        self.config.indent_type = '    '
        self.config.unrepr = True

class ProjectCourse(ProjectGlobalConfig):
    """ This class represents a turnin course object. """

    def __init__(self, config_file, course):
        super(ProjectCourse, self).__init__(config_file)
        self.course = course
        if not self.config.__dict__.__contains__(course):
            self.config.reload() # We don't want to clobber something
            self.config[course] = {}
            self.config.write()

    def read(self):
        """ Reads the self.course section in the config file. """
        super(ProjectCourse, self).read()
        self.user = self.config[self.course]['user']
        self.directory = self.config[self.course]['directory']
        self.group = self.config[self.course]['group']
        self.sections = self.config[self.course]['sections']


    def write(self, user='', directory='', group='', sections=''):
        """ Modifies the config file. """
        self.config.reload() # We don't want to clobber something
        if user:
            self.config[self.course]['user'] = user
        if directory:
            self.config[self.course]['directory'] = directory
        if group:
            self.config[self.course]['group'] = group
        if sections:
            self.config[self.course]['sections'] = sections
        self.config.write()


class ProjectProject(ProjectCourse):
    """ This class represents a turnin course's project object. """

    def __init__(self, config_file, course, project):
        super(ProjectProject, self).__init__(config_file, course)
        self.project = project
        if not self.config[course].__contains__(project):
            self.config.reload() # We don't want to clobber something
            self.config[course][project] = {}
            self.config[course][project]['enabled'] = False
            self.config.write()

    def read(self):
        """ Reads the project from the config file. """
        self.config.reload()
        self.description = self.config[self.course][self.project]['description']
        self.enabled = self.config[self.course][self.project]['enabled']

    def write(self, enabled, description=''):
        """ Modifies the config file. """
        self.config.reload() # We don't want to clobber something
        self.config[self.course][self.project]['enabled'] = enabled
        if description:
            self.config[self.course][self.project]['description'] = description
        self.config.write()
