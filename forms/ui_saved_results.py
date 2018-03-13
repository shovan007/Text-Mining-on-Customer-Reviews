# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms\saved_results.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SavedResults(object):
    def setupUi(self, SavedResults):
        SavedResults.setObjectName("SavedResults")
        SavedResults.resize(692, 415)
        self.verticalLayout = QtWidgets.QVBoxLayout(SavedResults)
        self.verticalLayout.setObjectName("verticalLayout")
        self.results = QtWidgets.QTreeWidget(SavedResults)
        self.results.setObjectName("results")
        self.verticalLayout.addWidget(self.results)
        self.buttonBox = QtWidgets.QDialogButtonBox(SavedResults)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SavedResults)
        self.buttonBox.accepted.connect(SavedResults.accept)
        self.buttonBox.rejected.connect(SavedResults.reject)
        QtCore.QMetaObject.connectSlotsByName(SavedResults)

    def retranslateUi(self, SavedResults):
        _translate = QtCore.QCoreApplication.translate
        SavedResults.setWindowTitle(_translate("SavedResults", "Saved results"))
        self.results.headerItem().setText(0, _translate("SavedResults", "Saved at"))
        self.results.headerItem().setText(1, _translate("SavedResults", "Price"))
        self.results.headerItem().setText(2, _translate("SavedResults", "Product"))
        self.results.headerItem().setText(3, _translate("SavedResults", "Brand"))

