import numpy as np

MP = True       # Mediapipe available

class Expression():
    def __init__(self, state, params):
        self.state = state
        self.command = params['COMMAND']
        self.waitTime = params['WAIT']
        self.text = params['TEXT']
        self.condition = params['CONDITION']
        self.landmarks = params['LANDMARKS']

    def check(self, LM):
        return False

    def __str__(self):
        txt  = self.text + '\n'
        txt += self.waitTime.__str__() + '\n'
        txt += self.condition.__str__() + '\n'
        txt += self.landmarks.__str__() + '\n'
        return txt

    def dist(self, p1, p2):
        if MP:
            return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
        else:
            return np.linalg.norm(p1 - p2)

class smileExpr(Expression):
    def check(self, LM):
        state = False
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[ self.landmarks[0]])
        if w_mouth > (w_face * self.condition):
            state = True
        return state

class mouthOpenExpr(Expression):
    def check(self, LM):
        state = False
        w_mouth = self.dist(LM[self.landmarks[0]], LM[self.landmarks[1]])
        h_mouth = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        mar = h_mouth / w_mouth if w_mouth != 0 else 0
        if mar > self.condition:
            state = True
        return state

class TiltRightExpr(Expression):
    def check(self, LM):
        state = False
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[ self.landmarks[0]])
        if w_mouth > (w_face * self.condition):
            state = True
        return state

class TiltLeftExpr(Expression):
    def check(self, LM):
        state = False
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[ self.landmarks[0]])
        if w_mouth > (w_face * self.condition):
            state = True
        return state

class kissExpr(Expression):
    def check(self, LM):
        state = False
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]], LM[self.landmarks[0]])
        if w_mouth < (w_face * self.condition):
            state = True
        return state

class tongueRightExpr(Expression):
    def check(self, LM):
        state = False
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[self.landmarks[0]])
        if w_mouth > (w_face * self.condition):
            state = True
        return state

class tongueLeftExpr(Expression):
    def check(self, LM):
        state = False
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[self.landmarks[0]])
        if w_mouth > (w_face * self.condition):
            state = True
        return state



