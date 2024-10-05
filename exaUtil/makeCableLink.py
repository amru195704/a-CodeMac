# -*- coding: utf-8 -*-
import sys
import ezdxf
import glob
import time
import numpy as np
from scipy.spatial import cKDTree

from PyQt5.uic.properties import QtWidgets


def summaryDump(msp):
    entityTbl = dict()
    no=0
    print(f"#-------------- 図形サマリー ----------")
    for e in msp:
        if e.DXFTYPE=="INSERT":
            layTyp = f"{e.dxf.layer}-{e.DXFTYPE}-{e.dxf.name}"
        else:
            layTyp = f"{e.dxf.layer}-{e.DXFTYPE}"

        if layTyp in entityTbl:
            entityTbl[layTyp] +=1
        else:
            entityTbl[layTyp] =1
    keySorted = sorted(entityTbl.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        print(f"{no} 図形({key}) 配置数({value})")
    print()

def attrDump(e):
    for atr in e.attribs:
        if len(atr.dxf.text) > 0:
            print(
                f"       Lay({atr.dxf.layer}) Tag({atr.dxf.tag}) Txt({atr.dxf.text}) xya({atr.dxf.insert.vec2.x},{atr.dxf.insert.vec2.y},{atr.dxf.insert.angle_deg})")


def insertDump(msp,GET_LAYER):
    no=0
    #
    insPontList = list()
    insList = list()
    #
    #print(f"#-------------- INSERT サマリー ----------")
    for e in msp:
        if (e.dxf.layer != GET_LAYER):
            continue
        if e.DXFTYPE=="INSERT":
            no += 1
            insPontList.append(e.dxf.insert.vec2)
            insList.append(e)
    #print()
    return (insPontList,insList)

def textDump(msp,GET_LAYER):
    no=0
    print(f"#-------------- TEXT サマリー ----------")
    for e in msp:
        if (e.dxf.layer != GET_LAYER):
            continue
        if e.DXFTYPE=="TEXT":
            no += 1
            print(f"{no} handle({e}) Lay({e.dxf.layer}) Txt({e.dxf.text}) rot({e.dxf.rotation}) xya({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.insert.angle_deg})")
    print()

def lineDump(msp,GET_LAYER):
    no=0
    #
    linePontList = list()
    lineList = list()
    #
    #print(f"#-------------- LINE サマリー ----------")
    for e in msp:
        if (e.dxf.layer != GET_LAYER):
            continue
        if e.DXFTYPE=="LINE":
            no += 1
            #print(f"{no} handle({e}) Lay({e.dxf.layer}) St({e.dxf.start.x},{e.dxf.start.y}) Ed({e.dxf.end.x},{e.dxf.end.y})")
            pt4 = ((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y))
            linePontList.append(pt4)
            lineList.append(e)

    #print()
    return (linePontList,lineList)

def lwpolylineDump(msp,GET_LAYER):
    no=0
    #
    lwPontList = list()
    lwList = list()
    #
    #print(f"#-------------- LWPOLYLINE サマリー ----------")
    for e in msp:
        if (e.dxf.layer != GET_LAYER):
            continue
        if e.DXFTYPE=="LWPOLYLINE":
            no += 1
            pts = list(e.lwpoints.values)
            #print(f"{no} handle({e}) Lay({e.dxf.layer}) Pts({pts})")
            pt4 = ((pts[0], pts[1]), (pts[-5], pts[-4]))
            lwPontList.append(pt4)
            lwList.append(e)
    print()
    return (lwPontList,lwList)

def mtextDump(msp,GET_LAYER):
    no=0
    print(f"#-------------- MTEXT サマリー ----------")
    for e in msp:
        if (e.dxf.layer != MAIN_CABLE_LAYER and e.dxf.layer != SUB_CABLE_LAYER):
            continue
        if e.DXFTYPE=="MTEXT":
            no += 1
            print(f"{no} handle({e}) Lay({e.dxf.layer}) Txt({e.text}) xya({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.insert.angle_deg})")
    print()

def pointDump(msp,GET_LAYER):
    no=0
    print(f"#-------------- POINT サマリー ----------")
    for e in msp:
        if (e.dxf.layer != MAIN_CABLE_LAYER and e.dxf.layer != SUB_CABLE_LAYER):
            continue
        if e.DXFTYPE=="POINT":
            no += 1
            print(f"{no} handle({e}) Lay({e.dxf.layer}) xya({e.dxf.location.x},{e.dxf.location.y},{e.dxf.location.angle_deg})")
    print()

def dumpCableData(title,insPontList,insList,linePontList,lineList,lwpPontList,lwpList):
    print(f"-------------- {title} --------------------------")
    print(f"insPontList:")
    for (org,e) in zip(insPontList,insList):
        print(f"    handlehandle({e}) Lay({e.dxf.layer} name({e.dxf.name}) org{org}")
    print(f"linePontList:")
    for ((st,ed),e) in zip(linePontList,lineList):
        print(f"    handlehandle({e}) Lay({e.dxf.layer} st{st} ed{ed}")
    print(f"lwpPontList:")
    for ((st,ed),e) in zip(lwpPontList,lwpList):
        print(f"    handlehandle({e}) Lay({e.dxf.layer} st{st} ed{ed}")

def checkSecondInsert(kd_tree, st, lwStDis):
    print(f"-------------- 2番目に近いinsertチェック --------------------------")
    (stDis, stIdx) = kd_tree.query(st)
    dist, ind = kd_tree.query(st, k=3)
    print(f"** checkSecondInsert = {ind} {dist} <-- {stIdx} {stDis}")
    if (dist[1]<lwStDis):
        return (ind[1], dist[1], True)
    else:
        return (ind[1], dist[1], False)

def makeCableGraph2(title,kd_tree,insList,linePontList,lineList,lwpPontList,lwpList, lstDis, ledDis, lwStDis, lwEdDis):
    print(f"-------------- {title} --------------------------")
    print(f"linePontList:")
    for ((st,ed),e) in zip(linePontList,lineList):
        (stDis,stIdx) = kd_tree.query(st)
        (edDis,edIdx) = kd_tree.query(ed)
        est = insList[stIdx]
        eed = insList[edIdx]
        erFlg=False
        if (stDis > lstDis or edDis > ledDis):
            print(f" *** 距離ERROR :{e.dxf.layer} stdis:{stDis:.1f} edDis:{edDis:.1f}")
            erFlg = True
        if (e.dxf.layer !=est.dxf.layer or e.dxf.layer !=eed.dxf.layer):
            print(f" *** レイヤーWARNING :{e.dxf.layer} st:{est.dxf.layer} ed:{est.dxf.layer}")
            erFlg = True
        if erFlg:
            print(f" *** handle({e}) st{st} ed{ed} : {est}/{stIdx}/{stDis:.1f}-{eed}/{edIdx}/{edDis:.1f}")
        else:
            print(f"     handle({e}) st{st} ed{ed} : {est}/{stIdx}/{stDis:.1f}-{eed}/{edIdx}/{edDis:.1f}")

    print(f"lwpPontList:")
    for ((st,ed),e) in zip(lwpPontList,lwpList):
        (stDis,stIdx) = kd_tree.query(st)
        (edDis,edIdx) = kd_tree.query(ed)
        eed = insList[edIdx]
        if (stIdx == edIdx):
            print(f" *** 同一INSERT({eed})　WARNING :{e.dxf.layer} {stIdx}/{stDis:.1f} ../{edDis:.1f}")
            (stIdx,stDis,errFlg) = checkSecondInsert(kd_tree, st, lwStDis)
        #
        est = insList[stIdx]
        erFlg=False
        if (stDis > lwStDis or edDis > lwEdDis):
            print(f" *** 距離ERROR :{e.dxf.layer} stdis:{stDis:.1f} edDis:{edDis:.1f}")
            erFlg = True
        if (e.dxf.layer !=est.dxf.layer or e.dxf.layer !=eed.dxf.layer):
            print(f" *** レイヤーWARNING :{e.dxf.layer} st:{est.dxf.layer} ed:{est.dxf.layer}")
            erFlg = True
        if erFlg:
            print(f" *** handle({e}) st{st} ed{ed} : {est}/{stIdx}/{stDis:.1f}-{eed}/{edIdx}/{edDis:.1f}")
        else:
            print(f"     handle({e}) st{st} ed{ed} : {est}/{stIdx}/{stDis:.1f}-{eed}/{edIdx}/{edDis:.1f}")

def entityDump(dxfFile):
    doc = ezdxf.readfile(dxfFile)
    msp = doc.modelspace()
    #
    #summaryDump(msp)
    #
    (insMainPontList,insMainList) = insertDump(msp,MAIN_CABLE_LAYER)
    (insSubPontList1,insSubList1) = insertDump(msp,SUB_CABLE_LAYER1)
    (insSubPontList2,insSubList2) = insertDump(msp,SUB_CABLE_LAYER2)
    #
    (lineMainPontList,lineMainList) = lineDump(msp,MAIN_CABLE_LAYER)
    (lineSubPontList1,lineSubList1) = lineDump(msp,SUB_CABLE_LAYER1)
    (lineSubPontList2,lineSubList2) = lineDump(msp,SUB_CABLE_LAYER2)
    #
    (lwMainPontList,lwMainList) = lwpolylineDump(msp,MAIN_CABLE_LAYER)
    (lwSubPontList1,lwSubList1) = lwpolylineDump(msp,SUB_CABLE_LAYER1)
    (lwSubPontList2,lwSubList2) = lwpolylineDump(msp,SUB_CABLE_LAYER2)
    #mtextDump(msp)
    #pointDump(msp)
    #textDump(msp)
    #
    insPontList = insMainPontList
    insPontList.extend(insSubPontList1)
    insPontList.extend(insSubPontList2)
    #
    insList = insMainList
    insList.extend(insSubList1)
    insList.extend(insSubList2)
    #
    insData = np.array(insPontList)
    kd_tree = cKDTree(insData)
    #
    makeCableGraph2("MAIN_CABLE", kd_tree,insList,lineMainPontList,lineMainList,lwMainPontList,lwMainList, 5,0.001, 5, 0.001)
    makeCableGraph2("SUB_CABLE1", kd_tree,insList,lineSubPontList1,lineSubList1,lwSubPontList1,lwSubList1, 5, 5, 5,0.001)
    makeCableGraph2("SUB_CABLE2", kd_tree,insList,lineSubPontList2,lineSubList2,lwSubPontList2,lwSubList2, 5, 5, 5,0.001)
    #
    return

def mainDump(dxfPat):
    blockSummary = dict()
    cnt=0
    for dxfFile in glob.glob(dxfPat):
        cnt +=1
        print(f"-------------- {cnt} : {dxfFile} ----------")
        try:
            entityDump(dxfFile)
        except Exception as e:
            print(f"mainDump:{e}")
            pass

    keySorted = sorted(blockSummary.items(), key=lambda x: x[0])
    no=0
    for (key,value) in keySorted:
        no +=1
        print(f"block{no}={key} : {value}")

def open_file():
        filename, filter = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', '', 'CAD files (*.dxf *.DXF)')
        return filename

if __name__ == '__main__':
    if len(sys.argv) < 2:
        dxdFile = open_file()
    else:
        dxdFile = sys.argv[1]
    #
    if dxdFile == "":
        exit(-1)
    print(f"Start {dxdFile}")
    #
    # 500C-TL 主線
    MAIN_CABLE_LAYER = "500C-TL"
    # 500C-BL 分岐信号線
    SUB_CABLE_LAYER1 = "500C-BL"
    SUB_CABLE_LAYER2 = "FK-12C-BL"
    #
    start = time.time()
    mainDump(dxdFile)
    elapsed_time = time.time() - start
    print (f"elapsed_time:{elapsed_time}[sec]")
