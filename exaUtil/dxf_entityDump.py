# -*- coding: utf-8 -*-
import sys
import ezdxf
import glob
import time

def summaryDump(msp,dmpF):
    entityTbl = dict()
    no=0
    filePrint(dmpF,f"#-------------- 図形サマリー ----------")
    for e in msp:
        if e.DXFTYPE in entityTbl:
            entityTbl[e.DXFTYPE] +=1
        else:
            entityTbl[e.DXFTYPE] =1
    keySorted = sorted(entityTbl.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        filePrint(dmpF,f"{no} 図形({key}) 配置数({value})")
    filePrint(dmpF," ")

def attrDump(e,dmpF):
    for atr in e.attribs:
        if len(atr.dxf.text) > 0:
            filePrint(dmpF,
                f"       Lay({atr.dxf.layer}) Tag({atr.dxf.tag}) Txt({atr.dxf.text}) "
                f"xya({atr.dxf.insert.vec2.x},{atr.dxf.insert.vec2.y},{atr.dxf.rotation})")


def insertDump(msp,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- INSERT サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="INSERT":
            no += 1
            filePrint(dmpF,f"{no} Lay({e.dxf.layer}) name({e.dxf.name}) "
                      f"xya({e.dxf.insert.vec2.x},{e.dxf.insert.vec2.y},{e.dxf.rotation})")
            attrDump(e,dmpF)
    filePrint(dmpF," ")

def textDump(msp,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- TEXT サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="TEXT":
            no += 1
            filePrint(dmpF,f"{no} Lay({e.dxf.layer}) Txt({e.dxf.text}) rot({e.dxf.rotation}) "
                      f"xya({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.rotation})")
    filePrint(dmpF," ")

def lineDump(msp,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- LINE サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="LINE":
            no += 1
            filePrint(dmpF,f"{no} Lay({e.dxf.layer}) St({e.dxf.start.x},{e.dxf.start.y}) Ed({e.dxf.end.x},{e.dxf.end.y})")
    filePrint(dmpF," ")

def lwpolylineDump(msp,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- LWPOLYLINE サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="LWPOLYLINE":
            no += 1
            pts = e.lwpoints.values
            filePrint(dmpF,f"{no} Lay({e.dxf.layer}) Pts({list(pts)})")
    filePrint(dmpF," ")

def mtextDump(msp,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- MTEXT サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="MTEXT":
            no += 1
            filePrint(dmpF,f"{no} Lay({e.dxf.layer}) Txt({e.text}) "
                      f"({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.rotation})")
    filePrint(dmpF," ")

def pointDump(msp,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- POINT サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="POINT":
            no += 1
            filePrint(dmpF,f"{no} Lay({e.dxf.layer}) ({e.dxf.location.x},{e.dxf.location.y},{e.dxf.rotation})")
    filePrint(dmpF," ")

def oneFileEntityDump(doc, dmpF):
    msp = doc.modelspace()
    #
    summaryDump(msp, dmpF)
    #
    insertDump(msp, dmpF)
    lineDump(msp, dmpF)
    lwpolylineDump(msp, dmpF)
    mtextDump(msp, dmpF)
    pointDump(msp, dmpF)
    textDump(msp, dmpF)
    #
    return

def mainDump(dxfPat,dmpFile="dxf_entity.txt"):
    global gDumpF
    gDumpF =  open(dmpFile, "w")    
    #   
    blockSummary = dict()
    cnt=0
    for dxfFile in glob.glob(dxfPat):
        cnt +=1
        filePrint(gDumpF,f"-------------- {cnt} : {dxfFile} ----------")
        doc = ezdxf.readfile(dxfFile)
        try:
            oneFileEntityDump(doc, gDumpF)
        except Exception as e:
            filePrint(gDumpF,f"mainDump:{e}")
            pass

    keySorted = sorted(blockSummary.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        filePrint(gDumpF,f"block{no}={key} : {value}")
    #
    gDumpF.close()
    
def filePrint(dmpF,str):
    print(str)
    dmpF.write(str + "\n")


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
