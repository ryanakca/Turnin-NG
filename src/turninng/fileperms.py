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

import pwd
import grp
import os

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
