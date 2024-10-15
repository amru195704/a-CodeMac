# -*- coding: utf-8 -*-
import sys,os
import ezdxf
import glob
import time

global gDumpF

def entityDump(dxfFile):
    doc = ezdxf.readfile(dxfFile)
    msp = doc.modelspace()
    entityTbl = dict()
    no=0
    filePrint(f"-------------- INSERTサマリー ----------")
    for e in msp:
        if e.DXFTYPE in entityTbl:
            entityTbl[e.DXFTYPE] +=1
        else:
            entityTbl[e.DXFTYPE] =1
        if e.DXFTYPE=="INSERT":
            no += 1
            filePrint(f"{no} l({e.dxf.layer}) name:{e.dxf.name} "
                      f"xya:{e.dxf.insert.vec2.x},{e.dxf.insert.vec2.y},{e.dxf.rotation}")
            for atr in e.attribs:
                if len(atr.dxf.text)>0:
                    filePrint(f"       l({atr.dxf.layer}) {atr.dxf.tag}={atr.dxf.text} "
                              f"xya:{atr.dxf.insert.vec2.x},{atr.dxf.insert.vec2.y},{atr.dxf.rotation}")
    #
    filePrint(f"-------------- 図形サマリー ----------")
    keySorted = sorted(entityTbl.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        filePrint(f"{no} 図形={key} 配置数={value}")
    return

def mainDump(dxfPat):
    global gDumpF
    gDumpF =  open("dxf_insert.txt", "w") 
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
    print(os.getcwd())
    if len(sys.argv) < 2:
        dxdFile = "sample/Zu03.dxf"
    else:
        dxdFile = sys.argv[1]
    print(f"Start {dxdFile}")
    start = time.time()
    mainDump(dxdFile)
    elapsed_time = time.time() - start
    print (f"elapsed_time:{elapsed_time}[sec]")
