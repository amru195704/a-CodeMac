# -*- coding: utf-8 -*-
import sys,os
import ezdxf
import glob
import time

global gDumpF

def getInstalNameTable(doc):
    msp = doc.modelspace()
    insertTbl = dict()
    for e in msp:
        if e.DXFTYPE=="INSERT":
            if e.dxf.name in insertTbl:
                insertTbl[e.dxf.name] +=1
            else:
                insertTbl[e.dxf.name] =1
    #
    return insertTbl

def oneFileBlcokDump(doc,dmpF):
    insertTbl = getInstalNameTable(doc)
    keySorted = sorted(insertTbl.items(), key=lambda x: x[0])
    bno=0
    filePrint(dmpF,f"-------------- BLOCKサマリー ----------")
    for (blockName,cnt) in keySorted:
        bno
        filePrint(dmpF,f"-------------- BLOCK{bno} ={blockName} : {cnt} ----------")
        # ブロック定義を取得
        block_def = doc.blocks[blockName]
        # ブロック内のエンティティを調べる
        no = 0
        for e in block_def:
            no += 1
            if e.DXFTYPE=="INSERT":
                filePrint(dmpF,f" {no} INSERT Lay({e.dxf.layer}) name:{e.dxf.name} "
                      f"xya:{e.dxf.insert.vec2.x},{e.dxf.insert.vec2.y},{e.dxf.rotation}")
            elif e.DXFTYPE=="TEXT":
                filePrint(dmpF,f" {no} TEXT Lay({e.dxf.layer}) Txt({e.dxf.text}) rot({e.dxf.rotation}) "
                      f"xya({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.rotation})")
            elif e.DXFTYPE=="LINE":
                filePrint(dmpF,f" {no} LINE Lay({e.dxf.layer}) St({e.dxf.start.x},{e.dxf.start.y}) Ed({e.dxf.end.x},{e.dxf.end.y})")
            elif e.DXFTYPE=="LWPOLYLINE":
                pts = e.lwpoints.values
                filePrint(dmpF,f" {no} LWPOLYLINE Lay({e.dxf.layer}) Pts({list(pts)})")     
            elif e.DXFTYPE=="MTEXT":
                filePrint(dmpF,f" {no} MTEXT Lay({e.dxf.layer}) Txt({e.text}) "
                      f"({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.rotation})")     
            elif e.DXFTYPE=="POINT":
                filePrint(dmpF,f" {no} POINT Lay({e.dxf.layer}) ({e.dxf.location.x},{e.dxf.location.y})")
            elif e.DXFTYPE=="CIRCLE":
                filePrint(dmpF,f" {no} CIRCLE Lay({e.dxf.layer}) ({e.dxf.center.x},{e.dxf.center.y},{e.dxf.radius})")  
            elif e.DXFTYPE=="ATTDEF":
                filePrint(dmpF,f" {no} ATTDEF Lay({e.dxf.layer}) tag({e.dxf.tag}) {e.dxf.text}")
            else:
                filePrint(dmpF,f" {no} {e.DXFTYPE} Lay({e.dxf.layer})")
            #if e.DXFTYPE!="TEXT":                     
            #    for atr in e.attribs:
            #        if len(atr.dxf.text)>0:
            #            filePrint(dmpF,f"       l({atr.dxf.layer}) {atr.dxf.tag}={atr.dxf.text} "
            #                    f"xya:{atr.dxf.insert.vec2.x},{atr.dxf.insert.vec2.y},{atr.dxf.rotation}")
    #
    return

def mainDump(dxfPat,dmpFile="dxf_block.txt"):
    global gDumpF
    blockSummary = dict()
    gDumpF =  open(dmpFile, "w") 
    cnt=0
    for dxfFile in glob.glob(dxfPat):
        cnt +=1
        filePrint(gDumpF,f"-------------- {cnt} : {dxfFile} ----------")
        doc = ezdxf.readfile(dxfFile)
        try:
            oneFileBlcokDump(doc,gDumpF)
        except Exception as e:
            filePrint(gDumpF,f"mainDump:{e}")
            pass

    keySorted = sorted(blockSummary.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        filePrint(dmpF,f"block{no}={key} : {value}")
    #
    gDumpF.close()

def filePrint(dmpF,str):
    print(str)
    dmpF.write(str + "\n")

if __name__ == '__main__':
    print(os.getcwd())
    if len(sys.argv) < 2:
        dxdFile = "sample/*.dxf"
    else:
        dxdFile = sys.argv[1]
    print(f"Start {dxdFile}")
    start = time.time()
    mainDump(dxdFile)
    elapsed_time = time.time() - start
    print (f"elapsed_time:{elapsed_time}[sec]")
