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

coreTimes = OrderedDict([
    ("LogicINPUT", 0),
    ("LogicNEWINPUT", 0),
    ("LogicGRAPH", 0),
    ("LogicMATH", 0),
    ("LogicAND", 0),
    ("LogicOR", 0),
    ("LogicSTRONG", 0),
    ("LogicWEAK", 0),
    ("LogicQUERYTAG", 0),
    ("LogicSETTAG", 0),
    ("LogicVARIABLE", 0),
    ("LogicFILTER", 0),
    ("LogicMAP", 0),
    ("LogicOUTPUT", 0),
    ("LogicPRIORITY", 0),
    ("LogicEVENT", 0),
    ("LogicPYTHON", 0),
    ("LogicPRINT", 0)
])

coreNumber = OrderedDict([
    ("LogicINPUT", 0),
    ("LogicNEWINPUT", 0),
    ("LogicGRAPH", 0),
    ("LogicMATH", 0),
    ("LogicAND", 0),
    ("LogicOR", 0),
    ("LogicSTRONG", 0),
    ("LogicWEAK", 0),
    ("LogicQUERYTAG", 0),
    ("LogicSETTAG", 0),
    ("LogicVARIABLE", 0),
    ("LogicFILTER", 0),
    ("LogicMAP", 0),
    ("LogicOUTPUT", 0),
    ("LogicPRIORITY", 0),
    ("LogicEVENT", 0),
    ("LogicPYTHON", 0),
    ("LogicPRINT", 0)
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
    print("Cores")
    for k, v in coreTimes.items():
        n = coreNumber[k]
        print("     ", k, v, n, v/max(n, 1))
    print("Channel times")
    for k in sorted(channelTimes):
        v = channelTimes[k]
        print("     ", k, sum(v.values()))
        for k1 in sorted(v):
            v1 = v[k1]
            print("          ", k1, v1)
