import numpy as np

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
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def getValue(self, LM):
        return [0,0, 0]

class smileExpr(Expression):
#     [L_MOUTH, R_MOUTH, L_FACE, R_FACE]
    def check(self, LM):
        l_mouth = LM[self.landmarks[0]]
        r_mouth = LM[self.landmarks[1]]
        l_face = LM[self.landmarks[2]]
        r_face = LM[self.landmarks[3]]
        w_face = self.dist(l_face, r_face)
        w_mouth = self.dist(l_mouth, r_mouth)
        state = (w_mouth > (w_face * self.condition))
        return state

    def getValue(self, LM):
        l_mouth = LM[self.landmarks[0]]
        r_mouth = LM[self.landmarks[1]]
        l_face = LM[self.landmarks[2]]
        r_face = LM[self.landmarks[3]]
        w_face = self.dist(l_face, r_face)
        w_mouth = self.dist(l_mouth, r_mouth)
        if self.check(LM):
            state = 0.2
        else:
            state = 0
        return [w_mouth, (w_face*self.condition), state]

class mouthOpenExpr(Expression):
#     [L_MOUTH, R_MOUTH, TOP_LIP, BOTTOM_LIP]
    def check(self, LM):
        l_mouth = LM[self.landmarks[0]]
        r_mouth = LM[self.landmarks[1]]
        top_lip = LM[self.landmarks[2]]
        bot_lip = LM[self.landmarks[3]]
        w_mouth = self.dist(l_mouth, r_mouth)
        h_mouth = self.dist(top_lip, bot_lip)
        mar = h_mouth / w_mouth if w_mouth != 0 else 0
        state = (mar > self.condition)
        return state

    def getValue(self, LM):
        l_mouth = LM[self.landmarks[0]]
        r_mouth = LM[self.landmarks[1]]
        top_lip = LM[self.landmarks[2]]
        bot_lip = LM[self.landmarks[3]]
        w_mouth = self.dist(l_mouth, r_mouth)
        h_mouth = self.dist(top_lip, bot_lip)
        mar = h_mouth / w_mouth if w_mouth != 0 else 0
        if self.check(LM):
            state = 1
        else:
            state = 0
        return [mar, self.condition, state]

class TiltRightExpr(Expression):
#     [L_FACE, R_FACE]
    def check(self, LM):
        l_face = LM[self.landmarks[0]]
        r_face = LM[self.landmarks[1]]
        tilt = (l_face.y -r_face.y)*100
        state = (tilt > self.condition)
        return state

    def getValue(self, LM):
        l_face = LM[self.landmarks[0]]
        r_face = LM[self.landmarks[1]]
        tilt = (l_face.y -r_face.y)*100
        if self.check(LM):
            state = 10
        else:
            state = 0
        return [tilt, self.condition, state]

class TiltLeftExpr(Expression):
#     [L_FACE, R_FACE]
    def check(self, LM):
        l_face = LM[self.landmarks[0]]
        r_face = LM[self.landmarks[1]]
        tilt = (l_face.y -r_face.y)*100
        state = (tilt < -self.condition)
        return state

    def getValue(self, LM):
        l_face = LM[self.landmarks[0]]
        r_face = LM[self.landmarks[1]]
        tilt = (l_face.y -r_face.y)*100
        if self.check(LM):
            state = 10
        else:
            state = 0
        return [tilt, -self.condition, state]

class kissExpr(Expression):
#     [L_MOUTH, R_MOUTH, L_FACE, R_FACE]
    def check(self, LM):
        l_mouth = LM[self.landmarks[0]]
        r_mouth = LM[self.landmarks[1]]
        l_face = LM[self.landmarks[2]]
        r_face = LM[self.landmarks[3]]
        w_face = self.dist(l_face, r_face)
        w_mouth = self.dist(l_mouth, r_mouth)
        state =  (w_mouth < (w_face * self.condition))
        return state

    def getValue(self, LM):
        l_mouth = LM[self.landmarks[0]]
        r_mouth = LM[self.landmarks[1]]
        l_face = LM[self.landmarks[2]]
        r_face = LM[self.landmarks[3]]
        w_face = self.dist(l_face, r_face)
        w_mouth = self.dist(l_mouth, r_mouth)
        if self.check(LM):
            state = 0.1
        else:
            state = 0
        return [w_mouth, (w_face * self.condition), state]

