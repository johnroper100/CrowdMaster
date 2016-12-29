from collections import OrderedDict
from .cm_channels import channelTimes

placement = OrderedDict([])

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
    ("colour", 0)
])

def printTimings():
    print("Placement")
    for k, v in placement.items():
        print("     ", k, v)
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
