from project.configparser import ProjectGlobal, ProjectCourse

def create_course(config_file, course):
    project = ProjectCourse(config_file, course)
    user = raw_input("Username [usually your UNIX login]: ")
    directory = raw_input("Full path to project directory: ")
    group = raw_input("Group: ")
    sections = raw_input("Sections: ")
    project.write(user, directory, group, sections) 
    print "Successfully created the course %s." % course