class tongueRightExpr(Expression):
#     [NOSE, L_MOUTH, R_MOUTH, L_FACE, R_FACE]
    def check(self, LM):
        nose = LM[self.landmarks[0]]
        l_mouth = LM[self.landmarks[1]]
        r_mouth = LM[self.landmarks[2]]
        l_face = LM[self.landmarks[3]]
        r_face = LM[self.landmarks[4]]
        mouth_center_x = (l_mouth.x + r_mouth.x) / 2
        w_face = self.dist(l_face, r_face)
        tongue_shift = (mouth_center_x - nose.x) / w_face
        state = (tongue_shift > self.condition)
        return state

    def getValue(self, LM):
        nose = LM[self.landmarks[0]]
        l_mouth = LM[self.landmarks[1]]
        r_mouth = LM[self.landmarks[2]]
        l_face = LM[self.landmarks[3]]
        r_face = LM[self.landmarks[4]]
        mouth_center_x = (l_mouth.x + r_mouth.x) / 2
        w_face = self.dist(l_face, r_face)
        tongue_shift = (mouth_center_x - nose.x) / w_face
        if self.check(LM):
            state = 0.1
        else:
            state = 0
        return [tongue_shift, self.condition, state]

class tongueLeftExpr(Expression):
#     [NOSE, TOP_LIP, BOTTOM_LIP, L_FACE, R_FACE]
    def check(self, LM):
        nose = LM[self.landmarks[0]]
        l_mouth = LM[self.landmarks[1]]
        r_mouth = LM[self.landmarks[2]]
        l_face = LM[self.landmarks[3]]
        r_face = LM[self.landmarks[4]]
        mouth_center_x = (l_mouth.x + r_mouth.x) / 2
        w_face = self.dist(l_face, r_face)
        w_mouth = self.dist(l_mouth, r_mouth)
        tongue_shift = (mouth_center_x - nose.x) / w_face
        state = (tongue_shift < -self.condition)
        return state

    def getValue(self, LM):
        nose = LM[self.landmarks[0]]
        l_mouth = LM[self.landmarks[1]]
        r_mouth = LM[self.landmarks[2]]
        l_face = LM[self.landmarks[3]]
        r_face = LM[self.landmarks[4]]
        mouth_center_x = (l_mouth.x + r_mouth.x) / 2
        w_face = self.dist(l_face, r_face)
        w_mouth = self.dist(l_mouth, r_mouth)
        tongue_shift = (mouth_center_x - nose.x) / w_face
        if self.check(LM):
            state = 0.1
        else:
            state = 0
        return [tongue_shift, -self.condition, state]

class puffLeftExpr(Expression):
#     [NOSE, L_PUFF]
    def check(self, LM):
        nose = LM[self.landmarks[0]]
        l_puff = LM[self.landmarks[1]]
        w_puff = self.dist(nose, l_puff)
        state = (w_puff > self.condition)
        return state

    def getValue(self, LM):
        nose = LM[self.landmarks[0]]
        l_puff = LM[self.landmarks[1]]
        w_puff = self.dist(nose, l_puff)
        if self.check(LM):
            state = 1
        else:
            state = 0
        return [ w_puff, self.condition, state]

class puffRightExpr(Expression):
#     [NOSE, R_PUFF]
    def check(self, LM):
        nose = LM[self.landmarks[0]]
        r_puff = LM[self.landmarks[1]]
        w_puff = self.dist(nose, r_puff)
        state = (w_puff > self.condition)
        return state

    def getValue(self, LM):
        nose = LM[self.landmarks[0]]
        l_puff = LM[self.landmarks[1]]
        w_puff = self.dist(nose, l_puff)
        if self.check(LM):
            state = 1
        else:
            state = 0
        return [ w_puff, self.condition, state]

classes = {
    'NEUTRAL' : Expression,
    'SMILE' : smileExpr,
    'MOUTH_OPEN' : mouthOpenExpr,
    'KISS' : kissExpr,
    'TILT_RIGHT' : TiltRightExpr,
    'TILT_LEFT' : TiltLeftExpr,
    'TONGUE_RIGHT' : tongueRightExpr,
    'TONGUE_LEFT' : tongueLeftExpr,
    'PUFF_LEFT' : puffLeftExpr,
    'PUFF_RIGHT' : puffRightExpr
}



