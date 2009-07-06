import ConfigParser

class TurninGlobalConfig(object):
    """ This class is in case we ever decide we want global configurations. """
    
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(self.config_file)

class TurninCourse(TurninGlobalConfig):
    """ This class represents a turnin course object. """

    def __init__(self, config_file, course):
        super(TurninCourse, self).__init__(config_file)
        self.course = course
        if not self.config.has_section(self.course):
            self.config.add_section(self.course)
            with open(self.config_file, 'wb') as config_file:
                config.write(config_file)

    def read():
        """ Reads the self.course section in the config file. """
        try:
            self.user = self.config.get(self.course, 'user')
            self.directory = self.config.get(self.course, 'directory')
            self.group = self.config.get(self.course, 'group')
            self.sections = self.config.get(self.course, 'sections')
        except ConfigParser.NoSectionError, e:
            print "Course %s does not exist." % e.section
        except ConfigParser.NoOptionError, e:
            print ("Option %s has not yet been defined for the course %s." %
                (e.option, e.course))


    def write(user='', directory='', group='', sections=[]):
        """ Modifies the config file. """
        try:
            if user:
                self.config.set(self.course, 'user', user)
            elif directory:
                self.config.set(self.course, 'directory', directory)
            elif group:
                self.config.set(self.course, 'group', group)
            elif sections:
                self.config.set(self.course, 'sections', sections)
