## Copyright (C) 2007 Red Hat, Inc., Adam Stokes <astokes@redhat.com>

### This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from sos.plugins import Plugin, RedHatPlugin, UbuntuPlugin, DebianPlugin
import os, re

class autofs(Plugin):
    """autofs server-related information
    """

    plugin_name = "autofs"

    files = ('/etc/sysconfig/autofs', '/etc/default/autofs')
    packages = ('autofs',)

    def checkdebug(self):
        """ testing if autofs debug has been enabled anywhere
        """
        # Global debugging
        opt = self.fileGrep(r"^(DEFAULT_LOGGING|DAEMONOPTIONS)=(.*)", *self.files)
        for opt1 in opt:
            for opt2 in opt1.split(" "):
                if opt2 in ("--debug", "debug"):
                    return True
        return False

    def getdaemondebug(self):
        """ capture daemon debug output
        """
        debugout = self.fileGrep(r"^(daemon.*)\s+(\/var\/log\/.*)", *self.files)
        for i in debugout:
            return i[1]

    def setup(self):
        self.addCopySpec("/etc/auto*")
        self.collectExtOutput("/etc/init.d/autofs status")
        self.collectExtOutput("ps auxwww | grep automount")
        self.collectExtOutput("/bin/egrep -e 'automount|pid.*nfs' /proc/mounts")
        self.collectExtOutput("/bin/mount | egrep -e 'automount|pid.*nfs'")
        if self.checkdebug():
            self.addCopySpec(self.getdaemondebug())

class RedHatAutofs(autofs, RedHatPlugin):
    """autofs server-related on RedHat based distributions"""

    def setup(self):
        super(RedHatAutofs, self).setup()
        self.collectExtOutput("/bin/rpm -qV autofs")

class DebianAutofs(autofs, DebianPlugin, UbuntuPlugin):
    """autofs server-related on Debian based distributions"""

    def setup(self):
        super(DebianAutofs, self).setup()
        self.collectExtOutput("/usr/bin/dpkg-query -s autofs")
