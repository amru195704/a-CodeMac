# -*- coding: utf-8 -*-
import sys
import ezdxf
import glob
import time

def summaryDump(msp):
    entityTbl = dict()
    no=0
    filePrint(f"#-------------- 図形サマリー ----------")
    for e in msp:
        if e.DXFTYPE in entityTbl:
            entityTbl[e.DXFTYPE] +=1
        else:
            entityTbl[e.DXFTYPE] =1
    keySorted = sorted(entityTbl.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        filePrint(f"{no} 図形({key}) 配置数({value})")
    filePrint(" ")

def attrDump(e):
    for atr in e.attribs:
        if len(atr.dxf.text) > 0:
            filePrint(
                f"       Lay({atr.dxf.layer}) Tag({atr.dxf.tag}) Txt({atr.dxf.text}) "
                f"xya({atr.dxf.insert.vec2.x},{atr.dxf.insert.vec2.y},{atr.dxf.rotation})")


def insertDump(msp):
    no=0
    filePrint(f"#-------------- INSERT サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="INSERT":
            no += 1
            filePrint(f"{no} Lay({e.dxf.layer}) name({e.dxf.name}) "
                      f"xya({e.dxf.insert.vec2.x},{e.dxf.insert.vec2.y},{e.dxf.rotation})")
            attrDump(e)
    filePrint(" ")

def textDump(msp):
    no=0
    filePrint(f"#-------------- TEXT サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="TEXT":
            no += 1
            filePrint(f"{no} Lay({e.dxf.layer}) Txt({e.dxf.text}) rot({e.dxf.rotation}) "
                      f"xya({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.rotation})")
    filePrint(" ")

def lineDump(msp):
    no=0
    filePrint(f"#-------------- LINE サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="LINE":
            no += 1
            filePrint(f"{no} Lay({e.dxf.layer}) St({e.dxf.start.x},{e.dxf.start.y}) Ed({e.dxf.end.x},{e.dxf.end.y})")
    filePrint(" ")

def lwpolylineDump(msp):
    no=0
    filePrint(f"#-------------- LWPOLYLINE サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="LWPOLYLINE":
            no += 1
            pts = e.lwpoints.values
            filePrint(f"{no} Lay({e.dxf.layer}) Pts({list(pts)})")
    filePrint(" ")

def mtextDump(msp):
    no=0
    filePrint(f"#-------------- MTEXT サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="MTEXT":
            no += 1
            filePrint(f"{no} Lay({e.dxf.layer}) Txt({e.text}) "
                      f"({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.})")
    filePrint(" ")

def pointDump(msp):
    no=0
    filePrint(f"#-------------- POINT サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="POINT":
            no += 1
            filePrint(f"{no} Lay({e.dxf.layer}) ({e.dxf.location.x},{e.dxf.location.y},{e.dxf.rotation})")
    filePrint(" ")

def entityDump(dxfFile):
    doc = ezdxf.readfile(dxfFile)
    msp = doc.modelspace()
    #
    summaryDump(msp)
    #
    insertDump(msp)
    lineDump(msp)
    lwpolylineDump(msp)
    mtextDump(msp)
    pointDump(msp)
    textDump(msp)
    #
    return

def mainDump(dxfPat):
    global gDumpF
    gDumpF =  open("dxf_entity.txt", "w")    
    #   
    blockSummary = dict()
    cnt=0
    for dxfFile in glob.glob(dxfPat):
        cnt +=1
        filePrint(f"-------------- {cnt} : {dxfFile} ----------")
        try:
            entityDump(dxfFile)
        except Exception as e:
            filePrint(f"mainDump:{e}")
            pass

    keySorted = sorted(blockSummary.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        filePrint(f"block{no}={key} : {value}")
    #
    gDumpF.close()
    
def filePrint(str):
    global gDumpF
    print(str)
    gDumpF.write(str + "\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        dxdFile = "sample/*.dxf"
    else:
        dxdFile = sys.argv[1]
    print(f"Start {dxdFile}")
    start = time.time()
    mainDump(dxdFile)
    elapsed_time = time.time() - start
    print (f"elapsed_time:{elapsed_time}[sec]")
