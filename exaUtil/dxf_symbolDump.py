# -*- coding: utf-8 -*-
import sys
import ezdxf
import glob
import time

def blockDump(dxfFile):
    doc = ezdxf.readfile(dxfFile)
    bkrs = doc.blocks
    blokTbl = dict()
    for blok in bkrs:
        if blok.name in blokTbl:
            blokTbl[blok.name] += 1
        else:
            blokTbl[blok.name] = 1
    return blokTbl

def mainDump(dxfPat):
    global gDumpF
    gDumpF =  open("dxf_symbol.txt", "w")     
    blockSummary = dict()
    cnt=0
    for dxfFile in glob.glob(dxfPat):
        cnt +=1
        filePrint(f"-------------- {cnt} : {dxfFile} ----------")
        try:
            blokTbl = blockDump(dxfFile)
            for (key, value) in blokTbl.items():
                if key in blockSummary:
                    blockSummary[key] += value
                else:
                    blockSummary[key] = value
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
