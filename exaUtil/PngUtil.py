import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget,  QFileDialog,  QGraphicsView, \
    QGraphicsScene, QHBoxLayout, QGroupBox, QPushButton, QVBoxLayout,QLabel
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer

import sys
import os

# --------------------------
#  Mac で描画するために、必要
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # canvas
        self.canvas = PngCanvas()
        # canvasをMainWindowにセット
        self.setCentralWidget(self.canvas)
        self.setFixedSize(1024, 800)
        #
        self.zoomScale = 1.0

# --------------------------
# png表示用のcanvas作成
class PngCanvas(QWidget):
    def __init__(self):
        super(PngCanvas, self).__init__()

        # canvasのレイアウト
        self.canvas_layout = QVBoxLayout()
        #
        # 画像を表示するためのviewをレイアウトにセット
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        # バタン関連グループボックス
        self.createHGroupBox()
        self.canvas_layout.addWidget(self.buttonGroupBox)
        self.canvas_layout.addWidget(self.view)
        # canvas_layoutをQWidget(self)にセット
        self.setLayout(self.canvas_layout)
        #self.resize(self.CWIDTH, self.CHEIGHT)
        #
        self.VWIDTH = self.view.width()
        self.VHEIGHT = self.view.height()

    #-----------------------
    # ラベル・ボタンのグループボックス設定
    def createHGroupBox(self):
        self.buttonGroupBox = QGroupBox("PNG選択")
        #
        # --- １段目
        self.cntLabel = QLabel("0")
        self.pathLabel = QLabel("")
        # --- 2段目
        btnZoomIn = QPushButton("拡大")
        btnZoomIn.clicked.connect(self.zoomIn)
        btnZoomOut = QPushButton("縮小")
        btnZoomOut.clicked.connect(self.zoomOut)
        #
        btnAutoDec = QPushButton("<<")
        btnAutoDec.clicked.connect(self.autiDec)
        btnAutoStop = QPushButton("🔳")
        btnAutoStop.clicked.connect(self.autoStop)   
        btnAutoInc = QPushButton(">>")
        btnAutoInc.clicked.connect(self.autoInc)  
        # --- 自動再生用タイマー定義
        self.timer = QTimer(self)                     
        # --- 3段目
        btnOpenPng = QPushButton("PNGを開く")
        btnOpenPng.clicked.connect(self.pngOpenFile)
        #
        btnFit = QPushButton("全体表示")
        btnFit.clicked.connect(self.pngFit)
        #
        btnOrg = QPushButton("オリジナル")
        btnOrg.clicked.connect(self.pngOrg)
        #
        btnDec = QPushButton("<-")
        btnDec.clicked.connect(self.pngDec)
        #
        btnInc = QPushButton("->")
        btnInc.clicked.connect(self.pngInc)
        # --- 1段目レイアウト
        layoutCnt = QHBoxLayout()
        layoutCnt.addWidget(self.cntLabel)
        layoutCnt.addWidget(self.pathLabel)        
         # --- 2段目レイアウト     
        layoutFunc = QHBoxLayout()
        layoutFunc.addWidget(btnZoomIn)
        layoutFunc.addWidget(btnZoomOut)
        layoutFunc.addWidget(btnAutoDec)
        layoutFunc.addWidget(btnAutoStop)        
        layoutFunc.addWidget(btnAutoInc)
        # --- 3段目レイアウト
        layoutBtn = QHBoxLayout()
        layoutBtn.addWidget(btnOpenPng)
        layoutBtn.addWidget(btnFit)
        layoutBtn.addWidget(btnOrg)
        layoutBtn.addWidget(btnDec)
        layoutBtn.addWidget(btnInc)
        # ---- 全体レイアウト
        layout = QVBoxLayout()
        layout.addLayout(layoutCnt)
        layout.addLayout(layoutFunc)
        layout.addLayout(layoutBtn)
        #
        self.buttonGroupBox.setLayout(layout)

    # --- button
    #-----------------------
    # 画像全体fit表示
    def pngFit(self):
        print("btnFit")
        self.pixmap = self.fitImage(self.orgPixmap)
        # pixmapをsceneに追加
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        #
        self.zoomScale = 1.0
        self.viewZoom()
        # ウィジェットを更新
        self.update()

    #-----------------------
    # 画像拡大縮小
    def zoomIn(self):
        print("btnZoomIn")
        self.zoomScale *= 1.2
        self.viewZoom()

    def zoomOut(self):
        print("btnZoomIn")
        self.zoomScale *= 0.8
        self.viewZoom()

    #-----------------------
    # 画像fit/zoom共通処理
    def viewZoom(self):
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
        sw = int(self.view.width() * mag*self.zoomScale)
        sh = int(self.view.height() * mag*self.zoomScale)
        self.view.resize(sw, sh)

     #-----------------------
 
     #-----------------------
 
    #-----------------------
    # オリジナルサイズ画像表示          
    def pngOrg(self):
        print("btnOrg")
        self.pixmap = self.orgPixmap
        # pixmapをsceneに追加
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        # ウィジェットを更新
        self.update()
        #
 
    #-----------------------
    # 画像ファイルを開く
    def pngOpenFile(self):
        self.filepath = QFileDialog.getOpenFileName(self, 'open file', '', 'Images (*.png)')[0]
        if self.filepath:
            if self.setImage(self.filepath):
                self.pngFit()

    #-----------------------
    # 画像ファイルをセット
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
    #  自動再生
    def autiDec(self):
        print("btnAutoDec")
        try:
            self.timer.stop()
            self.timer.timeout.disconnect()
        except Exception as e:
            print(f"autoInc:{e}")
        self.timer.timeout.connect(self.pngDec)
        self.timer.start(500)  # 0.5秒ごとに更新

    def autoStop(self):
        print("btnAutoStop")
        self.timer.stop()

    def autoInc(self):
        print("btnAutoInc")
        try:
            self.timer.stop()
            self.timer.timeout.disconnect()
        except Exception as e:
            print(f"autoInc:{e}")
        self.timer.timeout.connect(self.pngInc)
        self.timer.start(500)  # 0.5秒ごとに更新

    #---------------------------------
    #   -1 png 移動
    def pngDec(self):
        print("btnDec")
        #
        self.currentRow -= 1
        if self.currentRow < 0:
            self.currentRow = 0
            self.autoStop()
        #
        fileName = self.resultTable.item( self.currentRow, 1)
        # cnt = self.folderTable.item(row, 2)
        pngFile = f"{self.gSearchFld}/{fileName.text()}"
        if self.setImage(pngFile):
            self.setCntLabel(pngFile)
            self.pngFit()

    #---------------------------------
    #   +1 png 移動
    def pngInc(self):
        print("btnInc")
        #
        self.currentRow += 1
        if self.currentRow >= self.resultTable.rowCount():
            self.currentRow = self.resultTable.rowCount() - 1
            self.autoStop()
        #
        fileName = self.resultTable.item( self.currentRow, 1)
        # cnt = self.folderTable.item(row, 2)
        pngFile = f"{self.gSearchFld}/{fileName.text()}"
        if self.setImage(pngFile):
            self.setCntLabel(pngFile)
            self.pngFit()

    #---------------------------------
    #   ラベル表示
    def setCntLabel(self,pngFile):
        cntStr = f"{self.currentRow+1}/{self.resultTable.rowCount()}"
        self.cntLabel.setText(str(cntStr))
        self.pathLabel.setText(pngFile)

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
        pngFile = f"{self.gSearchFld}{fileName.text()}"
        if os.path.exists(pngFile):
            if self.setImage(pngFile):
                self.setCntLabel(pngFile)
                self.pngFit()
            else:
                print(f"*** ERROR **** setImage:{pngFile}")
        else:
            print(f"file not found:{pngFile}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #win = MainWindow()
    win = PngCanvas()
    win.show()
    sys.exit(app.exec_())
