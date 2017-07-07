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
        # Toolbars
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
        ("*", "No group selected"): "Spanish Here",
        ("*", "Manual Agents"): "Spanish Here",
        ("*", "Brain Type"): "Spanish Here",
        ("Operator", "Create Manual Agents"): "Spanish Here",
        ("*", "Armature Action"): "Spanish Here",
        ("*", "Motion Action"): "Spanish Here",
        ("*", "Action pairings:"): "Spanish Here",
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
        # User Prefs
        ("*", "General Settings"): "Spanish Here",
        ("*", "Addon Update Settings"): "Spanish Here",
        ("*", "Debug Options"): "Spanish Here",
        ("*", "Use Custom Icons"): "Spanish Here",
        ("*", "Start Animation Automatically"): "Spanish Here",
        ("*", "Ask To Save"): "Spanish Here",
        ("*", "Use Node Color"): "Spanish Here",
        ("*", "Show Debug Options"): "Spanish Here",
        ("Operator", "Our Website"): "Spanish Here",
        ("Operator", "Email Us"): "Spanish Here",
        ("Operator", "Save Settings"): "Spanish Here",
        ("*", "Updater Settings"): "Spanish Here",
        ("*", "Auto-check for Update"): "Spanish Here",
        ("*", "Interval between checks"): "Spanish Here",
        ("*", "Months"): "Spanish Here",
        ("*", "Days"): "Spanish Here",
        ("*", "Hours"): "Spanish Here",
        ("*", "Minutes"): "Spanish Here",
        ("Operator", "Check now for crowdmaster update"): "Spanish Here",
        ("Operator", "Install latest develop / old version"): "Spanish Here",
        ("Operator", "Restore addon backup (none found)"): "Spanish Here",
        ("Operator", "Run Short Tests"): "Spanish Here",
        ("Operator", "Run Long Tests"): "Spanish Here",
        ("*", "Show Debug Timings"): "Spanish Here",
        ("*", "Enable Show Debug Options to access these settings (only for developers)."): "Spanish Here",
        # Node names
        # generation
        ("*", "Constrain Bone"): "Spanish Here",
        ("*", "Link Armature"): "Spanish Here",
        ("*", "Modify Bone"): "Spanish Here",
        ("*", "Add To Group"): "Spanish Here",
        ("*", "Combine"): "Spanish Here",
        ("*", "Point Towards"): "Spanish Here",
        ("*", "Random Material"): "Spanish Here",
        ("*", "Set Tag"): "Spanish Here",
        ("*", "Positioning"): "Spanish Here",
        ("*", "Formation"): "Spanish Here",
        ("*", "Ground"): "Spanish Here",
        # simulation
        ("*", "Print"): "Spanish Here",
        ("*", "Graph"): "Spanish Here",
        ("*", "Map"): "Spanish Here",
        ("*", "Logic"): "Spanish Here",
        ("*", "Strong"): "Spanish Here",
        ("*", "Weak"): "Spanish Here",
        # Node props
        # simulation
        ("*", "Agent Info"): "Spanish Here",
        ("*", "Agent Info Options"): "Spanish Here",
        ("*", "Get Tag Name"): "Spanish Here",
        ("*", "Get Tag"): "Spanish Here",
        ("*", "Heading rx"): "Spanish Here",
        ("*", "Heading rz"): "Spanish Here",
        ("*", "Flocking Input"): "Spanish Here",
        ("*", "Translation Axis"): "Spanish Here",
        ("*", "Cohere"): "Spanish Here",
        ("*", "Formation Group"): "Spanish Here",
        ("*", "Ground Group"): "Spanish Here",
        ("*", "Ground Options"): "Spanish Here",
        ("*", "ahead rx"): "Spanish Here",
        ("*", "ahead rz"): "Spanish Here",
        ("*", "Noise Options"): "Spanish Here",
        ("*", "Agent Random"): "Spanish Here",
        ("*", "Path Name"): "Spanish Here",
        ("*", "Prediction"): "Spanish Here",
        ("*", "Minus radius"): "Spanish Here",
        ("*", "State Options"): "Spanish Here",
        ("*", "Query tag"): "Spanish Here",
        ("*", "World Options"): "Spanish Here",
        ("*", "Event"): "Spanish Here",
        ("*", "Multi Input Type"): "Spanish Here",
        ("*", "Save To File"): "Spanish Here",
        ("*", "Output Filepath"): "Spanish Here",
        ("*", "Lower Input"): "Spanish Here",
        ("*", "Upper Input"): "Spanish Here",
        ("*", "Lower Output"): "Spanish Here",
        ("*", "Upper Output"): "Spanish Here",
        ("*", "Single Output"): "Spanish Here",
        ("*", "Include All"): "Spanish Here",
        ("*", "State Length"): "Spanish Here",
        ("*", "Cycle State"): "Spanish Here",
        ("*", "Action Name"): "Spanish Here",
        ("*", "Interupt State"): "Spanish Here",
        ("*", "Sync State"): "Spanish Here",
        ("*", "Random wait time:"): "Spanish Here",
        ("*", "Not equal"): "Spanish Here",
        ("*", "Less than"): "Spanish Here",
        ("*", "Greater than"): "Spanish Here",
        ("*", "Least only"): "Spanish Here",
        ("*", "Most only"): "Spanish Here",
        ("*", "Set To"): "Spanish Here",
        ("*", "Tag Name"): "Spanish Here",
        ("*", "Use Threshold"): "Spanish Here",
        ("*", "Note Text"): "Spanish Here",
        ("Operator", "Grab Text From Clipboard"): "Spanish Here",
        ("*", "Rotation Axis"): "Spanish Here",
        ("*", "Formation Options"): "Spanish Here",
        ("*", "Ground Ahead Offset"): "Spanish Here",
        ("*", "Path Options"): "Spanish Here",
        ("*", "In lane"): "Spanish Here",
        ("*", "Search Distance"): "Spanish Here",
        ("*", "close"): "Spanish Here",
        ("*", "over"): "Spanish Here",
        ("*", "Global Vel X"): "Spanish Here",
        ("*", "Global Vel Y"): "Spanish Here",
        ("*", "Global Vel X"): "Spanish Here",
        ("*", "Target Options"): "Spanish Here",
        ("*", "Arrived"): "Spanish Here",
        ("*", "Event Name"): "Spanish Here",
        ("*", "Size Average"): "Spanish Here",
        ("*", "Sum"): "Spanish Here",
        ("*", "Lower Zero"): "Spanish Here",
        ("*", "Lower One"): "Spanish Here",
        ("*", "Upper One"): "Spanish Here",
        ("*", "Upper Zero"): "Spanish Here",
        # generation
        ("*", "Parent Group"): "Spanish Here",
        ("*", "Group File"): "Spanish Here",
        ("*", "Duplicates Directory"): "Spanish Here",
        ("*", "Rig Object"): "Spanish Here",
        ("*", "Additional Groups"): "Spanish Here",
        ("*", "Parent To (Bone)"): "Spanish Here",
        ("*", "Geo Switch"): "Spanish Here",
        ("*", "Defer Geometry"): "Spanish Here",
        ("*", "Group name:"): "Spanish Here",
        ("*", "Point to Object"): "Spanish Here",
        ("*", "Point Type"): "Spanish Here",
        ("*", "Min Rand Rotation"): "Spanish Here",
        ("*", "Max Rand Rotation"): "Spanish Here",
        ("*", "Min Rand Scale"): "Spanish Here",
        ("*", "Max Rand Scale"): "Spanish Here",
        ("*", "Target Material"): "Spanish Here",
        ("*", "Template Switch"): "Spanish Here",
        ("*", "Formation Positioning"): "Spanish Here",
        ("*", "Number of Agents"): "Spanish Here",
        ("*", "Rows"): "Spanish Here",
        ("*", "Row Margin"): "Spanish Here",
        ("*", "Column Margin"): "Spanish Here",
        ("*", "Guide Mesh"): "Spanish Here",
        ("*", "Overwrite position"): "Spanish Here",
        ("*", "Relax Iterations"): "Spanish Here",
        ("*", "Relax Radius"): "Spanish Here",
        ("*", "Obstacles"): "Spanish Here",
        ("*", "Location Object"): "Spanish Here",
        ("*", "Location Offset"): "Spanish Here",
        ("*", "Rotation Offset"): "Spanish Here",
        ("*", "Group By Mesh Islands"): "Spanish Here",
        ("*", "Sector"): "Spanish Here",
        ("*", "Target Type"): "Spanish Here",
        ("*", "Target Positioning"): "Spanish Here",
        ("*", "Place"): "Spanish Here",
        ("*", "Guide Mesh"): "Spanish Here",
        ("Operator", "Generate Agents"): "Spanish Here",
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