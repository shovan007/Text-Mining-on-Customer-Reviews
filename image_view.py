#-*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class ImageView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        self.update()

    def clear(self):
        self.image = None
        self.update()

    def paintEvent(self, event):
        p = QtGui.QPainter()
        p.begin(self)
        p.setBrush(QtGui.QBrush(QtCore.Qt.gray))
        p.drawRect(self.rect())
        if self.image is not None:
            p.drawImage(self.rect(), self.image)
        p.end()
