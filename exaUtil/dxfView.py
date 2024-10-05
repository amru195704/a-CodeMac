# -*- coding: utf-8 -*-
from typing import List

import ezdxf
import sys

from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QCheckBox, QGraphicsLineItem, QGraphicsPathItem, \
    QGraphicsPolygonItem, QLineEdit
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.pyqt import PyQtBackend, CorrespondingDXFEntity, CorrespondingDXFParentStack
from ezdxf.addons.drawing.properties import is_dark_color
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.addons.drawing.qtviewer import CADGraphicsViewWithOverlay, CADGraphicsView
from PyQt5 import QtWidgets, QtCore, QtGui


# ------------------------------------------------------
#  y.maru 変更テスト
from skimage.viewer.qt import Signal


class DXFGraphicsViewWithOverlay(CADGraphicsView):

    mouse_moved = Signal(QtCore.QPointF)
    element_selected = Signal(object, int)
    double_clicked = Signal(QtCore.QPointF)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_items: List[QtWidgets.QGraphicsItem] = []
        self._selected_index = None
        #-- y.maru 最大拡大率を100-->300に変更する
        self._zoom_limits = (0.5, 300)


    def clear(self):
        super().clear()
        self._selected_items = None
        self._selected_index = None

    def begin_loading(self):
        self.clear()
        super().begin_loading()

    #---- y.maru  選択図形表示方法変更
    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawForeground(painter, rect)
        if self._selected_items:
            item = self._selected_items[self._selected_index]
            # .QGraphicsEllipseItem provides an ellipse item
            # 6.QGraphicsLineItem provides a line item
            # 2.QGraphicsPathItem provides an arbitrary path item
            # .QGraphicsPixmapItem provides a pixmap item
            # 5.QGraphicsPolygonItem provides a polygon item
            # .QGraphicsRectItem provides a rectangular item
            # .QGraphicsSimpleTextItem provides a simple text label item
            # .QGraphicsTextItem provides an advanced text browser item
            typ = item.type()
            print(f" select type:{typ}")
            if typ == 6:
                # 6.QGraphicsLineItem
                qLineF = item.line()
                print(f"line=LINE:{qLineF}")
                line = item.sceneTransform().map(qLineF)
                painter.setPen(QtGui.QColor(255, 0, 0, 100))
                painter.drawLine(line)
            elif typ == 2:
                # 2.QGraphicsPathItem
                qPainterPath = item.path()
                print(f"path=LWPOLYLINE/HATCH:{qPainterPath}")
                path = item.sceneTransform().map(qPainterPath)
                painter.setPen(QtGui.QColor(255, 0, 0, 100))
                painter.drawPath(path)
            elif typ == 5:
                # 5.QGraphicsPolygonItem
                qPolygonF = item.polygon()
                print(f"polygon={qPolygonF}")
                poly = item.sceneTransform().map(qPolygonF)
                painter.setPen(QtGui.QColor(255, 0, 0, 100))
                painter.drawPolygon(poly)
            else:
                r = item.sceneTransform().mapRect(item.boundingRect())
                #painter.fillRect(r, QtGui.QColor(0, 255, 0, 100))
                painter.fillRect(r, QtGui.QColor(255, 0, 0, 100))

    #---- y.maru 自動選択を取り除く
    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        pos = self.mapToScene(event.pos())
        self.mouse_moved.emit(pos)
        # selected_items = self.scene().items(pos)
        # if selected_items != self._selected_items:
        #     self._selected_items = selected_items
        #     self._selected_index = 0 if self._selected_items else None
        #     self._emit_selected()

    #---- y.maru   図形選択追加
    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        pos = self.mapToScene(event.pos())
        self.double_clicked.emit(pos)
        selected_items = self.scene().items(pos)
        if selected_items != self._selected_items:
            self._selected_items = selected_items
            self._selected_index = 0 if self._selected_items else None
            self._emit_selected()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if event.button() == QtCore.Qt.LeftButton and self._selected_items:
            self._selected_index = (self._selected_index + 1) % len(
                self._selected_items
            )
            self._emit_selected()

    def _emit_selected(self):
        self.element_selected.emit(self._selected_items, self._selected_index)
        self.scene().invalidate(
            self.sceneRect(), QtWidgets.QGraphicsScene.ForegroundLayer
        )


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #
        print(sys.argv)
        #
        self.resize(800, 800)

        self.render_params = {'linetype_renderer': 'ezdxf'}
        self.selectedInfo = SelectedInfo(self)
        self.layers = Layers(self)
        self.logView = LogView(self)
        self.statusLabel = QtWidgets.QLabel()
        #self.view = CADGraphicsViewWithOverlay()
        self.view = DXFGraphicsViewWithOverlay()
        self.view.setScene(QtWidgets.QGraphicsScene())
        self.view.scale(1, -1)

        self.setCentralWidget(self.view)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.layers)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.selectedInfo)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.logView)

        # self.open_file_action = QtWidgets.QAction('Open files')
        # self.open_file_action.triggered.connect(self.open_file)
        # self.menuBar().addAction(self.open_file_action)
        # self.select_layout_menu = self.menuBar().addMenu('Select Layout')
        self.statusBar().addPermanentWidget(self.statusLabel)

        self.view.element_selected.connect(self.selectedInfo.set_elements)
        self.view.mouse_moved.connect(self._on_mouse_moved)
        # -----------------
        #  layer からの再描画
        self.layers.updated_signal.connect(lambda: self.draw_layout(self.current_layout))
        self.layers.updatedFit_signal.connect(lambda: self.drawFit_layout(self.current_layout))
        #
        self.viewCnt = 0
        #
        if len(sys.argv) < 2:
            self.open_file()
        else:
            self.openDxf(sys.argv[1])

    def open_file(self):
        filename, filter = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', '', 'CAD files (*.dxf *.DXF)')
        if filename == '':
            return
        #
        self.openDxf(filename)
        #

    def openDxf(self, filename):
        print(f"openDxf={filename}")
        self.dxf = ezdxf.readfile(filename)

        self.render_context = RenderContext(self.dxf)
        # self.backend = PyQtBackend(use_text_cache=True, params=self.render_params)
        self.backend = PyQtBackend(use_text_cache=True)
        self.layers.visible_names = None
        self.current_layout = None

        self.layers.populate_layer_list(self.render_context.layers.values())
        self.drawFit_layout('Model')
        self.setWindowTitle('DXF Viewer - ' + filename)

    def change_layout(self):
        layout_name = self.sender().text()
        self.draw_layout(layout_name)

    # ----------------------------------------
    # 全体描画
    def drawFit_layout(self, layout_name):
        self.reDrawLayout(layout_name, True)

    # 再描画
    def draw_layout(self, layout_name):
        self.reDrawLayout(layout_name, False)

    #  描画共通部分
    def reDrawLayout(self, layout_name, fitFlg):
        self.current_layout = layout_name
        self.view.begin_loading()
        new_scene = QtWidgets.QGraphicsScene()
        self.backend.set_scene(new_scene)
        layout = self.dxf.layout(layout_name)
        self.render_context.set_current_layout(layout)
        if self.layers.visible_names is not None:
            self.render_context.set_layers_state(self.layers.visible_names, state=True)
        try:
            frontend = MyFrontend(self.render_context, self.backend)
            frontend.log_view = self.logView
            frontend.draw_layout(layout)
        except DXFStructureError as e:
            self.logView.append('DXF Structure Error')
            self.logView.append(f'Abort rendering of layout "{layout_name}": {str(e)}')
        finally:
            self.backend.finalize()

        self.view.end_loading(new_scene)
        self.view.buffer_scene_rect()
        if fitFlg:
            self.view.fit_to_scene()
        self.view.setScene(new_scene)

    def _on_mouse_moved(self, mouse_pos: QtCore.QPointF):
        self.statusLabel.setText(f'mouse position: {mouse_pos.x():.4f}, {mouse_pos.y():.4f}\n')


