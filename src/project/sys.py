import pwd
import grp
import os

def chown(path, user, group):
    return os.chown(path, pwd.getpwnam(user)[2], grp.getgrnam(group)[2])
