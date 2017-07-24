# Copyright 2017 CrowdMaster Developer Team
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

from collections import OrderedDict

from .cm_channels import channelTimes

placement = OrderedDict([
    ("GROUP", 0),
    ("GROUPA", 0),
    ("GROUPB", 0),
    ("deferGeoB", 0)
])

def printPlacementTimings():
    print("Placement")
    for k, v in placement.items():
        print("     ", k, v)

agent = OrderedDict([
    ("init", 0),
    ("brainExecute", 0),
    ("highLight", 0),
    ("setOutput", 0),
    ("applyOutput", 0)
])

brain = OrderedDict([
    ("setUser", 0),
    ("newFrame", 0),
    ("evaluate", 0),
    ("evalState", 0)
])

simulation = OrderedDict([
    ("total", 0),
    ("betweenFrames", 0),
    ("totalFrames", 0)
])

neuron = OrderedDict([
    ("deps", 0),
    ("sumColour", 0)
])

coreTimes = OrderedDict([
    ("LogicINPUT", 0),
    ("LogicNEWINPUT", 0),
    ("LogicGRAPH", 0),
    ("LogicMATH", 0),
    ("LogicAND", 0),
    ("LogicOR", 0),
    ("LogicNOT", 0),
    ("LogicSTRONG", 0),
    ("LogicWEAK", 0),
    ("LogicSETTAG", 0),
    ("LogicFILTER", 0),
    ("LogicMAP", 0),
    ("LogicOUTPUT", 0),
    ("LogicPRIORITY", 0),
    ("LogicEVENT", 0),
    ("LogicPRINT", 0)
])

coreNumber = OrderedDict([
    ("LogicINPUT", 0),
    ("LogicNEWINPUT", 0),
    ("LogicGRAPH", 0),
    ("LogicMATH", 0),
    ("LogicAND", 0),
    ("LogicOR", 0),
    ("LogicNOT", 0),
    ("LogicSTRONG", 0),
    ("LogicWEAK", 0),
    ("LogicSETTAG", 0),
    ("LogicFILTER", 0),
    ("LogicMAP", 0),
    ("LogicOUTPUT", 0),
    ("LogicPRIORITY", 0),
    ("LogicEVENT", 0),
    ("LogicPRINT", 0)
])


def printTimings():
    print("Agent")
    for k, v in agent.items():
        print("     ", k, v)
    print("Brain")
    for k, v in brain.items():
        print("     ", k, v)
    print("Simulation")
    for k, v in simulation.items():
        print("     ", k, v)
    print("Neuron")
    for k, v in neuron.items():
        print("     ", k, v)
    print("Cores")
    for k, v in coreTimes.items():
        n = coreNumber[k]
        print("     ", k, v, n, v / max(n, 1))
    print("Channel times")
    for k in sorted(channelTimes):
        v = channelTimes[k]
        print("     ", k, sum(v.values()))
        for k1 in sorted(v):
            v1 = v[k1]
            print("          ", k1, v1)
