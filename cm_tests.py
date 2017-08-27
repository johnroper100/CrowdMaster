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

import unittest

import bpy
from bpy.types import Operator

from .cm_syncManager import SyncManagerTestCase


class AddonRegisterTestCase(unittest.TestCase):
    def setUp(self):
        self.play_animation = bpy.context.user_preferences.addons[
            __package__].preferences.play_animation
        bpy.ops.wm.read_homefile()
        bpy.context.user_preferences.addons[__package__].preferences.play_animation = False

    def tearDown(self):
        bpy.context.user_preferences.addons[__package__].preferences.play_animation = self.play_animation

    def testStartStopSim(self):
        pa = bpy.context.user_preferences.addons[__package__].preferences.play_animation
        bpy.ops.scene.cm_start()
        bpy.ops.scene.cm_stop()

    def testRegistered(self):
        sceneProps = ["cm_actions", "cm_events", "cm_groups",
                      "cm_groups_index", "cm_manual",
                      "cm_paths", "cm_view_details", "cm_view_details_index"]
        for sp in sceneProps:
            self.assertIn(sp, dir(bpy.context.scene))

        opsProps = ["cm_actions_populate", "cm_actions_remove", "cm_agent_add",
                    "cm_agent_add_selected", "cm_agent_nodes_generate",
                    "cm_agents_move", "cm_events_move",
                    "cm_events_populate", "cm_events_remove",
                    "cm_groups_reset",
                    "cm_paths_populate", "cm_paths_remove",
                    "cm_place_deferred_geo", "cm_run_long_tests",
                    "cm_run_short_tests", "cm_save_prefs",
                    "cm_start", "cm_stop"]
        for op in opsProps:
            self.assertIn(op, dir(bpy.ops.scene))


def createShortTestSuite():
    """Gather all the short tests from this module in a test suite"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(AddonRegisterTestCase))
    test_suite.addTest(unittest.makeSuite(SyncManagerTestCase))
    return test_suite


def createLongTestSuite():
    """Gather all the long tests from this module in a test suite"""
    test_suite = unittest.TestSuite()
    return test_suite


class CrowdMaster_run_short_tests(Operator):
    """For tests cases that will run quickly.
    ie. that don't involve running simulations"""
    bl_idname = "scene.cm_run_short_tests"
    bl_label = "Run Short Tests"

    def execute(self, context):
        testSuite = createShortTestSuite()
        test = unittest.TextTestRunner()
        result = test.run(testSuite)
        if not result.wasSuccessful():
            return {'CANCELLED'}
        return {'FINISHED'}


class CrowdMaster_run_long_tests(Operator):
    """For tests cases that will take a long time.
    ie. that involve simulation"""
    bl_idname = "scene.cm_run_long_tests"
    bl_label = "Run Long Tests"

    def execute(self, context):
        testSuite = createLongTestSuite()
        test = unittest.TextTestRunner()
        result = test.run(testSuite)
        if not result.wasSuccessful():
            return {'CANCELLED'}
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CrowdMaster_run_short_tests)
    bpy.utils.register_class(CrowdMaster_run_long_tests)


def unregister():
    bpy.utils.unregister_class(CrowdMaster_run_short_tests)
    bpy.utils.unregister_class(CrowdMaster_run_long_tests)
