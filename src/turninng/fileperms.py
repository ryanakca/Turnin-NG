# Turnin-NG, an assignment submitter and manager. --- Custom system utilities
# Copyright (C) 2009  Ryan Kavanagh <ryanakca@kubuntu.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import errno
import pwd
import grp
import os
import shutil
import tempfile

from shutil import Error
from stat import ST_UID, ST_GID

def chown(path, user='', group=''):
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
    if user:
        UID = pwd.getpwnam(user)[2]
    else:
        # Set to -1 to leave unchanged.
        UID = -1
    if group:
        GID = grp.getgrnam(group)[2]
    else:
        GID = -1
    return os.chown(path, UID, GID)

def chgrp(path, group):
    """
    Change the group of 'path'

    @type path: string
    @param path: file / directory for which to change the group
    @type group: string
    @param group: group name
    @rtype: function
    @return: Function to change the group of path

    """
    return chown(path, group=group)

def chmod_hack(path):
    """
    We need to be the owner of 'path' to be able to change the permissions. This
    convoluted hack is necessary if we want to change the permissions of a
    directory we have g+rwx, but not u+rwx.

    Loosely based on the sourcecode for shutil.copytree

    @type path: string
    @param path: file / directory on which to change permissions
    @return: None

    """
    # Get the name of the group that owns path
    path_group = grp.getgrgid(os.stat(path)[ST_GID])[0]
    temp_dir = tempfile.mkdtemp()
    files = os.listdir(path)
    errors = []
    for file in files:
        src = os.path.join(path, file)
        dst = os.path.join(temp_dir, file)
        try:
            if os.path.islink(src):
                linkto = os.readlink(src)
                os.symlink(linkto, dst)
            elif os.path.isdir(src):
                shutil.copytree(src, dst, symlinks=True)
            else:
                shutil.copy2(src, dst)
        except (IOError, os.error), why:
            errors.append((src, dst, str(why)))
        except Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(path, temp_dir)
        shutil.rmtree(path)
        os.rename(temp_dir, path)
        chgrp(path, path_group)
    except OSError, why:
        errors.extend((path, temp_dir, str(why)))
    if errors:
        raise Error(errors)

def chmod(path, permissions):
    """
    Change the permissions of 'path'

    @type path: string
    @param path: file / directory on which to change permissions
    @type permissions: int
    @param permissions: 4 digit octal permissions for path
    @return: None
    @raise ValueError: permissions aren't valid octal permissions

    """
    if not 0 <= permissions <= 7777:
        raise ValueError("%s are invalid octal permissions", oct(permissions))
    # Do we own the file or are we root?
    if os.stat(path)[ST_UID] != os.geteuid() and os.geteuid() != 0:
        # Ewwww!
        chmod_hack(path)
    os.chmod(path, permissions)
