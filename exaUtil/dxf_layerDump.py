# -*- coding: utf-8 -*-
import sys
import ezdxf
import glob
import time

def layerDump(dxfFile):
    doc = ezdxf.readfile(dxfFile)
    #doc = ezdxf.readfile(dxfFile,"UTF-16BE")
    layerTbl = dict()
    for layer in doc.layers:
        if layer.dxf.name in layerTbl:
            layerTbl[layer.dxf.name] += 1
        else:
            layerTbl[layer.dxf.name] = 1
    return layerTbl

def mainDump(dxfPat):
    global gDumpF
    gDumpF =  open("dxf_layer.txt", "w") 
    #
    layerSummary = dict()
    cnt=0
    for dxfFile in glob.glob(dxfPat):
        cnt +=1
        filePrint(f"-------------- {cnt} : {dxfFile} ----------")
        try:
            layerTbl = layerDump(dxfFile)
            for (key, value) in layerTbl.items():
                if key in layerSummary:
                    layerSummary[key] += value
                else:
                    layerSummary[key] = value
        except Exception as e:
            filePrint(f"mainDump:{e}")
            pass
    keySorted = sorted(layerSummary.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        filePrint(f"layer{no}={key} : {value}")
    #
    gDumpF.close()
    
def filePrint(str):
    global gDumpF
    print(str)
    gDumpF.write(str + "\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        dxdFile = "sample/Zu03.dxf"
    else:
        dxdFile = sys.argv[1]
    print(f"Start {dxdFile}")
    start = time.time()
    mainDump(dxdFile)
    elapsed_time = time.time() - start
    print (f"elapsed_time:{elapsed_time}[sec]")
