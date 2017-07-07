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

import bpy

translations = {
    'es': {
        ("Operator", "Start Simulation"): "Spanish Here",
        ("Operator", "Stop Simulation"): "Spanish Here",
        ("*", "Utilities"): "Spanish Here",
        ("Operator", "Place Deferred Geometry"): "Spanish Here",
        ("Operator", "Convert Selected To Bounding Box"): "Spanish Here",
        ("Operator", "Switch Dupli Groups"): "Spanish Here",
        ("*", "Dupli Group Suffix"): "Spanish Here",
        ("*", "Dupli Group Target"): "Spanish Here",
        ("*", "Agents"): "Spanish Here",
        ("*", "Group Name"): "Spanish Here",
        ("*", "Number | Origin"): "Spanish Here",
        ("*", "View Group Details"): "Spanish Here",
        ("*", "Manual Agents"): "Spanish Here",
        ("*", "Brain Type"): "Spanish Here",
        ("Operator", "Create Manual Agents"): "Spanish Here",
        ("*", "Armature Action"): "Spanish Here",
        ("*", "Motion Action"): "Spanish Here",
        ("*", "Action pairings"): "Spanish Here",
        ("*", "Events"): "Spanish Here",
        ("*", "Time+Volume"): "Spanish Here",
        ("*", "Road"): "Spanish Here",
        ("*", "Bidirectional"): "Spanish Here",
        ("Operator", "Breadth First Search To Direct Edges"): "Spanish Here",
        ("Operator", "Depth First Search To Direct Edges"): "Spanish Here",
        ("Operator", "Switch The Direction Of The Connected Edges"): "Spanish Here",
        ("Operator", "Switch The Direction Of The Selected Edges"): "Spanish Here",
        ("*", "Lane Separation"): "Spanish Here",
        ("Operator", "Draw The Directions Of A Path"): "Spanish Here",
    }
}

def register():
    # Register translations
    bpy.app.translations.register(__name__, translations)


def unregister():
    # Unregister translations
    bpy.app.translations.unregister(__name__)


if __name__ == "__main__":
    register()