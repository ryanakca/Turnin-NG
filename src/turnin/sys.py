import pwd
import grp
import os

def chown(path, user, group):
    """
    Change the owner and the group of 'path'

    @type path: string
    @param path: file / directory for which to change the owner/group
    @type user: string
    @param user: username
    @type group: string
    @param group: groupname
    @rtype: function
    @return: Function to change the owner and group of 'path'

    """
    return os.chown(path, pwd.getpwnam(user)[2], grp.getgrnam(group)[2])
