import pwd
import os

def chmod(path, user, group):
    return os.chmod(path, pwd.getpwnam[2], pwd.getpwnam[3])
