# -*- coding: utf-8 -*-
import sys
import ezdxf
import glob
import time
import numpy as np
from scipy.spatial import cKDTree
#
from PyQt5.QtCore import (QDir, Qt)
from PyQt5.QtWidgets import (QFileDialog,QApplication)


def summaryDump(msp,dmpF):
    entityTbl = dict()
    no=0
    filePrint(dmpF,f"#-------------- 図形サマリー ----------")
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
        filePrint(dmpF,f"{no} 図形({key}) 配置数({value})")
    #
    filePrint(dmpF,"")

def attrDump(e,dmpF):
    for atr in e.attribs:
        if len(atr.dxf.text) > 0:
            filePrint(dmpF,
                f"       Lay({atr.dxf.layer}) Tag({atr.dxf.tag}) Txt({atr.dxf.text}) "
                f"xya({atr.dxf.insert.vec2.x},{atr.dxf.insert.vec2.y},{atr.dxf.rotation})")
#----------------------------------------------
# 座標地の回転
def rotData(org,rotDo,circleList):
    rotCircleList = list()
    rot = np.radians(rotDo)
    for (lay,x,y,r) in circleList:
        x0 = x 
        y0 = y 
        x1 = x0*np.cos(rot) - y0*np.sin(rot)
        y1 = x0*np.sin(rot) + y0*np.cos(rot)
        x2 = x1 + org[0]
        y2 = y1 + org[1]
        rotCircleList.append((lay,x2,y2,r))
    #
    return rotCircleList

def insertDump(msp,GET_LAYER,blockDict,dmpF):
    no=0
    #
    insPontList = list()
    insList = list()
    #
    filePrint(dmpF,f"#-------------- INSERT({GET_LAYER}) サマリー ----------")
    for e in msp:
        if (e.dxf.layer != GET_LAYER):
            continue
        if e.DXFTYPE=="INSERT":
            filePrint(dmpF,f"{no} l({e.dxf.layer}) name:{e.dxf.name} "
                      f"xya:{e.dxf.insert.vec2.x},{e.dxf.insert.vec2.y},{e.dxf.rotation}")
            if e.dxf.name in blockDict:
                no += 1
                circleList = blockDict[e.dxf.name]
                rotCircleList = rotData(e.dxf.insert.vec2,e.dxf.rotation,circleList)
                filePrint(dmpF,f"  =>circle node:{rotCircleList}")
                for (_,x,y,_) in rotCircleList:
                    insPontList.append((x,y))
                    insList.append(e) 
            else:
                no += 1
                insPontList.append(e.dxf.insert.vec2)
                insList.append(e)
    filePrint(dmpF,f" total {no}")
    return (insPontList,insList)

