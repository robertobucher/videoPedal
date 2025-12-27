import numpy as np

MP = True       # Mediapipe available

class Expression():
    def __init__(self, state, params):
        self.state = state
        self.command = params['COMMAND']
        self.waitTime = params['WAIT']
        self.text = params['TEXT']
        self.condition = params['COND']
        self.landmarks = params['LANDMARK']

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
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[ self.landmarks[0]])
        state = w_mouth > (w_face * self.condition)
        return state

class mouthOpenExpr(Expression):
    def check(self, LM):
        w_mouth = self.dist(LM[self.landmarks[0]], LM[self.landmarks[1]])
        h_mouth = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        mar = h_mouth / w_mouth if w_mouth != 0 else 0
        state = mar > self.condition
        return state

class TiltRightExpr(Expression):
    def check(self, LM):
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[ self.landmarks[0]])
        state =  w_mouth > (w_face * self.condition)
        return state

class TiltLeftExpr(Expression):
    def check(self, LM):
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[ self.landmarks[0]])
        state = w_mouth > (w_face * self.condition)
        return state

class kissExpr(Expression):
    def check(self, LM):
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]], LM[self.landmarks[0]])
        state =  w_mouth < (w_face * self.condition)
        return state

class tongueRightExpr(Expression):
    def check(self, LM):
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[self.landmarks[0]])
        state = w_mouth > (w_face * self.condition)
        return state

class tongueLeftExpr(Expression):
    def check(self, LM):
        w_face = self.dist(LM[self.landmarks[2]], LM[self.landmarks[3]])
        w_mouth = self.dist(LM[self.landmarks[1]],LM[self.landmarks[0]])
        state = w_mouth > (w_face * self.condition)
        return state

class puffLeftExpr(Expression):
    def check(self, LM):
        w_puff = self.dist(LM[self.landmarks[1]],LM[self.landmarks[0]])
        state = w_puff > self.condition
        return state

class puffRightExpr(Expression):
    def check(self, LM):
        w_puff = self.dist(LM[self.landmarks[1]],LM[self.landmarks[0]])
        state = w_puff > self.condition
        return state



