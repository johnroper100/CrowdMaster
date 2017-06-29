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


class syncManager:
    def __init__(self):
        self.messages = {}
        # {"source": {"target": {"action": (state, value)}}}
        self.actionPairs = {}
        # {"Source action": {"Target action"}}

    def newFrame(self):
        self.lastFrame = self.resolveSync()
        self.messages = {}

    def actionPair(self, action0, action1):
        if action0 not in self.actionPairs:
            self.actionPairs[action0] = []
        if action1 not in self.actionPairs[action0]:
            self.actionPairs[action0].append(action1)

    def tell(self, source, target, action, value, state):
        """
        :param source: The name of the source agent.
        :param target: The name of the target agent.
        :param action: The name of the action.
        :param value: The value associated with the action.
        :param state: The name of the state node broadcasting.
        """
        if source not in self.messages:
            self.messages[source] = {}
        src = self.messages[source]
        if target not in src:
            src[target] = {}
        tgt = src[target]
        if action not in tgt:
            tgt[action] = (state, value)
        else:
            tgt[action] = max(tgt[action], (state, value), key=lambda x: x[1])

    def resolveSync(self):
        seenPairs = set()
        pairs = []
        for source in self.messages:
            for target in self.messages[source]:
                # For the same input pair s0 and s1 will always be the same
                if source < target:
                    s0 = source
                    s1 = target
                else:
                    s0 = target
                    s1 = source
                if (s0, s1) in seenPairs:
                    continue  # We've seen this pair already
                else:
                    seenPairs.add((s0, s1))
                    # Don't evaluate the same pair again
                messagesPresent = s0 in self.messages and s1 in self.messages
                if messagesPresent:
                    messagesPresent = s0 in self.messages[s1]
                    messagesPresent &= s1 in self.messages[s0]
                if messagesPresent:
                    m0 = self.messages[s0][s1]  # All messages from a -> b
                    m1 = self.messages[s1][s0]  # All messages from b -> a
                    for action, (state, value) in m0.items():
                        if action in self.actionPairs:
                            bestState = None
                            bestAction = None
                            bestScore = 0
                            for possiblePair in self.actionPairs[action]:
                                if possiblePair in m1:
                                    s, v = m1[possiblePair]
                                    score = v * value
                                    if score > bestScore:
                                        bestState = s
                                        bestAction = possiblePair
                                        bestScore = score
                            if bestScore > 0:
                                # All possible pairings get to this point
                                pairs.append(((s0, (state, action)),
                                              (s1, (bestState, bestAction)),
                                              bestScore))
        # Starting at maximum valued pair assign actions if no action has
        #    already been assigned to either agent.
        seenAgents = set()
        agentActions = {}
        for pair in sorted(pairs, key=lambda x: x[2], reverse=True):
            if pair[0][0] not in seenPairs and pair[1][0] not in seenPairs:
                agentActions[pair[0][0]] = (pair[0][1], pair[1][0])
                agentActions[pair[1][0]] = (pair[1][1], pair[0][0])
                seenPairs.add(pair[0][0])
                seenPairs.add(pair[1][0])
        # agentActions in the form {fromActions: ((state, action), otherAgent)}
        return agentActions

    def getResult(self, agentName):
        if agentName in self.lastFrame:
            return self.lastFrame[agentName]
        else:
            return (None, None), None


class SyncManagerTestCase(unittest.TestCase):
    def testCase(self):
        sm = syncManager()
        sm.actionPair("attack", "defence")
        sm.actionPair("defence", "attack")
        sm.actionPair("kill", "die")
        sm.actionPair("die", "kill")

        sm.tell("z", "y", "attack", 0.6, "attackState")
        sm.tell("z", "y", "defence", 0.2, "defenceState")
        sm.tell("z", "y", "kill", 0.1, "killState")
        sm.tell("z", "y", "die", 0.0, "dieState")

        sm.tell("z", "x", "attack", 0.5, "attackState")
        sm.tell("z", "x", "defence", 0.5, "defenceState")
        sm.tell("z", "x", "kill", 0.0, "killState")
        sm.tell("z", "x", "die", 0.0, "dieState")

        sm.tell("x", "z", "attack", 0.9, "attackState")

        sm.tell("y", "z", "attack", 0.1, "attackState")
        sm.tell("y", "z", "defence", 0.9, "defenceState")

        self.assertEqual(sm.resolveSync(), {'z': (('attackState', 'attack'), 'y'),
                                            'y': (('defenceState', 'defence'), 'z')})

    def testCase2(self):
        sm = syncManager()
        sm.actionPair("attack", "impact")
        sm.actionPair("attack", "death1")
        sm.actionPair("attack", "death2")

        sm.actionPair("death1", "attack")
        sm.actionPair("death1", "slash")

        sm.actionPair("slash", "impact")
        sm.actionPair("slash", "death1")
        sm.actionPair("slash", "death2")

        sm.actionPair("death2", "attack")
        sm.actionPair("death2", "slash")

        sm.actionPair("impact", "attack")
        sm.actionPair("impact", "slash")

        sm.tell("x", "y", "death1", 1.5322003178298897, "Action.005")
        sm.tell("x", "y", "attack", 1.0213593144361799, "Action.001")
        sm.tell("x", "y", "slash", 1.0213593144361799, "Action.001")
        sm.tell("x", "y", "death2", 0.5322003178298897, "Action.005")
        sm.tell("x", "y", "impact", 1.012717818329232, "Action.002")

        sm.tell("y", "x", "death1", 0.5275212760897328, "Action.005")
        sm.tell("y", "x", "attack", 1.0282780862831944, "Action.001")
        sm.tell("y", "x", "slash", 1.0282780862831944, "Action.001")
        sm.tell("y", "x", "death2", 0.5275212760897328, "Action.005")
        sm.tell("y", "x", "impact", 1.0214241096853804, "Action.002")

        result = sm.resolveSync()
        self.assertEqual(result, {'y': (('Action.001', 'attack'), 'x'),
                                  'x': (('Action.005', 'death1'), 'y')})
