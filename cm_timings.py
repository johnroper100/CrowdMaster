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

import logging
from collections import OrderedDict

from .cm_channels import channelTimes

logger = logging.getLogger("CrowdMaster")

placement = OrderedDict([
    ("Construct", 0),
    ("Build", 0),
    ("GeoTemplateOBJECT", 0),
    ("GeoTemplateGROUP", 0),
    ("GeoTemplateLINKGROUPNODE", 0),
    ("GeoTemplateCONSTRAINBONE", 0),
    ("GeoTemplateMODIFYBONE", 0),
    ("GeoTemplatePARENT", 0),
    ("TemplateADDTOGROUP", 0),
    ("TemplateRANDOMMATERIAL", 0),
    ("TemplateAGENT", 0),
    ("TemplateAGENT-Build", 0),
    ("TemplateAGENT-cm_agent_add", 0),
    ("TemplateOFFSET", 0),
    ("TemplateRANDOM", 0),
    ("TemplatePOINTTOWARDS", 0),
    ("TemplateRANDOMPOSITIONING", 0),
    ("TemplateMESHPOSITIONING", 0),
    ("TemplateVCOLPOSITIONING", 0),
    ("TemplatePATH", 0),
    ("TemplateFORMATION", 0),
    ("TemplateTARGET", 0),
    ("TemplateOBSTACLE", 0),
    ("TemplateGROUND", 0),
    ("cm_agent_add", 0),
    ("cm_agent_add-find_category", 0),
    ("cm_agent_add-create_entry", 0),
    ("cm_agent_add-initial_tags", 0),
    ("cm_agent_add-modify_bones", 0)
])

placementNum = OrderedDict([
    ("Construct", 0),
    ("Build", 0),
    ("GeoTemplateOBJECT", 0),
    ("GeoTemplateGROUP", 0),
    ("GeoTemplateLINKGROUPNODE", 0),
    ("GeoTemplateCONSTRAINBONE", 0),
    ("GeoTemplateMODIFYBONE", 0),
    ("GeoTemplatePARENT", 0),
    ("TemplateADDTOGROUP", 0),
    ("TemplateRANDOMMATERIAL", 0),
    ("TemplateAGENT", 0),
    ("TemplateAGENT-Build", 0),
    ("TemplateAGENT-cm_agent_add", 0),
    ("TemplateOFFSET", 0),
    ("TemplateRANDOM", 0),
    ("TemplatePOINTTOWARDS", 0),
    ("TemplateRANDOMPOSITIONING", 0),
    ("TemplateMESHPOSITIONING", 0),
    ("TemplateVCOLPOSITIONING", 0),
    ("TemplatePATH", 0),
    ("TemplateFORMATION", 0),
    ("TemplateTARGET", 0),
    ("TemplateOBSTACLE", 0),
    ("TemplateGROUND", 0),
    ("cm_agent_add", 0),
    ("cm_agent_add-find_category", 0),
    ("cm_agent_add-create_entry", 0),
    ("cm_agent_add-initial_tags", 0),
    ("cm_agent_add-modify_bones", 0)
])

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
    logger.debug("Placement")
    for k, v in placement.items():
        n = placementNum[k]
        logger.debug("     {} {} {} {}".format(k, v, n, v / max(n, 1)))
    logger.debug("Agent")
    for k, v in agent.items():
        logger.debug("     {} {}".format(k, v))
    logger.debug("Brain")
    for k, v in brain.items():
        logger.debug("     {} {}".format(k, v))
    logger.debug("Simulation")
    for k, v in simulation.items():
        logger.debug("     {} {}".format(k, v))
    logger.debug("Neuron")
    for k, v in neuron.items():
        logger.debug("     {} {}".format(k, v))
    logger.debug("Cores")
    for k, v in coreTimes.items():
        n = coreNumber[k]
        logger.debug("     {} {} {} {}".format(k, v, n, v / max(n, 1)))
    logger.debug("Channel times")
    for k in sorted(channelTimes):
        v = channelTimes[k]
        logger.debug("     {} {}".format(k, sum(v.values())))
        for k1 in sorted(v):
            v1 = v[k1]
            logger.debug("          {} {}".format(k1, v1))
