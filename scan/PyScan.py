#!/usr/bin/python


from lib.util.datatype import AttribDict
from lib.util.db import summary2detail, insertDB, exportDB

from contextlib import contextmanager
import os,sys
from copy import deepcopy
from queue import Queue
from uuid import uuid1

import importlib.util
import random
import json
import traceback
import logging

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PyQt5.uic import loadUiType

current_directory =  os.path.dirname(os.path.abspath(__file__))

class ScanSignals(QObject):
    
    finished = pyqtSignal()
    result = pyqtSignal(AttribDict)
    
    targetchanged = pyqtSignal(str,str)
    statuschanged = pyqtSignal(bool)

    error = pyqtSignal(tuple)


class ScanWorker(QRunnable):

    def __init__(self,fn,host):
        QThread.__init__(self)

        self.single_scan_target = AttribDict()
        self.single_scan_target.target = host
        self.single_scan_target.plugin = fn
        # self.single_scan_target.result = {}

        self._status = False   # run status
        self.signals = ScanSignals()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        if new_status != self._status:
            self._status = new_status
            self.signals.statuschanged.emit(new_status)

    def run(self):
        self.status = True

        try:
            self.single_scan_target.result = self.single_scan_target.plugin(
                self.single_scan_target.target)

        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(deepcopy(self.single_scan_target))
        finally:
            self.signals.finished.emit()

            self.status = False

