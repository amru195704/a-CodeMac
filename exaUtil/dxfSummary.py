# -*- coding: utf-8 -*-

from PyQt5.QtCore import (QDir, Qt)
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
                             QDialogButtonBox, QVBoxLayout,
                             QDialog, QFileDialog, QGridLayout, QHBoxLayout, QLabel,
                             QProgressDialog, QPushButton, QSizePolicy, QTableWidget,
                             QTableWidgetItem, QMessageBox, QMenu)

import sys
sys.path.append(".")
sys.path.append("exaUtil")
import subprocess
import os

import fileUtil
import PngUtil



class Window(QDialog):
    global gSearchFld
    global gOutFld
    
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        # closeボタン
        buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        #------ ボタン定義 ------
        # フォルダー選択
        browseButton = self.createButton("フォルダー指定...", self.browse)
        outBrowseButton = self.createButton("フォルダー指定...", self.outBrowse)  
        #　検索ボタン
        findDxfButton = self.createButton("dxf検索", self.findDxf)
        findPngButton = self.createButton("png検索", self.findPng)
        #　検索結果処理ボタン
        sClearButton = self.createButton("選択クリアー", self.sClear)
        sAllButton = self.createButton("全選択", self.sAll)
        sFldListSaveButton = self.createButton("フォルダーリスト保存", self.sFldListSave)
        sFileListSaveButton = self.createButton("ファイルリスト保存", self.sFileListSave)
        #　解析ボタン
        sLayerButton = self.createButton("レイヤー調査", self.sLayer)
        sSymbolButton = self.createButton("シンボル調査", self.sSymbo)
        sPNGButton = self.createButton("画像変換", self.sDxf2Png)
        # 検索ボタン関連
        self.directoryComboBox = self.createComboBox(QDir.currentPath())
        self.directoryComboBox.resize(500, 16)
        directoryLabel = QLabel("検索ルート:")
        directoryLabel.resize(300,16)
        # メッセージラベル
        self.messageLabel = QLabel()
        self.messageLabel.resize(400,40)
        # 保存ボタン関連
        self.outDirectoryComboBox = self.createComboBox(QDir.currentPath())
        self.outDirectoryComboBox.resize(500, 16)
        outDirectoryLabel = QLabel("出力ルート:")
        outDirectoryLabel.resize(300,16)
        #　検索結果フォルダー
        self.createFolderTable()
        # -------- レイアウト --------
        #  検索ボタン
        findBLayout = QHBoxLayout()
        findBLayout.addWidget(self.messageLabel)
        findBLayout.addStretch()
        findBLayout.addWidget(findDxfButton)
        findBLayout.addWidget(findPngButton)
        #　結果表示リスト
        resultLayout = QGridLayout()
        resultLayout.addWidget(self.folderTable, 0, 0, 1,1)
        resultLayout.addWidget(self.resultTable, 0, 2, 1,1)
        #　検索結果処理ボタン
        dxfBLayout1 = QHBoxLayout()
        dxfBLayout1.addWidget(sClearButton)
        dxfBLayout1.addWidget(sAllButton)
        dxfBLayout1.addWidget(sFldListSaveButton)
        dxfBLayout1.addStretch()
        dxfBLayout1.addWidget(sFileListSaveButton)
        #　解析簿ボタン
        dxfBLayout2 = QHBoxLayout()
        dxfBLayout2.addStretch()
        dxfBLayout2.addWidget(sLayerButton)
        dxfBLayout2.addWidget(sSymbolButton)
        dxfBLayout2.addWidget(sPNGButton)
        # ----- 実際の配置 -----
        execLayout = QGridLayout()
        execLayout.addWidget(directoryLabel, 2, 0)
        execLayout.addWidget(self.directoryComboBox, 2, 1)
        execLayout.addWidget(browseButton, 2, 2)
        #
        execLayout.addLayout(findBLayout, 3, 0, 1, 3)
        execLayout.addLayout(resultLayout, 4, 0, 2, 4)
        #
        execLayout.addLayout(dxfBLayout1, 6, 0, 1, 3)       
        #
        execLayout.addWidget(outDirectoryLabel, 7, 0)
        execLayout.addWidget(self.outDirectoryComboBox, 7, 1)
        execLayout.addWidget(outBrowseButton, 7, 2)   
        #
        execLayout.addLayout(dxfBLayout2, 8, 0, 1, 3)   
        #
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(execLayout)
        mainLayout.addWidget(buttonBox)
        #
        self.setLayout(mainLayout)

        self.setWindowTitle("DXF概要調査")
        #
        self.canvas = None
        self.setFixedSize(1024, 800)
        #
        #

    # ----------------------------------------------------
    #    dxf/png 検索　フォルダー指定
    # ----------------------------------------------------
    def browse(self):
        global gSearchFld
        #
        if gSearchFld is None:
            directory = QFileDialog.getExistingDirectory(self, "Find Files",
                                                         QDir.currentPath())
        else:
            directory = QFileDialog.getExistingDirectory(self, "Find Files",
                                                         gSearchFld)
        if directory:
            if self.directoryComboBox.findText(directory) == -1:
                self.directoryComboBox.addItem(directory)

            self.directoryComboBox.setCurrentIndex(self.directoryComboBox.findText(directory))
            self.directoryComboBox.resize(500,16)

    # ----------------------------------------------------
    #    png 出力　フォルダー指定
    # ----------------------------------------------------
    def outBrowse(self):
        global gOutFld
        #
        if gOutFld is None:
            directory = QFileDialog.getExistingDirectory(self, "Find Files",
                                                         QDir.currentPath())
        else:
            directory = QFileDialog.getExistingDirectory(self, "Find Files",
                                                         gOutFld)
        if directory:
            if self.outDirectoryComboBox.findText(directory) == -1:
                self.outDirectoryComboBox.addItem(directory)

            self.outDirectoryComboBox.setCurrentIndex(self.outDirectoryComboBox.findText(directory))
            self.outDirectoryComboBox.resize(500,16)
        #
        print(f"outBrowse:{directory}")
        gOutFld = directory

    # ----------------------------------------------------
    #    result clear 表示
    # ----------------------------------------------------
    def resultClear(self):
        self.resultTable.clear()
        rowmx = self.resultTable.rowCount()
        for drow in range(0,rowmx):
            self.resultTable.removeRow(rowmx-drow-1)

    # ----------------------------------------------------
    #    フォルダー選択関連機能 button
    # ----------------------------------------------------
    def sClear(self):
        print("選択クリアー実行")
        self.folderTable.clearSelection()

    # ----------------------------------------------------
    #    フォルダー全選択：結果リストに全ファイル表示
    # ----------------------------------------------------
    def sAll(self):
        print("全選択実行")
        self.folderTable.selectAll()
        self.showResultFiles(self.fileSummary)

    # ----------------------------------------------------
    #    選択ファイル数調査
    # ----------------------------------------------------
    def selectDxfFileCount(self):
        maxCnt=0
        for item in self.folderTable.selectedItems():
            row = item.row()
            col = item.column()
            if col != 1:
                continue
            cnt = self.folderTable.item(row, 2)
            maxCnt += int(cnt.text())
        #
        return maxCnt

    # ----------------------------------------------------
    #    レイヤー調査
    # ----------------------------------------------------
    # ----------------------------------------------------
    #    dxf選択 menu表示
    # ----------------------------------------------------
    def showDxfPopupMenu(self, row, column):
        #
        fileName = self.resultTable.item(row, 1)
        # cnt = self.folderTable.item(row, 2)
        dxfile = f"{gSearchFld}/{fileName.text()}"
        print(f"選択:{dxfile}")
        #
        menu = QMenu()

        action1 = menu.addAction("DXF 表示")
        action2 = menu.addAction("ケーブルリンク作成")
        action3 = menu.addAction("キャンセル")

        selected_action = menu.exec_()

        if selected_action == action1:
            self.showDxf(dxfile)
        if selected_action == action2:
            self.makeCableLink(dxfile)

    # ----------------------------------------------------
    #    dxf表示
    # ----------------------------------------------------
    def showDxf(self, dxfile):
        #
        if os.path.exists('exaUtil/dxfView.py'):
            rtn = subprocess.Popen(['python', 'exaUtil/dxfView.py', dxfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            rtn = subprocess.Popen(['python', 'dxfView.py', dxfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"rtn={rtn}")

    # ----------------------------------------------------
    #    dxf link 作成
    # ----------------------------------------------------
    def makeCableLink(self, dxfile):
        #
        if os.path.exists('exaUtil/makeCableLink.py'):
            rtn = subprocess.Popen(['python', 'exaUtil/makeCableLink.py', dxfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            rtn = subprocess.Popen(['python', 'makeCableLink.py', dxfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"rtn={rtn}")

    # ----------------------------------------------------
    #    レイヤー調査
    # ----------------------------------------------------
    def sLayer(self):
        global gSearchFld
        print("レイヤー調査実行開始")
        layerSummary = dict()
        #--- 調査対象ファイル数計算
        maxCnt = self.selectDxfFileCount()
        #---- progress バー作成
        progressDialog = QProgressDialog(self)
        progressDialog.setCancelButtonText("&Cancel")
        progressDialog.setRange(0, maxCnt)
        progressDialog.setWindowTitle("レイヤー調査")
        progressDialog.setMinimumWidth(500)
        progressDialog.show()
        #
        no = 0
        for item in self.folderTable.selectedItems():
            row = item.row()
            col = item.column()
            if col != 1:
                continue
            # no = self.folderTable.item(row, 0)
            fld = self.folderTable.item(row, 1)
            print(f"選択:{fld.text()}")
            # cnt = self.folderTable.item(row, 2)
            for (fileName,size) in self.fileSummary[fld.text()]:
                no += 1
                dxfFile = f"{gSearchFld}/{fld.text()}/{fileName}"
                msg = f"レイヤー解析中{no:4} {dxfFile}"
                self.messageLabel.setText(msg)
                print(msg)
                # ---- progress 表示
                progressDialog.setValue(no)
                progressDialog.setLabelText(f"レイヤー調査dxfファイル {no}/{maxCnt}")
                QApplication.processEvents()
                # ---- progress 表示終了
                if progressDialog.wasCanceled():
                    break
                #
                layerTbl = fileUtil.layerDump(dxfFile)
                for (key, value) in layerTbl.items():
                    if key in layerSummary:
                        layerSummary[key] += value
                    else:
                        layerSummary[key] = value
                #
            #
            # ---- progress 表示終了
            if progressDialog.wasCanceled():
                break
            msg = f"  -->レイヤー解析end{no:4} レイヤー数={len(layerSummary)}"
            self.messageLabel.setText(msg)
        #
        # ---- progress 表示終了
        progressDialog.close()
        #
        print("レイヤー解析結果表示")
        #
        self.resultClear()
        #
        self.resultTable.setHorizontalHeaderLabels(("No", "レイヤー名", "使用数"))
        lno = 0
        for (layerName, siz) in layerSummary.items():
            lno += 1
            noItem = QTableWidgetItem(f"{lno}")
            noItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            noItem.setFlags(noItem.flags() ^ Qt.ItemIsEditable)
            #
            layerNameItem = QTableWidgetItem(layerName)
            layerNameItem.setFlags(layerNameItem.flags() ^ Qt.ItemIsEditable)
            #
            sizeItem = QTableWidgetItem(f"{siz}")
            sizeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            sizeItem.setFlags(noItem.flags() ^ Qt.ItemIsEditable)
            #print(f"---- {lno} {layerName} {siz}")
            #
            row = self.resultTable.rowCount()
            self.resultTable.insertRow(row)
            self.resultTable.setItem(row, 0, noItem)
            self.setItem(row, 1, layerNameItem)
            self.resultTable.setItem(row, 2, sizeItem)
        #
        #
        print("レイヤー調査実行終了")

    # ----------------------------------------------------
    #    シンボル調査
    # ----------------------------------------------------
    def sSymbo(self):
        print("シンボル調査実行")
        global gSearchFld
        symbolSummary = dict()
        #
        #--- 調査対象ファイル数計算
        maxCnt = self.selectDxfFileCount()
        #---- progress バー作成
        progressDialog = QProgressDialog(self)
        progressDialog.setCancelButtonText("&Cancel")
        progressDialog.setRange(0, maxCnt)
        progressDialog.setWindowTitle("シンボル調査")
        progressDialog.setMinimumWidth(500)
        progressDialog.show()
        #
        no = 0
        for item in self.folderTable.selectedItems():
            row = item.row()
            col = item.column()
            if col != 1:
                continue
            # no = self.folderTable.item(row, 0)
            fld = self.folderTable.item(row, 1)
            print(f"選択:{fld.text()}")
            # cnt = self.folderTable.item(row, 2)
            for (fileName,size) in self.fileSummary[fld.text()]:
                no += 1
                dxfFile = f"{gSearchFld}/{fld.text()}/{fileName}"
                #
                msg = f"シンボル解析中{no:4} {dxfFile}"
                self.messageLabel.setText(msg)
                print(msg)
                # ---- progress 表示
                progressDialog.setValue(no)
                progressDialog.setLabelText(f"シンボル調査dxfファイル {no}/{maxCnt}")
                QApplication.processEvents()
                # ---- progress 表示終了
                if progressDialog.wasCanceled():
                    break
                #
                symbolTbl = fileUtil.symbolDump(dxfFile)
                for (key, value) in symbolTbl.items():
                    if key in symbolSummary:
                        symbolSummary[key] += value
                    else:
                        symbolSummary[key] = value
                #
            #
            # ---- progress 表示終了
            if progressDialog.wasCanceled():
                break
            msg = f"  -->シンボル解析end{no:4} シンボル数={len(symbolSummary)}"
            self.messageLabel.setText(msg)
            #
        # ---- progress 表示終了
        progressDialog.close()
        #
        print("シンボル解析結果表示")
        #
        self.resultClear()
        #
        self.resultTable.setHorizontalHeaderLabels(("No", "シンボル名", "使用数"))
        lno = 0
        for (symbolName, siz) in symbolSummary.items():
            lno += 1
            noItem = QTableWidgetItem(f"{lno}")
            noItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            noItem.setFlags(noItem.flags() ^ Qt.ItemIsEditable)
            #
            symbolNameItem = QTableWidgetItem(symbolName)
            symbolNameItem.setFlags(symbolNameItem.flags() ^ Qt.ItemIsEditable)
            #
            sizeItem = QTableWidgetItem(f"{siz}")
            sizeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            sizeItem.setFlags(noItem.flags() ^ Qt.ItemIsEditable)
            print(f"---- {lno} {symbolName} {siz}")
            #
            row = self.resultTable.rowCount()
            self.resultTable.insertRow(row)
            self.resultTable.setItem(row, 0, noItem)
            self.resultTable.setItem(row, 1, symbolNameItem)
            self.resultTable.setItem(row, 2, sizeItem)

        #
        print("シンボル調査終了")

    # ----------------------------------------------------
    #    画像変換 調査
    # ----------------------------------------------------
    # ----------------------------------------------------
    #    画像選択 png表示
    # ----------------------------------------------------
    def showPng(self, row, column):
        # no = self.folderTable.item(row, 0)
        fileName = self.resultTable.item(row, 1)
        # cnt = self.folderTable.item(row, 2)
        pngFile = f"{gSearchFld}/{fileName.text()}"
        print(f"選択:{pngFile}")
        #
        if self.canvas is None:
            self.canvas = PngUtil.PngCanvas()
        self.canvas.viewImageFile(self.resultTable,row,gSearchFld)
        self.canvas.show()

    # ----------------------------------------------------
    #    dxf->png 画像変換
    # ----------------------------------------------------
    def sDxf2Png(self):
        print("画像変換実行")
        global gSearchFld
        pngSummary = dict()
        #
        #--- 調査対象ファイル数計算
        maxCnt = self.selectDxfFileCount()
        #---- progress バー作成
        progressDialog = QProgressDialog(self)
        progressDialog.setCancelButtonText("&Cancel")
        progressDialog.setRange(0, maxCnt)
        progressDialog.setWindowTitle("画像変換")
        progressDialog.setMinimumWidth(500)
        progressDialog.show()
        #
        no = 0
        for item in self.folderTable.selectedItems():
            row = item.row()
            col = item.column()
            if col != 1:
                continue
            # no = self.folderTable.item(row, 0)
            fld = self.folderTable.item(row, 1)
            print(f"選択:{fld.text()}")
            # cnt = self.folderTable.item(row, 2)
            for (fileName,size) in self.fileSummary[fld.text()]:
                no += 1
                dxfFile = f"{gSearchFld}/{fld.text()}/{fileName}"
                pngfld = f"{gOutFld}/{fld.text()}/"
                if not os.path.exists(pngfld):
                    os.makedirs(pngfld)
                #              
                pngName = f"{gOutFld}/{fld.text()}/{fileName[:-4]}.png"
                #
                msg = f"画像変換中{no:4} {fileName} --> {pngName}"
                print(msg)
                self.messageLabel.setText(msg)
                # ---- progress 表示
                progressDialog.setValue(no)
                progressDialog.setLabelText(f"画像変換 {no}/{maxCnt}")
                QApplication.processEvents()
                # ---- progress 表示終了
                if progressDialog.wasCanceled():
                    break
                #
                fileUtil.dxf2png(dxfFile, pngName)
                pngSummary[no] = pngName
            #
            # ---- progress 表示終了
            if progressDialog.wasCanceled():
                break
        # ---- progress 表示終了
        progressDialog.close()
        #
        print("画像変換結果表示")
        #
        self.resultClear()
        #
        self.resultTable.setHorizontalHeaderLabels(("No", "画像名", "---"))
        for (lno, pngName) in pngSummary.items():
            noItem = QTableWidgetItem(f"{lno}")
            noItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            noItem.setFlags(noItem.flags() ^ Qt.ItemIsEditable)
            #
            pngNameItem = QTableWidgetItem(pngName)
            pngNameItem.setFlags(pngNameItem.flags() ^ Qt.ItemIsEditable)
            #
            print(f"---- {lno} {pngName}")
            #
            row = self.resultTable.rowCount()
            self.resultTable.insertRow(row)
            self.resultTable.setItem(row, 0, noItem)
            self.resultTable.setItem(row, 1, pngNameItem)
        #
        # --------------
        #　result 行をダブルクリックした場合の動作設定
        self.resultTable.cellActivated.connect(self.showPng)
        # --------------
        print("画像変換終了")
        
    # ----------------------------------------------------
    #    ComboBox 追加・更新(同一アイテムなら追加しない)
    # ----------------------------------------------------    
    @staticmethod
    def updateComboBox(comboBox):
        if comboBox.findText(comboBox.currentText()) == -1:
            comboBox.addItem(comboBox.currentText())

    # ----------------------------------------------------
    #    dxf検索
    # ----------------------------------------------------   
    def findDxf(self):
        global gSearchFld
        #
        self.folderTable.setRowCount(0)
        path = self.directoryComboBox.currentText()
        gSearchFld = path
        self.fileSummary = fileUtil.findAllFiles(path, "*.dxf")
        self.showFolders(self.fileSummary)
        # --------------
        #　folder 行をダブルクリックした場合の動作設定
        self.folderTable.cellActivated.connect(self.updateResultList)
        # --------------
        #　result 行をダブルクリックした場合の動作設定
        self.resultTable.cellActivated.connect(self.showDxfPopupMenu)
        # --------------
        self.resultClear()
        #

    # ----------------------------------------------------
    #    PNG検索
    # ----------------------------------------------------   
    def findPng(self):
        global gSearchFld
        #
        self.folderTable.setRowCount(0)
        path = self.directoryComboBox.currentText()
        gSearchFld = path
        self.fileSummary = fileUtil.findAllFiles(path, "*.png")
        # self.updateComboBox(self.directoryComboBox)
        self.showFolders(self.fileSummary)
        # --------------
        #　folder 行をダブルクリックした場合の動作設定
        self.folderTable.cellActivated.connect(self.updateResultList)
        # --------------
        #　result 行をダブルクリックした場合の動作設定
        self.resultTable.cellActivated.connect(self.showPng)
        # --------------
        self.resultClear()
        #

    # ----------------------------------------------------
    #    検索結果(folderTable)フォルダー設定&表示
    # ----------------------------------------------------  
    def showFolders(self, fileSummary):
        no = 0
        for (fld, fileList) in fileSummary.items():
            no += 1
            print(f"fld={fld} file数={len(fileList)}")
            #
            noItem = QTableWidgetItem(f"{no}")
            noItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            noItem.setFlags(noItem.flags() ^ Qt.ItemIsEditable)
            #
            fileNameItem = QTableWidgetItem(fld)
            fileNameItem.setFlags(fileNameItem.flags() ^ Qt.ItemIsEditable)
            #
            sizeItem = QTableWidgetItem("%d " % len(fileList))
            sizeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            sizeItem.setFlags(sizeItem.flags() ^ Qt.ItemIsEditable)

            row = self.folderTable.rowCount()
            self.folderTable.insertRow(row)
            self.folderTable.setItem(row, 0, noItem)
            self.folderTable.setItem(row, 1, fileNameItem)
            self.folderTable.setItem(row, 2, sizeItem)

        #
        msg = "%d フォルダー(s) が見つかりました" % len(fileSummary)
        self.messageLabel.setText(msg)
        #
        reply = QMessageBox.information(self,
                                        "検索終了", msg)

    def sFldListSave(self):
        print("フォルダーリスト保存")
        #
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self , 
                    "ファイル保存", "", "All Files (*);;Text Files (*.csv)", options=options)
        if file_name:
            # 選択されたファイルパスを使用してファイルを保存
            fileUtil.saveFileList(self.folderTable, file_name)
        
    # ----------------------------------------------------
    #    結果(resultTable) リスト設定&表示
    # ----------------------------------------------------
    def updateResultList(self, row, column):
        # no = self.folderTable.item(row, 0)
        fld = self.folderTable.item(row, 1)
        # cnt = self.folderTable.item(row, 2)
        print(f"選択:{fld.text()}")
        #
        self.resultClear()
        #
        self.resultTable.setHorizontalHeaderLabels(("No", "ファイル名", "kb"))
        no = 0
        for (fileName,size) in self.fileSummary[fld.text()]:
            no += 1
            noItem = QTableWidgetItem(f"{no}")
            noItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            noItem.setFlags(noItem.flags() ^ Qt.ItemIsEditable)
            #
            resultName = f"{fld.text()}/{fileName}"
            dxfNameItem = QTableWidgetItem(resultName)
            dxfNameItem.setFlags(dxfNameItem.flags() ^ Qt.ItemIsEditable)
            #
            sizeItem = QTableWidgetItem("%d KB" % (int((size + 1023) / 1024)))
            sizeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            sizeItem.setFlags(sizeItem.flags() ^ Qt.ItemIsEditable)
            #
            trow = self.resultTable.rowCount()
            self.resultTable.insertRow(trow)
            self.resultTable.setItem(trow, 0, noItem)
            self.resultTable.setItem(trow, 1, dxfNameItem)
            self.resultTable.setItem(trow, 2, sizeItem)

    def showResultFiles(self, fileSummary):
        fldCnt = 0
        fileCnt = 0
        self.resultTable.setHorizontalHeaderLabels(("No", "ファイル名", "サイズ"))
        for (fld, fileList) in fileSummary.items():
            fldCnt += 1
            #
            for (fileName,size) in fileList:
                noItem = QTableWidgetItem(f"{fileCnt}")
                noItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                noItem.setFlags(noItem.flags() ^ Qt.ItemIsEditable)
                #
                filePath=f"{fld}{fileName}"
                fileNameItem = QTableWidgetItem(filePath)
                fileNameItem.setFlags(fileNameItem.flags() ^ Qt.ItemIsEditable)
                # 右側のみ表示＆ツールチップ表示
                #fileNameItem.setTextElideMode(Qt.ElideLeft)
                #fileNameItem.setToolTip(filePath)
                #
                sizeItem = QTableWidgetItem(f"{size}")
                sizeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                sizeItem.setFlags(sizeItem.flags() ^ Qt.ItemIsEditable)

                self.resultTable.insertRow(fileCnt)
                self.resultTable.setItem(fileCnt, 0, noItem)
                self.resultTable.setItem(fileCnt, 1, fileNameItem)
                self.resultTable.setItem(fileCnt, 2, sizeItem)
                fileCnt += 1       
                     
            print(f"fld={fld} file数={len(fileList)}")
            msg = f"{fldCnt}::{fileCnt} ファイル(s) が見つかりました"
            self.messageLabel.setText(msg)
        #
        msg = f"{fldCnt}::{fileCnt} ファイル(s) が見つかりました"
        self.messageLabel.setText(msg)
        #

    def sFileListSave(self):
        print("ファイルリスト保存")
        #
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self , 
                    "ファイル保存", "", "All Files (*);;Text Files (*.csv)", options=options)
        if file_name:
            # 選択されたファイルパスを使用してファイルを保存
            fileUtil.saveFileList(self.resultTable, file_name)
    # ----------------------------------------------------
    #    utility ボタン作成とイベント設定
    # ----------------------------------------------------   
    def createButton(self, text, member):
        button = QPushButton(text)
        button.clicked.connect(member)
        return button

    # ----------------------------------------------------
    #    utility コンボボックス作成と初期値設定
    # ----------------------------------------------------   
    def createComboBox(self, text=""):
        comboBox = QComboBox()
        comboBox.setEditable(True)
        comboBox.addItem(text)
        comboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return comboBox

    # ----------------------------------------------------
    #    検索・結果 Table設定&表示
    # ----------------------------------------------------
    def createFolderTable(self):
        self.folderTable = QTableWidget(0, 3)

        self.folderTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.folderTable.setHorizontalHeaderLabels(("No", "フォルダー", "数"))
        #self.folderTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.folderTable.verticalHeader().hide()
        self.folderTable.setShowGrid(False)
        self.folderTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        #
        self.folderTable.setColumnWidth(0, 60)
        self.folderTable.setColumnWidth(1,280)
        self.folderTable.setColumnWidth(2,80)
        self.folderTable.resize(420,400)
        # --------------
        self.resultTable = QTableWidget(0, 3)
        self.resultTable.setHorizontalHeaderLabels(("No", "ファイル名", "サイズ"))
        #self.resultTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.resultTable.verticalHeader().hide()
        self.resultTable.setShowGrid(False)
        self.resultTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        #
        self.resultTable.setColumnWidth(0, 60)
        self.resultTable.setColumnWidth(1, 280)
        self.resultTable.setColumnWidth(2, 80)
        self.resultTable.resize(420,400)

if __name__ == '__main__':
    import sys

    gSearchFld = None
    gOutFld = None
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
