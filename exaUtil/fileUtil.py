# -*- coding: utf-8 -*-
import os
import glob
import time
import ezdxf
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QWidget

from ezdxf.addons.drawing import matplotlib
# --------------------------
#  Mac で描画するために、必要
import matplotlib as plt

plt.use("Qt5Agg")


# ----------------------------------------------------
#    file検索機能
# ----------------------------------------------------
def findAllFiles(rootFld, pat):
    filePat = f"{rootFld}/**/{pat}"
    print(f" 検索パターン：{filePat}")
    allFiles = dict()
    fileSummary = dict()
    hadLen = len(rootFld)
    cnt = 0
    print(f"glob.glob {time.ctime()}:{filePat} start")
    fileAllLisy = glob.glob(filePat, recursive=True);
    print(f"glob.glob {time.ctime()}: end")
    for oneFile in fileAllLisy:
        cnt += 1
        size = QFileInfo(oneFile).size()
        oneRelPath = oneFile[hadLen:]
        (fldName, fileName) = os.path.split(oneRelPath)
        print(f"-------------- {cnt} : {oneRelPath} ----------")
        try:
            #
            if not (fldName in fileSummary):
                fileSummary[fldName] = list()
            fileSummary[fldName].append((fileName,size))
        except Exception as e:
            print(f"findAllFiles:{e}")
            pass
    # file list をソートする
    for fldName in fileSummary.keys():
        fileSummary[fldName].sort()
    #
    print(f"glob.glob {time.ctime()}: listup end")
    return fileSummary

    # ----------------------------------------------------
    #    DXF関連機能
    # ----------------------------------------------------


def layerDump(dxfFile):
    doc = ezdxf.readfile(dxfFile)
    # doc = ezdxf.readfile(dxfFile,"UTF-16BE")
    layerTbl = dict()
    for layer in doc.layers:
        if layer.dxf.name in layerTbl:
            layerTbl[layer.dxf.name] += 1
        else:
            layerTbl[layer.dxf.name] = 1
    return layerTbl


def symbolDump(dxfFile):
    doc = ezdxf.readfile(dxfFile)
    bkrs = doc.blocks
    blokTbl = dict()
    for blok in bkrs:
        if blok.name in blokTbl:
            blokTbl[blok.name] += 1
        else:
            blokTbl[blok.name] = 1
    return blokTbl

    # ----------------------------------------------------
    #    DXF 画像関連機能
    # ----------------------------------------------------


def dxf2png(dxfFile, outpng):
    doc = ezdxf.readfile(dxfFile)
    model = doc.modelspace()
    matplotlib.qsave(model, outpng)

