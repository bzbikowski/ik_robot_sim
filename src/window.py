from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QMainWindow, QAction, QVBoxLayout, QPushButton,\
    QLineEdit, QLabel, QMessageBox
from src.gl import GLWidget
from src.settings import AngleValidator


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setup_menubar()
        self.ui = KsaGui()
        self.setCentralWidget(self.ui)

        self.setWindowTitle("Komputerowe systemy automatyki - project")

    def setup_menubar(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        optionMenu = mainMenu.addMenu('Options')
        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)
        cameraButton = QAction('Restore default camera', self)
        cameraButton.setShortcut('Ctrl+R')
        cameraButton.setStatusTip('Restore camera to default position')
        cameraButton.triggered.connect(self.restore_camera)
        optionMenu.addAction(cameraButton)

    def restore_camera(self):
        self.ui.glwidget.setDefaultCamera()


class KsaGui(QWidget):
    def __init__(self):
        super(KsaGui, self).__init__()
        self.mainLayout = QHBoxLayout(self)
        self.glwidget = GLWidget()
        self.guiLayout = QVBoxLayout()

        self.armLayout = QVBoxLayout()
        self.firstArmLayout = QHBoxLayout()
        self.subbFirstArm = QPushButton("<")
        self.subbFirstArm.clicked.connect(self.subbFirstEvent)
        self.angleValidator = AngleValidator()
        self.displayFirstArm = QLineEdit("0.0")
        self.displayFirstArm.setValidator(self.angleValidator)
        self.displayFirstArm.returnPressed.connect(self.refreshAngleGL)
        self.addFirstArm = QPushButton(">")
        self.addFirstArm.clicked.connect(self.addFirstEvent)
        self.firstArmLayout.addWidget(self.subbFirstArm)
        self.firstArmLayout.addWidget(self.displayFirstArm)
        self.firstArmLayout.addWidget(self.addFirstArm)
        self.armLayout.addLayout(self.firstArmLayout)

        self.secondArmLayout = QHBoxLayout()
        self.subbSecondArm = QPushButton("<")
        self.subbSecondArm.clicked.connect(self.subbSecondEvent)
        self.displaySecondArm = QLineEdit("0.0")
        self.displaySecondArm.setValidator(self.angleValidator)
        self.displaySecondArm.returnPressed.connect(self.refreshAngleGL)
        self.addSecondArm = QPushButton(">")
        self.addSecondArm.clicked.connect(self.addSecondEvent)
        self.secondArmLayout.addWidget(self.subbSecondArm)
        self.secondArmLayout.addWidget(self.displaySecondArm)
        self.secondArmLayout.addWidget(self.addSecondArm)
        self.armLayout.addLayout(self.secondArmLayout)

        self.thirdArmLayout = QHBoxLayout()
        self.subbThirdArm = QPushButton("<")
        self.subbThirdArm.clicked.connect(self.subbThirdEvent)
        self.displayThirdArm = QLineEdit("0.0")
        self.displayThirdArm.setValidator(self.angleValidator)
        self.displayThirdArm.returnPressed.connect(self.refreshAngleGL)
        self.addThirdArm = QPushButton(">")
        self.addThirdArm.clicked.connect(self.addThirdEvent)
        self.thirdArmLayout.addWidget(self.subbThirdArm)
        self.thirdArmLayout.addWidget(self.displayThirdArm)
        self.thirdArmLayout.addWidget(self.addThirdArm)
        self.armLayout.addLayout(self.thirdArmLayout)

        self.animateButton = QPushButton("Animate")
        self.animateButton.clicked.connect(self.refreshAngleGL)
        self.armLayout.addWidget(self.animateButton)
        self.guiLayout.addLayout(self.armLayout)

        self.coordLayout = QVBoxLayout()
        self.posValidator = QRegExpValidator(QRegExp("^\-?\d*\.?\d*(e\-?\d*)?$"))
        self.xLayout = QHBoxLayout()
        self.xLabel = QLabel("X coord: ")
        self.xDisplay = QLineEdit("0.0")
        self.xDisplay.returnPressed.connect(self.refreshPositionGL)
        self.xDisplay.setValidator(self.posValidator)
        self.xLayout.addWidget(self.xLabel)
        self.xLayout.addWidget(self.xDisplay)
        self.coordLayout.addLayout(self.xLayout)

        self.yLayout = QHBoxLayout()
        self.yLabel = QLabel("Y coord: ")
        self.yDisplay = QLineEdit("0.0")
        self.yDisplay.returnPressed.connect(self.refreshPositionGL)
        self.yDisplay.setValidator(self.posValidator)
        self.yLayout.addWidget(self.yLabel)
        self.yLayout.addWidget(self.yDisplay)
        self.coordLayout.addLayout(self.yLayout)

        self.zLayout = QHBoxLayout()
        self.zLabel = QLabel("Z coord: ")
        self.zDisplay = QLineEdit("0.9")
        self.zDisplay.returnPressed.connect(self.refreshPositionGL)
        self.zDisplay.setValidator(self.posValidator)
        self.zLayout.addWidget(self.zLabel)
        self.zLayout.addWidget(self.zDisplay)
        self.coordLayout.addLayout(self.zLayout)
        self.posButton = QPushButton("Animate")
        self.posButton.clicked.connect(self.refreshPositionGL)
        self.coordLayout.addWidget(self.posButton)
        self.guiLayout.addLayout(self.coordLayout)

        self.mainLayout.addWidget(self.glwidget)
        self.mainLayout.addLayout(self.guiLayout)

        self.glwidget.positionChanged.connect(self.updateGui)
        self.glwidget.rotationChanged.connect(self.updateAngle)
        self.glwidget.errorDetected.connect(self.rotationError)

    def subbFirstEvent(self):
        newRotate = float(self.displayFirstArm.text()) - 1.0
        if newRotate < 0.0:
            newRotate += 360.0
        self.displayFirstArm.setText(str(newRotate))
        self.refreshAngleGL()

    def addFirstEvent(self):
        rotate = float(self.displayFirstArm.text())
        newRotate = rotate + 1.0
        if newRotate >= 360.0:
            newRotate -= 360.0
        self.displayFirstArm.setText(str(newRotate))
        self.refreshAngleGL()

    def subbSecondEvent(self):
        rotate = float(self.displaySecondArm.text())
        newRotate = rotate - 1.0
        if newRotate < 0.0:
            newRotate += 360.0
        self.displaySecondArm.setText(str(newRotate))
        self.refreshAngleGL()

    def addSecondEvent(self):
        firstRotate = float(self.displaySecondArm.text())
        newRotate = firstRotate + 1.0
        if newRotate >= 360.0:
            newRotate -= 360.0
        self.displaySecondArm.setText(str(newRotate))
        self.refreshAngleGL()

    def subbThirdEvent(self):
        rotate = float(self.displayThirdArm.text())
        newRotate = rotate - 1.0
        if newRotate < 0.0:
            newRotate += 360.0
        self.displayThirdArm.setText(str(newRotate))
        self.refreshAngleGL()

    def addThirdEvent(self):
        firstRotate = float(self.displayThirdArm.text())
        newRotate = firstRotate + 1.0
        if newRotate >= 360.0:
            newRotate -= 360.0
        self.displayThirdArm.setText(str(newRotate))
        self.refreshAngleGL()

    def refreshAngleGL(self):
        first = float(self.displayFirstArm.text())
        second = float(self.displaySecondArm.text())
        third = float(self.displayThirdArm.text())
        self.glwidget.setArmRotation(first, second, third)

    def updateGui(self, x, y, z):
        self.xDisplay.setText(str(x))
        self.yDisplay.setText(str(y))
        self.zDisplay.setText(str(z))

    def refreshPositionGL(self):
        x = float(self.xDisplay.text())
        y = float(self.yDisplay.text())
        z = float(self.zDisplay.text())
        self.glwidget.setPosition(x, y, z)

    def updateAngle(self, alpha, beta, gamma):
        self.displayFirstArm.setText(str(alpha))
        self.displaySecondArm.setText(str(beta))
        self.displayThirdArm.setText(str(gamma))

    def rotationError(self, error):
        QMessageBox().critical(self, "Error", error, QMessageBox.Ok)
