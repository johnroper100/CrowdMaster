from cm_generation import cm_templates
from libs.ins_vector import Vector

import time

t = time.time()

ag = cm_templates.TemplateAGENT([], {"brainType": "human"}, "AGENT")
co = cm_templates.TemplateAGENT([], {"brainType": "troll"}, "AGENT.001")
rd = cm_templates.TemplateRANDOM([ag], {"posRange": Vector((0.05,0.05,0)),  "rotRange":Vector((0,0,0.01)), "scaleRange":0.2, "scaleFactor": 1}, "RANDOM")
rc = cm_templates.TemplateRANDOM([co], {"posRange": Vector((0.05,0.05,0)),  "rotRange":Vector((0,0,0.01)), "scaleRange":0.2, "scaleFactor": 4}, "RANDOM.001")
sw = cm_templates.TemplateSWITCH([rd, rc], {"weights": [4, 1]}, "SWITCH")
ly = cm_templates.TemplateLAYOUT([sw], {}, "LAYOUT")

if ly.checkRecursive():
    ly.build(Vector((0,0,0)), Vector((0,0,0)), 1, {})
else:
    print("Error in graph or settings")

print("Total time:", time.time() - t)
