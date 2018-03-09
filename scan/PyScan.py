#!/usr/bin/python


from lib.util.datatype import AttribDict

from contextlib import contextmanager
import os,sys
from copy import deepcopy
from queue import Queue

import importlib.util
import random

from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
from PyQt5.QtWidgets import QWidget,QListWidgetItem, QMessageBox
from PyQt5.QtWidgets import (QApplication, QCheckBox, QColorDialog, QDialog,
                             QErrorMessage, QFileDialog, QFontDialog, QFrame, QGridLayout,
                             QInputDialog, QLabel, QPushButton)
from PyQt5.uic import loadUiType

current_directory =  os.path.dirname(os.path.abspath(__file__))

class ScanThread(QThread):
    OneScanFinished = pyqtSignal(AttribDict)
    ScanIpChanged = pyqtSignal(str,str)
    ScanStatusChanged = pyqtSignal(bool)

    def __init__(self,scan_target):
        QThread.__init__(self)
        self.single_scan_target = AttribDict()
        self.single_scan_target.result = {}
        self._hosts = []
        self._plugins = []
        self._status = False   # run status

    def set_argument(self,iplists,modulelists):
        self._hosts = iplists
        self._plugins = modulelists

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self,new_status):
        if new_status!=self._status:
            self._status = new_status
            self.ScanStatusChanged.emit(new_status)

    def run(self):
        self.status = True
        for ip in self._hosts:
            for plugin in self._plugins:
                self.ScanIpChanged.emit(ip,plugin.__name__)
                if self._status:
                    try:
                        self.single_scan_target.host = ip
                        self.single_scan_target.result = plugin.poc(ip)
                        self.OneScanFinished.emit(deepcopy(self.single_scan_target))
                    except Exception as e:
                        self.OneScanFinished.emit(deepcopy(self.single_scan_target))
                        pass
        self.status = False


scan_form, base_class = loadUiType(os.path.join(current_directory,'knife.ui'))
class ScanForm(QWidget, scan_form):
    def __init__(self):
        super(ScanForm, self).__init__()
        self.setupUi(self)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center()) # Center Display
        self.targetsumary.itemClicked.connect(self.on_targetsumary_itemclicked)
        self.scanresults.itemClicked.connect(self.on_scanresults_itemclicked)



        self._plugins =  set()  # Keep a set of loaded plugins(no duplicate modules)
        self._scan_thread = ScanThread(self)
        self._scan_thread.ScanIpChanged.connect(self.onScanIpChanged)
        self._scan_thread.OneScanFinished.connect(self.onOneScanFinished)
        self._scan_thread.ScanStatusChanged.connect(self.onScanStatusChanged)

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
            self.scanresults.addItem(scan_target.host)
            self.targetsumary.addItem(scan_target.result['Summary'])

    @pyqtSlot()
    def on_scan_clicked(self):
        selected_plugins = [item.text() for item in self.pluginlists.selectedItems()]

        modulelists = [plugin for plugin in self._plugins if plugin.__name__ in selected_plugins]
        iplists = [item.text() for item in self.scanlists.selectedItems()]
        

        if self.hosts.text() != "":
            iplists = [self.hosts.text()]
            
        if iplists and modulelists:
            # scan_target = AttribDict()
            # scan_target.modulelists = modulelists
            # scan_target.iplists = iplists
            self._scan_thread.set_argument(iplists,modulelists)
            self._scan_thread.start()
        else:
            self.status.setText("Select Target And Pulgin")
            self.status.setStyleSheet('color: red')

    @pyqtSlot()
    def on_removescan_clicked(self):
        
        self.removeListWidgets(self.scanlists)
        self.removeListWidgets(self.pluginlists)
        self.removeListWidgets(self.scanresults)
        self.removeListWidgets(self.targetsumary)

        self.lcddisplay()

    @pyqtSlot()
    def on_loadipfile_clicked(self):
        fileName = self.setOpenFileName()
        try:
            with open(fileName) as f:
                for ip in f.readlines():
                    self.scanlists.addItem(ip.strip())            

        except Exception as e:
            print(e)
            pass

        self.lcddisplay()

    @pyqtSlot()
    def on_targetsumary_itemclicked(self):
        try:
            self.targetdetails.setText(self.targetsumary.currentItem().text())
        except  Exception as e:
            print(e)
            pass

    @pyqtSlot()
    def on_scanresults_itemclicked(self):
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
                fileName = self.setOpenFileName()

            with open(fileName+'.res', 'a') as f:
                for i in range(self.targetsumary.count()):
                    res = str(self.targetsumary.item(i).text())

                    f.writelines(res+'\n')

                self.status.setText("Export to file done")

        except Exception as e:
            print(e)
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
            print(e)
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
            print(e)
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