def textDump(msp,GET_LAYER,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- TEXT({GET_LAYER}) サマリー ----------")
    for e in msp:
        if (e.dxf.layer != GET_LAYER):
            continue
        if e.DXFTYPE=="TEXT":
            no += 1
            filePrint(dmpF,f"{no} handle({e}) Lay({e.dxf.layer}) Txt({e.dxf.text}) rot({e.dxf.rotation}) "
                  f"xya({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.rotation})")
    filePrint(dmpF,f" total {no} ")

def lineDump(msp,GET_LAYER,dmpF):
    no=0
    #
    linePontList = list()
    lineList = list()
    #
    filePrint(dmpF,f"#-------------- LINE({GET_LAYER}) サマリー ----------")
    for e in msp:
        if (e.dxf.layer != GET_LAYER):
            continue
        if e.DXFTYPE=="LINE":
            no += 1
            filePrint(dmpF,f"{no} handle({e}) Lay({e.dxf.layer}) St({e.dxf.start.x},{e.dxf.start.y}) Ed({e.dxf.end.x},{e.dxf.end.y})")
            pt4 = ((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y))
            linePontList.append(pt4)
            lineList.append(e)
    #
    filePrint(dmpF,f" total {no} ")
    return (linePontList,lineList)

def lwpolylineDump(msp,GET_LAYER,dmpF):
    no=0
    #
    lwPontList = list()
    lwList = list()
    #
    filePrint(dmpF,f"#-------------- LWPOLYLINE({GET_LAYER}) サマリー ----------")
    for e in msp:
        if (e.dxf.layer != GET_LAYER):
            continue
        if e.DXFTYPE=="LWPOLYLINE":
            no += 1
            pts = list(e.lwpoints.values)
            #filePrint(dmpF,f"{no} handle({e}) Lay({e.dxf.layer}) Pts({pts})")
            #pt4 = ((pts[0][0:2], pts[1][0:2]), (pts[len(pts)-2][0:2], pts[len(pts)-1][0:2]))
            pt4 = (pts[0][0:2], pts[len(pts)-1][0:2])
            lwPontList.append(pt4)
            lwList.append(e)
    #
    filePrint(dmpF,f" total {no} {lwPontList}")
    return (lwPontList,lwList)

def mtextDump(msp,GET_LAYER,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- MTEXT({GET_LAYER}) サマリー ----------")
    for e in msp:
        if (e.dxf.layer != MAIN_CABLE_LAYER and e.dxf.layer != SUB_CABLE_LAYER):
            continue
        if e.DXFTYPE=="MTEXT":
            no += 1
            filePrint(dmpF,f"{no} handle({e}) Lay({e.dxf.layer}) Txt({e.text}) "
                  f"xya({e.dxf.insert.x},{e.dxf.insert.y},{e.dxf.rotation})")
    #
    filePrint(dmpF,f" total {no} ")

def pointDump(msp,GET_LAYER,dmpF):
    no=0
    filePrint(dmpF,f"#-------------- POINT({GET_LAYER}) サマリー ----------")
    for e in msp:
        if (e.dxf.layer != MAIN_CABLE_LAYER and e.dxf.layer != SUB_CABLE_LAYER):
            continue
        if e.DXFTYPE=="POINT":
            no += 1
            filePrint(dmpF,f"{no} handle({e}) Lay({e.dxf.layer}) xya({e.dxf.location.x},{e.dxf.location.y},{e.dxf.rotation})")
    #
    filePrint(dmpF,f" total {no} ")

def dumpCableData(dmpF,title,insPontList,insList,linePontList,lineList,lwpPontList,lwpList):
    filePrint(dmpF,f"=== dumpCableData ===")          
    filePrint(dmpF,f"-------------- {title} --------------------------")
    filePrint(dmpF,f"insPontList:")
    for (org,e) in zip(insPontList,insList):
        filePrint(dmpF,f"    handlehandle({e}) Lay({e.dxf.layer} name({e.dxf.name}) org{org}")
    filePrint(dmpF,f"linePontList:")
    for ((st,ed),e) in zip(linePontList,lineList):
        filePrint(dmpF,f"    handlehandle({e}) Lay({e.dxf.layer} st{st} ed{ed}")
    filePrint(dmpF,f"lwpPontList:")
    for ((st,ed),e) in zip(lwpPontList,lwpList):
        filePrint(dmpF,f"    handlehandle({e}) Lay({e.dxf.layer} st{st} ed{ed}")

def checkSecondInsert(dmpF,kd_tree, st, lwStDis):
    filePrint(dmpF,f"=== checkSecondInsert ===")        
    filePrint(dmpF,f"-------------- 2番目に近いinsertチェック --------------------------")
    (stDis, stIdx) = kd_tree.query(st)
    dist, ind = kd_tree.query(st, k=3)
    filePrint(dmpF,f"** checkSecondInsert = {ind} {dist} <-- {stIdx} {stDis}")
    if (dist[1]<lwStDis):
        return (ind[1], dist[1], True)
    else:
        return (ind[1], dist[1], False)

#----------------------------------------------1
# レイヤー別グラフ作成
def makeLayerGraph(dmpF,title,kd_tree,insList,linePontList,lineList,lwpPontList,lwpList, lstDis, ledDis, lwStDis, lwEdDis):
    filePrint(dmpF,f"=== makeLayerGraph ===")    
    filePrint(dmpF,f"-------------- {title} --------------------------")
    filePrint(dmpF,f"linePontList={len(linePontList)} :lineList={len(lineList)}")
    for ((st,ed),e) in zip(linePontList,lineList):
        (stDis,stIdx) = kd_tree.query(st)
        (edDis,edIdx) = kd_tree.query(ed)
        filePrint(dmpF,f"    {st}=>{stDis} {stIdx} : {ed}=>{edDis} {edIdx}")
        est = insList[stIdx]
        eed = insList[edIdx]
        erFlg=False
        if (stDis > lstDis or edDis > ledDis):
            filePrint(dmpF,f" *** 距離ERROR :{e.dxf.layer} stdis:{stDis:.1f} edDis:{edDis:.1f}")
            erFlg = True
        if (e.dxf.layer !=est.dxf.layer or e.dxf.layer !=eed.dxf.layer):
            filePrint(dmpF,f" *** レイヤーWARNING :{e.dxf.layer} st:{est.dxf.layer} ed:{est.dxf.layer}")
            erFlg = True
        if erFlg:
            filePrint(dmpF,f" *** handle({e}) st{st} ed{ed} : {est}/{stIdx}/{stDis:.1f}-{eed}/{edIdx}/{edDis:.1f}")
        else:
            filePrint(dmpF,f"     handle({e}) st{st} ed{ed} : {est}/{stIdx}/{stDis:.1f}-{eed}/{edIdx}/{edDis:.1f}")

    filePrint(dmpF,f"lwpPontList={len(lwpPontList)} :lwpList={len(lwpList)}")
    for ((st,ed),e) in zip(lwpPontList,lwpList):
        (stDis,stIdx) = kd_tree.query(st)
        (edDis,edIdx) = kd_tree.query(ed)
        filePrint(dmpF,f"\n    {st}=>{stDis} {stIdx} : {ed}=>{edDis} {edIdx}")       
        eed = insList[edIdx]
        if (stIdx == edIdx):
            filePrint(dmpF,f" *** 同一INSERT({eed}) WARNING :{e.dxf.layer} {stIdx}/{stDis:.1f} ../{edDis:.1f}")
            (stIdx,stDis,errFlg) = checkSecondInsert(dmpF,kd_tree, st, lwStDis)
        #
        est = insList[stIdx]
        erFlg=False
        if (stDis > lwStDis or edDis > lwEdDis):
            filePrint(dmpF,f" *** 距離ERROR :{e.dxf.layer} stdis:{stDis:.1f} edDis:{edDis:.1f}")
            erFlg = True
        if (e.dxf.layer !=est.dxf.layer or e.dxf.layer !=eed.dxf.layer):
            filePrint(dmpF,f" *** レイヤーWARNING :{e.dxf.layer} st:{est.dxf.layer} ed:{est.dxf.layer}")
            erFlg = True
        if erFlg:
            filePrint(dmpF,f" *** handle({e}) st{st} ed{ed} : {est}/{stIdx}/{stDis:.1f}-{eed}/{edIdx}/{edDis:.1f}")
        else:
            filePrint(dmpF,f"     handle({e}) st{st} ed{ed} : {est}/{stIdx}/{stDis:.1f}-{eed}/{edIdx}/{edDis:.1f}")

#----------------------------------------------
# インスタンス名テーブル取得
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
#----------------------------------------------
# ブロックから接続ノードを取得
def getBlockNode(dmpF,doc):
    filePrint(dmpF,f"=== getBlockNode ===")
    blockDict = dict()
    #
    insertTbl = getInstalNameTable(doc)
    keySorted = sorted(insertTbl.items(), key=lambda x: x[0])
    bno=0
    filePrint(dmpF,f"-------------- BLOCKサマリー ----------")
    for (blockName,cnt) in keySorted:
        bno
        filePrint(dmpF,f"-------------- BLOCK{bno} ={blockName} : {cnt} ----------")
        # ブロック定義を取得
        block_def = doc.blocks[blockName]
        # ブロック内のcircleエンティティを調べる
        no = 0
        circleList = list()
        for e in block_def:
            if e.DXFTYPE=="CIRCLE":
                if e.dxf.radius != 0.1:
                    continue
                circleData = (e.dxf.layer,e.dxf.center.x,e.dxf.center.y,e.dxf.radius)
                circleList.append(circleData)
        #
        if len(circleList) > 0:
            blockDict[blockName] = circleList
    #
    return blockDict    

#----------------------------------------------1
# 全体グラフ作成
def buildCableGraph(dxfFile,dmpF):
    filePrint(dmpF,f"=== buildCableGraph ===")
    doc = ezdxf.readfile(dxfFile)
    msp = doc.modelspace()
    #
    blockDict = getBlockNode(dmpF,doc)
    #
    (insMainPontList,insMainList) = insertDump(msp,MAIN_CABLE_LAYER,blockDict,dmpF)
    (lineMainPontList,lineMainList) = lineDump(msp,MAIN_CABLE_LAYER,dmpF)    
    (lwMainPontList,lwMainList) = lwpolylineDump(msp,MAIN_CABLE_LAYER,dmpF)    
    #
    (insSubPontList1,insSubList1) = insertDump(msp,SUB_CABLE_LAYER1,blockDict,dmpF)
    (lineSubPontList1,lineSubList1) = lineDump(msp,SUB_CABLE_LAYER1,dmpF)
    (lwSubPontList1,lwSubList1) = lwpolylineDump(msp,SUB_CABLE_LAYER1,dmpF)       
    #
    if SUB_CABLE_LAYER2 != None:
        (insSubPontList2,insSubList2) = insertDump(msp,SUB_CABLE_LAYER2,blockDict,dmpF)
        (lineSubPontList2,lineSubList2) = lineDump(msp,SUB_CABLE_LAYER2,dmpF)
        (lwSubPontList2,lwSubList2) = lwpolylineDump(msp,SUB_CABLE_LAYER2,dmpF)        
    else:
        (insSubPontList2,insSubList2) = (None,None)   
        (insSubPontList2,lineSubList2) = (None,None)   
        (insSubPontList2,lwSubList2) = (None,None)
    #
    insPontList = insMainPontList
    insPontList.extend(insSubPontList1)
    #
    insList = insMainList
    insList.extend(insSubList1)
    #
    if SUB_CABLE_LAYER2 != None:
        insPontList.extend(insSubPontList2)
        insList.extend(insSubList2)
    #
    insData = np.array(insPontList)
    kd_tree = cKDTree(insData)
    #
    makeLayerGraph(dmpF,"MAIN_CABLE", kd_tree,insList,lineMainPontList,lineMainList,lwMainPontList,lwMainList, 5,0.001, 5, 0.001)
    makeLayerGraph(dmpF,"SUB_CABLE1", kd_tree,insList,lineSubPontList1,lineSubList1,lwSubPontList1,lwSubList1, 5, 5, 5,0.001)
    #
    if SUB_CABLE_LAYER2 != None:
        makeLayerGraph(dmpF,"SUB_CABLE2", kd_tree,insList,lineSubPontList2,lineSubList2,lwSubPontList2,lwSubList2, 5, 5, 5,0.001)
    #
    return

    

#----------------------------------------------
#   node-link data (グラフ）作成
def mainBuildGraphg(dxfPat,dmpFile="dxf_link.txt"):
    gDumpF =  open(dmpFile, "w")  
    #    
    blockSummary = dict()
    cnt=0
    for dxfFile in glob.glob(dxfPat):
        cnt +=1
        filePrint(gDumpF,f"-------------- {cnt} : {dxfFile} ----------")
        try:
            buildCableGraph(dxfFile,gDumpF)
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

#----------------------------------------------
#   ファイルとコンソール出力   
def filePrint(dmpF,str):
    print(str)
    dmpF.write(str + "\n")

#----------------------------------------------
#   ファイル選択ダイアログ  
def open_file():
        filename, filter = QFileDialog.getOpenFileName(None, 'Open file', '', 'CAD files (*.dxf *.DXF)')
        return filename

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #
    if len(sys.argv) < 2:
        dxdFile ="sample/Zu03.dxf"
    else:
        dxdFile = sys.argv[1]
    #
    if dxdFile == "":
        exit(-1)
    print(f"Start {dxdFile}")
    #
    if False:
        # 500C-TL 主線
        MAIN_CABLE_LAYER = "500C-TL"
        # 500C-BL 分岐信号線
        SUB_CABLE_LAYER1 = "500C-BL"
        SUB_CABLE_LAYER2 = "FK-12C-BL"
    else:
         # 500C-TL 主線
        MAIN_CABLE_LAYER = "KAN"
        # 500C-BL 分岐信号線
        SUB_CABLE_LAYER1 = "BUN"
        SUB_CABLE_LAYER2 = "DROP"       
    #
    start = time.time()
    mainBuildGraphg(dxdFile)
    elapsed_time = time.time() - start
    print (f"elapsed_time:{elapsed_time}[sec]")