class SelectedInfo(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(SelectedInfo, self).__init__(parent)
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setReadOnly(True)
        self.setWidget(QtWidgets.QWidget())
        self.widget().setLayout(QtWidgets.QVBoxLayout())
        self.widget().layout().addWidget(self.text)
        self.setWindowTitle('Selected Info')

    def set_elements(self, elements, index):

        def _entity_attribs_string(dxf_entity, indent=''):
            text = ''
            for key, value in dxf_entity.dxf.all_existing_dxf_attribs().items():
                text += f'{indent}- {key}: {value}\n'
            return text

        if not elements:
             text = 'No element selected'
        else:
            text = f'Selected: {index + 1} / {len(elements)}    (click to cycle)\n'
            element = elements[index]
            dxf_entity = element.data(CorrespondingDXFEntity)
            if dxf_entity is None:
                text += 'No data'
            else:
                text += f'Selected Entity: {dxf_entity}\nLayer: {dxf_entity.dxf.layer}\n\nDXF Attributes:\n'
                text += _entity_attribs_string(dxf_entity)

                dxf_parent_stack = element.data(CorrespondingDXFParentStack)
                if dxf_parent_stack:
                    text += '\nParents:\n'
                    for entity in reversed(dxf_parent_stack):
                        text += f'- {entity}\n'
                        text += _entity_attribs_string(entity, indent='    ')

        self.text.setPlainText(text)

class Layers(QtWidgets.QDockWidget):
    updated_signal = QtCore.pyqtSignal(list)
    updatedFit_signal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(Layers, self).__init__(parent)

        self.visible_names = None

        self.model = QtGui.QStandardItemModel()
        self.view = QtWidgets.QListView()
        self.view.setModel(self.model)
        self.view.setStyleSheet('QListWidget {font-size: 12pt;} QCheckBox {font-size: 12pt; padding-left: 5px;}')
        #
        self.setWidget(QtWidgets.QWidget())
        self.widget().setLayout(QtWidgets.QVBoxLayout())
        # ------------ jump機能追加
        vPanButton = self.createButton("PAN", self.vPan)
        self.vTextBox = QLineEdit(self)
        #
        jumpLayout = QHBoxLayout()
        jumpLayout.addWidget(vPanButton)
        jumpLayout.addWidget(self.vTextBox)
        # ------------ 機能ボタン追加
        sClearButton = self.createButton("Off", self.sClear)
        sAllButton = self.createButton("On", self.sAll)
        sRedroawButton = self.createButton("再描画", self.sRedroaw)
        sViewAllButton = self.createButton("全体", self.sViewAll)
        #
        layerBLayout = QHBoxLayout()
        layerBLayout.addWidget(sAllButton)
        layerBLayout.addWidget(sClearButton)
        layerBLayout.addStretch()
        layerBLayout.addWidget(sRedroawButton)
        layerBLayout.addWidget(sViewAllButton)
        # ---------------------------------
        self.sAutoRedraw = QCheckBox("自動再描画")
        self.sOneLayer = QCheckBox("１レイヤー")
        #
        checkBLayout = QHBoxLayout()
        checkBLayout.addWidget(self.sAutoRedraw)
        checkBLayout.addWidget(self.sOneLayer)
        # ---------------------------------
        self.widget().layout().addLayout(jumpLayout)
        self.widget().layout().addLayout(layerBLayout)
        self.widget().layout().addLayout(checkBLayout)
        # ---------------------------------
        self.widget().layout().addWidget(self.view)
        self.setWindowTitle('Layers')
        #  チェックon/offイベント
        self.model.dataChanged.connect(self.layersChecked)
        #  クリックイベント
        self.view.clicked.connect(self.layerClicked)

    def createButton(self, text, member):
        button = QPushButton(text)
        button.clicked.connect(member)
        return button
    # ----------------------------------------------------
    #    view機能 button
    # ----------------------------------------------------
    def vPan(self):
        str = self.vTextBox.text()
        print(f"PAN実行: {str}")
        strNom = str.replace('(','').replace(')','')
        strPos = strNom.split(',')
        if len(strPos)==2:
            x = float(strPos[0])
            y = float(strPos[1])
            window.view.centerOn(x,y)


    # ----------------------------------------------------
    #    レイヤー選択関連機能 button
    # ----------------------------------------------------
    def sClear(self):
        print("選択クリアー実行")
        self.visible_names = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
        #
        if self.sAutoRedraw.isChecked():
            self.updated_signal.emit(self.visible_names)

    def sAll(self):
        print("全選択実行")
        self.visible_names = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            item.setCheckState(QtCore.Qt.Checked)
            self.visible_names.append(item.text())
        if self.sAutoRedraw.isChecked():
            self.updated_signal.emit(self.visible_names)

    def sRedroaw(self):
        print("再描画実行")
        self.updated_signal.emit(self.visible_names)

    def sViewAll(self):
        print("全体描画実行")
        self.updatedFit_signal.emit(self.visible_names)

    # ----------------------------------------------------
    def populate_layer_list(self, layers):
        self.model.clear()
        for layer in layers:
            item = QtGui.QStandardItem(layer.layer)
            item.setData(layer)
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked if layer.is_visible else QtCore.Qt.Unchecked)
            text_color = '#FFFFFF' if is_dark_color(layer.color, 0.4) else '#000000'
            item.setForeground(QtGui.QBrush(QtGui.QColor(text_color)))
            item.setBackground(QtGui.QBrush(QtGui.QColor(layer.color)))
            self.model.appendRow(item)

    # --------------
    #  check on/offイベント
    def layersChecked(self):
        if self.sOneLayer.isChecked():
            return
        print(f"レイヤーチェックBOX選択実行")
        self.visible_names = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.checkState() == QtCore.Qt.Checked:
                self.visible_names.append(item.text())
        if self.sAutoRedraw.isChecked():
            self.updated_signal.emit(self.visible_names)

    # --------------
    #  list クリックイベント:1レイヤーのみ表示
    def layerClicked(self, idx):
        if self.sOneLayer.isChecked():
            onRow = idx.row()
            print(f"1行選択実行={onRow}")
            self.visible_names = []
            for row in range(self.model.rowCount()):
                item = self.model.item(row, 0)
                if row == onRow:
                    item.setCheckState(QtCore.Qt.Checked)
                    self.visible_names.append(item.text())
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
            #
            if self.sAutoRedraw.isChecked():
                self.updated_signal.emit(self.visible_names)

class LogView(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(LogView, self).__init__(parent)
        self.text = QtWidgets.QTextBrowser()
        self.setWidget(QtWidgets.QWidget())
        self.widget().setLayout(QtWidgets.QVBoxLayout())
        self.widget().layout().addWidget(self.text)
        self.setWindowTitle('Log')

    def append(self, text):
        self.text.append(text)

class MyFrontend(Frontend):
    log_view = None

    def log_message(self, message):
        self.log_view.append(message)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