scan_form, base_class = loadUiType(os.path.join(current_directory,'knife.ui'))
class ScanForm(QWidget, scan_form):
    def __init__(self):
        super(ScanForm, self).__init__()
        self.setupUi(self)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center()) # Center Display
        # self.targetsumary.itemClicked.connect(self.on_targetsumary_itemclicked)
        self.scanresults.itemClicked.connect(self.on_scanresults_itemclicked)
        self.b_id = ""

        self._plugins =  set()  # Keep a set of loaded plugins(no duplicate modules)
        self._scan_threadpool = QThreadPool()


    def onScanStatusChanged(self,status):
        if status==True:
            self.scan.setText("Stop")
        else:
            self.scan.setText("Start")

    @pyqtSlot()
    def on_addscan_clicked(self):
        if self.hosts.text() == "":
            line = ""
        if self.hosts.text() != "" and self.ports.text() != "":
            line = self.hosts.text() + ":" + self.ports.text()
        if self.hosts.text() != "" and self.ports.text() == "":
            line = self.hosts.text()
        # if net range, just compute it and add it to scan item
        try:
            if line != "" and not self.existsitem(line, self.scanlists):
                self.scanlists.addItem(line)
                self.status.setText("Hosts Add Successful")
                self.status.setStyleSheet('color: green')
            else:
                self.status.setText("Hosts Already Add")
                self.status.setStyleSheet('color: red')
        except Exception as e:
            print(e)
            pass

        self.lcddisplay()

    def onScanIpChanged(self,scan_target):
        self.status.setText("  Now Scan:\t"+scan_target)
        self.status.setStyleSheet('color: red')
        
    def onOneScanFinished(self, scan_target):
        
        if scan_target.result['Exist']:
            self.scanresults.addItem(scan_target.target)
            u_id = str(uuid1())
            s_id = str(uuid1())

            scan_target.b_id = self.b_id
            scan_target.u_id = u_id
            scan_target.s_id = s_id

            insertDB(scan_target)
        
            self.targetsumary.setText(scan_target.result['Summary'])

    @pyqtSlot()
    def on_scan_clicked(self):
        
        iplists = []

        self.removeListWidgets(self.scanresults)
        self.targetsumary.setText("Scan Target Summary")
        
        selected_plugins = [item.text() for item in self.pluginlists.selectedItems()]
        modulelists = [plugin for plugin in self._plugins if plugin.__name__ in selected_plugins]

        if self.hosts.text() != "":
            iplists = [self.hosts.text()]


        if not iplists:
            iplists = [item.text() for item in self.scanlists.selectedItems()]
            # iplists = [self.scanlists.item(i).text() for i in range(self.scanlists.count())]

        if iplists and modulelists:
            # Current Scan Batch
            self.b_id = str(uuid1())

            for ip in iplists:
                scan_worker = ScanWorker(modulelists[0].poc,ip)
                scan_worker.signals.targetchanged.connect(self.onScanIpChanged)
                scan_worker.signals.result.connect(self.onOneScanFinished)
                scan_worker.signals.statuschanged.connect(self.onScanStatusChanged)
                self._scan_threadpool.start(scan_worker)

        else:
            self.status.setText("Select Target And Pulgin")
            self.status.setStyleSheet('color: red')
        
        self.lcddisplay()


    @pyqtSlot()
    def on_removescan_clicked(self):
        
        self.removeListWidgets(self.scanlists)
        # self.removeListWidgets(self.pluginlists)
        self.removeListWidgets(self.scanresults)
        # self.removeListWidgets(self.targetsumary)

        self.lcddisplay()

    @pyqtSlot()
    def on_loadipfile_clicked(self):
        fileName = self.setOpenFileName()
        try:
            with open(fileName) as f:
                for ip in f.readlines():
                    self.scanlists.addItem(ip.strip())            

        except Exception as e:
            print("on_loadipfile_clicked: " ,e)
            pass

        self.lcddisplay()

    # @pyqtSlot()
    # def on_targetsumary_itemclicked(self):
    #     try:
    #         self.targetdetails.setText(self.targetsumary.currentItem().text())
    #     except  Exception as e:
    #         print(e)
    #         pass

    @pyqtSlot()
    def on_scanresults_itemclicked(self):
        try:

            s_item = self.scanresults.currentItem().text()
            summary, detail = summary2detail(s_item)
            self.targetsumary.setText(summary)
            self.targetdetails.setText(detail)

        except  Exception as e:
            print("on_scanresults_itemclicked: " , e)
            pass


    @pyqtSlot()
    def on_loadplugins_clicked(self):
        plugin_dir = os.path.join(current_directory,"plugins")
        if os.path.exists(plugin_dir):
            plugin_files = [f for f in os.listdir(plugin_dir) if f.endswith(".py")]
            if plugin_files:
                
                for file_name in plugin_files:
                    file_abspath = os.path.join(plugin_dir,file_name)
                    spec = importlib.util.spec_from_file_location(file_name[:-3],file_abspath)
                    if spec is not None:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        if hasattr(module, "poc") and not self.existsitem(module.__name__, self.pluginlists):
                            self._plugins.add(module)
                            self.pluginlists.addItem(module.__name__)
                        else:
                            pass
            else:
                self.status.setText("Please Make Sure Your Plugin is end with py")
                self.status.setStyleSheet('color: red')
            
            self.lcddisplay()

    @pyqtSlot()
    def on_exportresult_clicked(self):
        try:
            if self.exportpath.text() != "":
                fileName = self.exportpath.text()
            else:
                fileName = self.setSaveFileName()

            exportDB(self.b_id, fileName)
            # with open(fileName+'.res', 'a') as f:
            #     for i in range(self.targetsumary.count()):
            #         res = str(self.targetsumary.item(i).text())

            #         f.writelines(res+'\n')

            self.status.setText("Export to file done")

        except Exception as e:
            print("on_exportresult_clicked: " , e)
            pass

    # Summary selected show details
    def setOpenFileName(self):
        options = QFileDialog.Options()
        try:
            fileName, _ = QFileDialog.getOpenFileName(self,
                                                    "Load Ip File", self.status.text(),
                                                    "All Files (*);;Text Files (*.txt)", options=options)
            if fileName:
                self.status.setText("Loading Ip File From:"+ fileName)
                return fileName

        except Exception as e:
            print("setOpenFileName: " , e)
            pass

    def setSaveFileName(self):    
        options = QFileDialog.Options()
        try:
            fileName, _ = QFileDialog.getSaveFileName(self,
                                                   "  Save Scan Results To File", self.status.text(),
                                                   "All Files (*);;Text Files (*.txt)", options=options)
            if fileName:
                self.status.setText("Saveing File To :" + fileName)
                return fileName

        except Exception as e :
            print("setSaveFileNameL ", e)
            pass


    def lcddisplay(self):
        self.hostscount.display(self.scanlists.count())
        self.pluginscount.display(self.pluginlists.count())
        self.resultscount.display(self.scanresults.count())
        
    def removeListWidgets(self, listwidgets):
        try:

            tmplists = listwidgets.selectedItems()
            if tmplists:
                for item in tmplists:
                    item = listwidgets.takeItem(listwidgets.row(item))
                    self.status.setText(
                        listwidgets.objectName() + " Remove:" + item.text())
                    item = None
            else:
                return
        except Exception as e:
            print("removeListWidgets: " , e)
            pass

    def showresults(self, flag, result):
        pass

    def checkIp(self,ip):
        pass

    def checkPath(self,path):
        pass

    def existsitem(self,item,listwidgets):
        """
            if uniqueitem is true
        """
        exists = listwidgets.findItems(item, Qt.MatchExactly)
        if exists:
            return True
        else:
            return False


    # def updateitem(self,item,listwidgets):
    #         """
    #         if uniqueitem is true
    #     """
    #     exists = listwidgets.findItems(item, Qt.MatchExactly)
    #     if exists:
    #         listwidgets.
    #     else:
    #         return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    scanform = ScanForm()
    scanform.show()
    sys.exit(app.exec_())
