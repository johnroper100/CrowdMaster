# Copyright 2016 CrowdMaster Developer Team
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of CrowdMaster.
#
# CrowdMaster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CrowdMaster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CrowdMaster.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import code


class Interpreter(code.InteractiveConsole):
    """A python interpreter to run the code that is input by user to brains"""
    def __init__(self, *args):
        code.InteractiveConsole.__init__(self, *args)

    def enter(self, codesource):
        """Run code"""
        source = self.preprocess(codesource)
        self.runcode(source)

    @staticmethod
    def preprocess(codesource):
        """This could be used to add macros"""
        return codesource

    def setup(self, localvars):
        """Add pre-declared variables such as the channels"""
        self.locals = {'__name__': '__console__', '__doc__': None}
        for v in localvars:
            self.locals[v] = localvars[v]

    def getoutput(self):
        """Get the output of the scripts"""
        if "output" in self.locals:
            return self.locals["output"]
        else:
            print("Script must have out output")
