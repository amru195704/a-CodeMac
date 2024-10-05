from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget,  QFileDialog,  QGraphicsView, \
    QGraphicsScene, QHBoxLayout, QGroupBox, QPushButton, QVBoxLayout,QLabel
from PyQt5 import QtGui

import sys
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # canvas
        self.canvas = PngCanvas()
        # canvasをMainWindowにセット
        self.setCentralWidget(self.canvas)

        #self.setGeometry(300, 300, 640, 640)
        self.setFixedSize(1024, 800)


class PngCanvas(QWidget):
    #CWIDTH = 980
    #CHEIGHT = 700
    def __init__(self):
        super(PngCanvas, self).__init__()

        # canvasのレイアウト
        self.canvas_layout = QVBoxLayout()

        #

        # 画像を表示するためのviewをレイアウトにセット
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        #
        self.createHGroupBox()
        self.canvas_layout.addWidget(self.buttonGroupBox)
        self.canvas_layout.addWidget(self.view)

        # canvas_layoutをQWidget(self)にセット
        self.setLayout(self.canvas_layout)
        #self.resize(self.CWIDTH, self.CHEIGHT)
        #
        self.VWIDTH = self.view.width()
        self.VHEIGHT = self.view.height()

    def createHGroupBox(self):
        self.buttonGroupBox = QGroupBox("PNG選択")
        #
        layoutCnt = QHBoxLayout()
        self.cntLabel = QLabel("0")
        layoutCnt.addWidget(self.cntLabel)
        #
        layoutBtn = QHBoxLayout()
        #
        btnOpenPng = QPushButton("PNGを開く")
        layoutBtn.addWidget(btnOpenPng)
        btnOpenPng.clicked.connect(self.pngOpenFile)
        #
        btnFit = QPushButton("全体表示")
        layoutBtn.addWidget(btnFit)
        btnFit.clicked.connect(self.pngFit)
        #
        btnOrg = QPushButton("オリジナル")
        layoutBtn.addWidget(btnOrg)
        btnOrg.clicked.connect(self.pngOrg)
        #
        btnDec = QPushButton("<-")
        layoutBtn.addWidget(btnDec)
        btnDec.clicked.connect(self.pngDec)
        #
        btnInc = QPushButton("->")
        layoutBtn.addWidget(btnInc)
        btnInc.clicked.connect(self.pngInc)
        #
        layout = QVBoxLayout()
        layout.addLayout(layoutCnt)
        layout.addLayout(layoutBtn)
        #
        self.buttonGroupBox.setLayout(layout)

    # --- button
    def pngFit(self):
        print("btnFit")
        self.pixmap = self.fitImage(self.orgPixmap)
        # pixmapをsceneに追加
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        # ウィジェットを更新
        self.update()
        #
        magx = float(self.view.width() - 20) / self.pixmap.width()
        magy = float(self.view.height() - 20) / self.pixmap.height()
        if magx < 1.0:
            if magx < magy:
                mag = magy
            else:
                mag = magx
        else:
            if magx < magy:
                mag = magx
            else:
                mag = magy
        #
        sw = int(self.view.width() * mag)
        sh = int(self.view.height() * mag)
        self.view.resize(sw, sh)
            
    def pngOrg(self):
        print("btnOrg")
        self.pixmap = self.orgPixmap
        # pixmapをsceneに追加
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        # ウィジェットを更新
        self.update()
        #
    
    def xxx():
        magx = float(self.view.width() - 20) / self.pixmap.width()
        magy = float(self.view.height() - 20) / self.pixmap.height()
        if magx < 1.0:
            if magx < magy:
                mag = magy
            else:
                mag = magx
        else:
            if magx < magy:
                mag = magx
            else:
                mag = magy
        #
        dw = self.width() - self.view.width()
        dh = self.height() - self.view.height()
        #
        sw = self.view.width() * mag
        sh = self.view.height() * mag
        if dw < self.CWIDTH:
            #self.resize(self.CWIDTH, self.CHEIGHT)
            self.view.resize(self.VWIDTH, self.VHEIGHT)
        #elif dw > (self.CWIDTH*2):
        #    self.resize(self.CWIDTH*2, self.CHEIGHT*2)
        #else:
        #    self.resize(sw+dw, sh+dh)

    def pngOpenFile(self):
        self.filepath = QFileDialog.getOpenFileName(self, 'open file', '', 'Images (*.png)')[0]
        if self.filepath:
            if self.setImage(self.filepath):
                self.pngFit()

    def setImage(self, filepath):
        img = QtGui.QImage()

        # 画像ファイルの読み込み
        if not img.load(filepath):
            return False

        # sceneの初期化
        self.scene.clear()

        # QImage -> QPixmap
        self.orgPixmap = QtGui.QPixmap.fromImage(img)

        return True

    #---------------------------------
    #   pixmap zoom
    def fitImage(self,imPixmap):
        self.setFixedSize(1024, 800)
        #
        magx = float(self.view.width() - 20) / imPixmap.width()
        magy = float(self.view.height() -20) / imPixmap.height()
        if magx < 1.0:
            if magx < magy:
                mag = magx
            else:
                mag = magy
        else:
            if magx < magy:
                mag = magy
            else:
                mag = magx
        sw = imPixmap.width() * mag
        sh = imPixmap.height() * mag
        outPixmap = imPixmap.scaled(int(sw),int(sh))
        return outPixmap

    #---------------------------------
    #   -1 png 移動
    def pngDec(self):
        print("btnDec")
        #
        self.currentRow -= 1
        if self.currentRow < 0:
            self.currentRow = 0
        #
        fileName = self.resultTable.item( self.currentRow, 1)
        # cnt = self.folderTable.item(row, 2)
        pngFile = f"{self.gSearchFld}/{fileName.text()}"
        if self.setImage(pngFile):
            self.pngFit()
            self.setCntLabel()

    #---------------------------------
    #   +1 png 移動
    def pngInc(self):
        print("btnInc")
        #
        self.currentRow += 1
        if self.currentRow >= self.resultTable.rowCount():
            self.currentRow = self.resultTable.rowCount() - 1
        #
        fileName = self.resultTable.item( self.currentRow, 1)
        # cnt = self.folderTable.item(row, 2)
        pngFile = f"{self.gSearchFld}/{fileName.text()}"
        if self.setImage(pngFile):
            self.pngFit()
            self.setCntLabel()

    def setCntLabel(self):
        cntStr = f"{self.currentRow+1}/{self.resultTable.rowCount()}"
        self.cntLabel.setText(str(cntStr))
    #---------------------
    # 外部コマンド
    def viewImageFile(self, resultTable0,row0,gSearchFld0):
        #
        self.resultTable = resultTable0
        self.currentRow = row0
        self.gSearchFld = gSearchFld0
        #
        fileName = self.resultTable.item( self.currentRow, 1)
        # cnt = self.folderTable.item(row, 2)
        pngFile = f"{self.gSearchFld}/{fileName.text()}"
        if self.setImage(pngFile):
            self.pngFit()
            self.setCntLabel()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #win = MainWindow()
    win = PngCanvas()
    win.show()
    sys.exit(app.exec_())
