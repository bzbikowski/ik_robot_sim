import OpenGL.GL as gl
from object_load import ModelLoader
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt, QTimer
from PyQt5.QtGui import QColor
import numpy as np
import math
import scipy.optimize


class GLWidget(QOpenGLWidget):
    positionChanged = pyqtSignal(float, float, float)
    rotationChanged = pyqtSignal(float, float, float)
    errorDetected = pyqtSignal(str)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.timer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.animateFigures)
        self.timer.start()
        # parameters of the robot (square base)
        # length of arms of the robot
        self.fl = 0.4
        self.sl = 0.3
        self.tl = 0.3
        # width of arms of the robot
        self.width = 0.1
        # distance from each joint to end edge of the robot
        self.free_dist = 0.05
        # 0 - rotation, 1 - position
        self.mode = 0

        self.x = 0
        self.y = 0
        self.z = 0.9

        self.xTarget = 0
        self.yTarget = 0
        self.zTarget = 0.9

        self.xRot = 60*16
        self.yRot = 0*16
        self.zRot = 0*16
        self.cameraDepth = 0.7
        self.cameraTransX = 0.0
        self.cameraTransY = 0.2

        self.curFirstRotate = 0.0
        self.curSecondRotate = 0.0
        self.curThirdRotate = 0.0

        self.targetFirstRotate = 0.0
        self.targetSecondRotate = 0.0
        self.targetThirdRotate = 0.0

        self.precision = 1e-2

        self.model = ModelLoader("models//sphere//point.obj")

        self.lastPos = QPoint()

        self.colorRed = QColor.fromRgbF(1.0, 0.0, 0.0, 0.0)
        self.colorBlue = QColor.fromRgbF(0.0, 0.0, 1.0, 0.0)
        self.colorGreen2 = QColor.fromRgbF(0.0, 1.0, 0.0, 0.0)
        self.colorGreen = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.colorPurple = QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
        self.colorGray = QColor.fromCmykF(0.5, 0.5, 0.5, 0.5)

        self.setMinimumSize(500, 500)

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def setArmRotation(self, f, s, t):
        fp, sp, tp = map(lambda x: x/180*math.pi, [f, s, t])
        _, _, z = self.calculate_fk([fp, sp, tp])
        if z < 0:
            self.errorDetected.emit("Nie dopuszczalna pozycja ramienia robota. ")
            return
        self.mode = 0
        self.targetFirstRotate = f
        self.targetSecondRotate = s
        self.targetThirdRotate = t

    def setPosition(self, x, y, z):
        if z < 0:
            self.errorDetected.emit("Nie dopuszczalna pozycja ramienia robota. ")
            return
        self.mode = 1
        self.xTarget = x
        self.yTarget = y
        self.zTarget = z

    def animateFigures(self):
        if self.mode == 0:
            if not (self.targetFirstRotate == self.curFirstRotate and self.targetSecondRotate == self.curSecondRotate
                    and self.targetThirdRotate == self.curThirdRotate):
                subs = self.targetFirstRotate - self.curFirstRotate
                if math.fabs(subs) <= 1.0:
                    self.curFirstRotate = self.targetFirstRotate
                else:
                    if subs >= 180.0:
                        subs -= 360
                    if subs <= -180.0:
                        subs += 360
                    if subs < 0.0:
                        self.curFirstRotate -= 1.0
                    else:
                        self.curFirstRotate += 1.0
                self.curFirstRotate = self.normalizeJointAngle(self.curFirstRotate)

                subs = self.targetSecondRotate - self.curSecondRotate
                if math.fabs(subs) <= 1.0:
                    self.curSecondRotate = self.targetSecondRotate
                else:
                    if subs >= 180.0:
                        subs -= 360
                    if subs <= -180.0:
                        subs += 360
                    if subs < 0.0:
                        self.curSecondRotate -= 1.0
                    else:
                        self.curSecondRotate += 1.0
                self.curSecondRotate = self.normalizeJointAngle(self.curSecondRotate)

                subs = self.targetThirdRotate - self.curThirdRotate
                if math.fabs(subs) <= 1.0:
                    self.curThirdRotate = self.targetThirdRotate
                else:
                    if subs >= 180.0:
                        subs -= 360
                    if subs <= -180.0:
                        subs += 360
                    if subs < 0.0:
                        self.curThirdRotate -= 1.0
                    else:
                        self.curThirdRotate += 1.0
                self.curThirdRotate = self.normalizeJointAngle(self.curThirdRotate)
                self.calculate_fk()
        elif self.mode == 1:
            result = self.calculate_ik()
            if result.success:
                if result.fun <= self.precision:
                    result = result.x
                else:
                    self.errorDetected.emit("Podany punkt nie jest osiagalny przez robota. ")
                    self.mode = -1
                    return
            else:
                print(result.status, result.message)
                self.mode = -1
                return
            result = list(map(lambda x: x * 180 / math.pi, result))
            self.targetFirstRotate = self.normalizeJointAngle(result[0])
            self.targetSecondRotate = self.normalizeJointAngle(result[1])
            self.targetThirdRotate = self.normalizeJointAngle(result[2])
            self.mode = 2
        elif self.mode == 2:
            if not (self.targetFirstRotate == self.curFirstRotate and self.targetSecondRotate == self.curSecondRotate
                    and self.targetThirdRotate == self.curThirdRotate):
                subs = self.targetFirstRotate - self.curFirstRotate
                if math.fabs(subs) <= 1.0:
                    self.curFirstRotate = self.targetFirstRotate
                else:
                    if subs >= 180.0:
                        subs -= 360
                    if subs <= -180.0:
                        subs += 360
                    if subs < 0.0:
                        self.curFirstRotate -= 1.0
                    else:
                        self.curFirstRotate += 1.0
                self.curFirstRotate = self.normalizeJointAngle(self.curFirstRotate)

                subs = self.targetSecondRotate - self.curSecondRotate
                if math.fabs(subs) <= 1.0:
                    self.curSecondRotate = self.targetSecondRotate
                else:
                    if subs >= 180.0:
                        subs -= 360
                    if subs <= -180.0:
                        subs += 360
                    if subs < 0.0:
                        self.curSecondRotate -= 1.0
                    else:
                        self.curSecondRotate += 1.0
                self.curSecondRotate = self.normalizeJointAngle(self.curSecondRotate)

                subs = self.targetThirdRotate - self.curThirdRotate
                if math.fabs(subs) <= 1.0:
                    self.curThirdRotate = self.targetThirdRotate
                else:
                    if subs >= 180.0:
                        subs -= 360
                    if subs <= -180.0:
                        subs += 360
                    if subs < 0.0:
                        self.curThirdRotate -= 1.0
                    else:
                        self.curThirdRotate += 1.0
                self.curThirdRotate = self.normalizeJointAngle(self.curThirdRotate)
                self.rotationChanged.emit(self.curFirstRotate, self.curSecondRotate, self.curThirdRotate)
        self.update()

    def setXRotation(self, angle):
        angle = self.normalizeCameraAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeCameraAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeCameraAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.update()

    def setCameraDepth(self, dist):
        self.cameraDepth = dist
        self.update()
        
    def update(self):
        super(GLWidget, self).update()

    def calculate_fk(self, rot=None):
        if rot is None:
            x = math.sin(self.curFirstRotate*math.pi/180.0)*(self.tl * math.sin((self.curThirdRotate+self.curSecondRotate)*math.pi/180.0) +
                                                             (self.sl - self.free_dist) * math.sin(self.curSecondRotate*math.pi/180.0))
            y = math.cos(self.curFirstRotate*math.pi/180.0)*(self.tl * math.sin((self.curThirdRotate+self.curSecondRotate)*math.pi/180.0) +
                                                             (self.sl - self.free_dist) * math.sin(self.curSecondRotate*math.pi/180.0))
            z = (self.fl - self.free_dist) + self.tl * math.cos((self.curThirdRotate+self.curSecondRotate)*math.pi/180.0) + \
                (self.sl - self.free_dist) * math.cos(self.curSecondRotate*math.pi/180.0)
            self.x = x
            self.y = y
            self.z = z
            self.positionChanged.emit(x, y, z)
        else:
            x = math.sin(rot[0])*(self.tl * math.sin(rot[2]+rot[1]) + (self.sl - self.free_dist) * math.sin(rot[1]))
            y = math.cos(rot[0])*(self.tl * math.sin(rot[2]+rot[1]) + (self.sl - self.free_dist) * math.sin(rot[1]))
            z = (self.fl - self.free_dist) + self.tl * math.cos(rot[2]+rot[1]) + (self.sl - self.free_dist) * math.cos(rot[1])
            return [x, y, z]

    def calculate_ik(self):
        """
        Find alpha,beta,gamma that move arm to given coords
        """
        def fun(rot):
            cur = self.calculate_fk(rot)
            tar = [self.xTarget, self.yTarget, self.zTarget]
            return np.sqrt(np.sum([(c - t)**2
                           for c, t in zip(cur, tar)]))

        def x_constraint(rot):
            cur = self.calculate_fk(rot)
            tar = [self.xTarget, self.yTarget, self.zTarget]
            x = cur[0] - tar[0]
            return x

        def y_constraint(rot):
            cur = self.calculate_fk(rot)
            tar = [self.xTarget, self.yTarget, self.zTarget]
            y = cur[1] - tar[1]
            return y

        def z_constraint(rot):
            cur = self.calculate_fk(rot)
            tar = [self.xTarget, self.yTarget, self.zTarget]
            z = cur[2] - tar[2]
            return z

        cur = [self.curFirstRotate, self.curSecondRotate, self.curThirdRotate]
        tar = [self.xTarget, self.yTarget, self.zTarget]
        cons = ({'type': 'eq',
                 'fun': lambda x: x_constraint(x)},
                {'type': 'eq',
                 'fun': lambda x: y_constraint(x)},
                {'type': 'eq',
                 'fun': lambda x: z_constraint(x)})
        # noinspection PyTypeChecker
        return scipy.optimize.minimize(
            fun=fun,
            x0=cur,
            method='Nelder-Mead',
            options={})

    def initializeGL(self):
        self.setClearColor(self.colorPurple.darker())
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslated(0.0, 0.0, -10.0)
        gl.glScaled(self.cameraDepth, self.cameraDepth, self.cameraDepth)
        gl.glTranslated(self.cameraTransX, self.cameraTransY, 0)
        gl.glPushMatrix()
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        gl.glCallList(self.makeBase())
        gl.glCallList(self.makeAxis())
        gl.glPushMatrix()
        gl.glRotated(self.curFirstRotate, 0.0, 0.0, 1.0)
        gl.glRotated(90.0, 1.0, 0.0, 0.0)
        gl.glCallList(self.makeArm(-(self.width/2), self.width/2, 0, self.fl, -(self.width/2), self.width/2))
        gl.glPushMatrix()
        gl.glTranslated(self.width, self.fl - self.free_dist, 0.0)
        gl.glRotated(self.curSecondRotate, 1.0, 0.0, 0.0)
        gl.glCallList(self.makeArm(-(self.width/2), self.width/2, 0, self.sl, -(self.width/2), self.width/2))
        gl.glPushMatrix()
        gl.glTranslated(-self.width, self.sl - self.free_dist, 0.0)
        gl.glRotated(self.curThirdRotate, 1.0, 0.0, 0.0)
        gl.glCallList(self.makeArm(-(self.width/2), self.width/2, 0, self.tl, -(self.width/2), self.width/2))
        gl.glPushMatrix()
        gl.glTranslated(0, self.tl+0.0175, 0)
        gl.glCallList(self.model.paint())
        gl.glPopMatrix()
        gl.glPopMatrix()
        gl.glPopMatrix()
        gl.glPopMatrix()
        gl.glPopMatrix()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                           side)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)
        elif event.buttons() & Qt.MiddleButton:
            self.setTranslation(dx / 100.0, dy / 100.0)

        self.lastPos = event.pos()

    def wheelEvent(self, event):
        super(GLWidget, self).wheelEvent(event)
        numStep = event.angleDelta().y() / 120
        newCamera = self.cameraDepth + numStep*0.02
        if newCamera <= 0.1:
            newCamera = 0.1
        self.setCameraDepth(newCamera)

    def makeBase(self):
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        self.setColor(self.colorGray)

        gl.glVertex3d(-1, -1, 0)
        gl.glVertex3d(-1, 1, 0)
        gl.glVertex3d(1, 1, 0)
        gl.glVertex3d(1, -1, 0)

        gl.glEnd()
        gl.glEndList()

        return genList

    def makeArm(self, x1, x2, y1, y2, z1, z2):
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        self.make_figure(x1, x2, y1, y2, z1, z2)

        gl.glEnd()
        gl.glEndList()

        return genList

    def makeAxis(self):
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)
        gl.glBegin(gl.GL_LINES)
        self.setColor(self.colorGreen2)
        gl.glVertex3d(0, 0, -10)
        gl.glVertex3d(0, 0, 10)
        gl.glEnd()
        self.make_labels(2)
        gl.glBegin(gl.GL_LINES)
        self.setColor(self.colorBlue)
        gl.glVertex3d(0, -10, 0.01)
        gl.glVertex3d(0, 10, 0.01)
        gl.glEnd()
        self.make_labels(1)
        gl.glBegin(gl.GL_LINES)
        self.setColor(self.colorRed)
        gl.glVertex3d(-10, 0, 0.01)
        gl.glVertex3d(10, 0, 0.01)
        gl.glEnd()
        self.make_labels(0)
        gl.glEndList()

        return genList

    def make_labels(self, axis):
        if axis == 0:
            self.setColor(self.colorRed)
            for x in np.linspace(-1.0, 1.0, 21):
                gl.glBegin(gl.GL_LINES)
                gl.glVertex3d(x, -0.03, 0.01)
                gl.glVertex3d(x, 0.03, 0.01)
                gl.glEnd()
        elif axis == 1:
            self.setColor(self.colorBlue)
            for x in np.linspace(-1.0, 1.0, 21):
                gl.glBegin(gl.GL_LINES)
                gl.glVertex3d(-0.03, x, 0.01)
                gl.glVertex3d(0.03, x, 0.01)
                gl.glEnd()
        elif axis == 2:
            self.setColor(self.colorGreen)
            for x in np.linspace(0.0, 1.0, 11):
                gl.glBegin(gl.GL_LINES)
                gl.glVertex3d(-0.03, 0.0, x)
                gl.glVertex3d(0.03, 0.0, x)
                gl.glEnd()

    def make_figure(self, x1, x2, y1, y2, z1, z2):
        self.quad(x1, x2, y1, y2, z1, z2)

        self.extrude_x(x1, x2, y1, y2, z1, z2)

        self.extrude_y(x1, x2, y1, y2, z1, z2)

    def quad(self, x1, x2, y1, y2, z1, z2):
        self.setColor(self.colorGreen)

        gl.glVertex3d(x2, y1, z1)
        gl.glVertex3d(x2, y2, z1)
        gl.glVertex3d(x1, y2, z1)
        gl.glVertex3d(x1, y1, z1)

        gl.glVertex3d(x1, y1, z2)
        gl.glVertex3d(x1, y2, z2)
        gl.glVertex3d(x2, y2, z2)
        gl.glVertex3d(x2, y1, z2)

    def extrude_x(self, x1, x2, y1, y2, z1, z2):
        self.setColor(self.colorGreen.darker(250 + int(100 * x1)))

        gl.glVertex3d(x1, y1, z1)
        gl.glVertex3d(x1, y2, z1)
        gl.glVertex3d(x1, y2, z2)
        gl.glVertex3d(x1, y1, z2)

        self.setColor(self.colorGreen.darker(250 + int(100 * x2)))

        gl.glVertex3d(x2, y1, z2)
        gl.glVertex3d(x2, y2, z2)
        gl.glVertex3d(x2, y2, z1)
        gl.glVertex3d(x2, y1, z1)

    def extrude_y(self, x1, x2, y1, y2, z1, z2):
        self.setColor(self.colorGreen.darker(250 + int(100 * y1)))

        gl.glVertex3d(x1, y1, z1)
        gl.glVertex3d(x1, y1, z2)
        gl.glVertex3d(x2, y1, z2)
        gl.glVertex3d(x2, y1, z1)

        self.setColor(self.colorGreen.darker(250 + int(100 * y2)))

        gl.glVertex3d(x2, y2, z1)
        gl.glVertex3d(x2, y2, z2)
        gl.glVertex3d(x1, y2, z2)
        gl.glVertex3d(x1, y2, z1)

    def normalizeCameraAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def normalizeJointAngle(self, angle):
        while angle < 0:
            angle += 360
        while angle > 360:
            angle -= 360
        return angle

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setTranslation(self, alpha, beta):
        self.cameraTransX += alpha * self.cameraDepth
        self.cameraTransY += beta * self.cameraDepth

    def setDefaultCamera(self):
        self.xRot = 60*16
        self.yRot = 0*16
        self.zRot = 0*16
        self.cameraDepth = 0.7
        self.cameraTransX = 0.0
        self.cameraTransY = 0.2
