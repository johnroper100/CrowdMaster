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

"""Here is some common code that is used throughout CrowdMaster. It is placed here to make my life easier when trying to find things."""

# Standard preferences definition
preferences = context.user_preferences.addons[__package__].preferences

# Preferences definition when not inheriting CONTEXT
preferences = bpy.context.user_preferences.addons[__package__].preferences

# Preferences definition when module gives errors with __package__
preferences = context.user_preferences.addons["CrowdMaster"].preferences
