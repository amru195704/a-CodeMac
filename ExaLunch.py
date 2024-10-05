#!/usr/bin/env python


from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)
import subprocess
import os

class Dialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(Dialog, self).__init__()

        self.createMenu()
        self.createVirticalGroupBox()

        #bigEditor = QTextEdit()
        bigEditor = QLabel("東洋紡のCATV調査用の各機能を起動します。")
        #bigEditor.setPlainText("東洋紡のCATV調査用の各機能を起動します。")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.virticalGroupBox)
        mainLayout.addWidget(bigEditor)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("東洋紡CATVデータ調査")

    def createMenu(self):
        self.menuBar = QMenuBar()

        self.fileMenu = QMenu("&File", self)
        self.exitAction = self.fileMenu.addAction("E&xit")
        self.menuBar.addMenu(self.fileMenu)

        self.exitAction.triggered.connect(self.accept)

    def createVirticalGroupBox(self):
        self.virticalGroupBox = QGroupBox("調査機能選択")
        layout = QVBoxLayout()
        #
        btnDxfSummary = QPushButton("DXF概要調査")
        layout.addWidget(btnDxfSummary)
        btnDxfSummary.clicked.connect(self.dxfSummary)
        #
        btnDxfLayer = QPushButton("--DXFレイヤー調査")
        layout.addWidget(btnDxfLayer)
        btnDxfLayer.clicked.connect(self.dxfLayer)
        #
        btnDxfSymbol = QPushButton("--DXFシンボル調査")
        layout.addWidget(btnDxfSymbol)
        btnDxfSymbol.clicked.connect(self.dxfSymbol)
        #
        self.virticalGroupBox.setLayout(layout)

    def dxfSummary(self):
        print("dxfSummary")
        rtn = subprocess.Popen(['python', 'exaUtil/dxfSummary.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"rtn={rtn}")

    def dxfLayer(self):
        print("dxfLayer")

    def dxfSymbol(self):
        print("dxfSymbol")

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
