
#!/usr/bin/python
# from ui_2015 import Ui_Addhost
from contextlib import contextmanager
import os,sys
# import threading
from queue import Queue

# import scan_worker
import importlib.util
import random

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QFileDialog,QMessageBox
from PyQt5.QtWidgets import (QCheckBox, QColorDialog, QDialog,
                             QErrorMessage, QFileDialog, QFontDialog, QFrame, QGridLayout,
                             QInputDialog, QLabel, QPushButton,QListWidgetItem)
from PyQt5.uic import loadUiType

current_directory =  os.path.dirname(os.path.abspath(__file__))

class ScanThread(QThread):
    OneScanFinished = pyqtSignal(str,str,tuple)
    ScanIpChanged = pyqtSignal(str,str)
    ScanStatusChanged = pyqtSignal(bool)

    def __init__(self,*args,**kwargs):
        QThread.__init__(self)
        self._hosts = []
        self._plugins = []
        self._status = False   # run status
        
    def set_argument(self,hosts,plugins):
        self._hosts = hosts
        self._plugins = plugins

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
                        result = plugin.poc(ip)
                        self.OneScanFinished.emit(ip,plugin.__name__,result)
                    except:
                        self.OneScanFinished.emit(ip,plugin.__name__,(False,"Exception Occurred"))
        self.status = False

scan_form, base_class = loadUiType('knife.ui')
class ScanForm(QWidget, scan_form):
    def __init__(self, *args):
        super(ScanForm, self).__init__(*args)
        self.setupUi(self)
        self.targetsumary.itemClicked.connect(self.on_targetsumary_itemclicked)
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
            if line != "":
                self.scanlists.addItem(line)
        except Exception as e:
            print(e)
            pass

        self.lcddisplay()

    def onScanIpChanged(self,*args,**kwargs):
        # update current scanning ip here
        print("onScanIpChanged:",args,kwargs)

    def onOneScanFinished(self,*args,**kwargs):
        # process scan result
        print("onOneScanFinished:",args,kwargs)

    @pyqtSlot()
    def on_scan_clicked(self):
        selected_plugins = [item.text() for item in self.pluginlists.selectedItems()]
        modulelists = [plugin for plugin in self._plugins if plugin.__name__ in selected_plugins]
        iplists = [ item.text() for item in self.scanlists.selectedItems()]
        if self.hosts.text() != "":
            iplists = [self.hosts.text()]
        if iplists and modulelists:
            self._scan_thread.set_argument(iplists,modulelists)
            self._scan_thread.start()


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
                        exists = self.pluginlists.findItems(
                            module.__name__, Qt.MatchExactly)
                        if hasattr(module, "poc") and not exists:
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

    def unique(self,listwidgets):
        pass    
        # for i in range(listwidgets.count()):
        #     print(listwidgets.item(i).text())

    # def scan_by(self):
        
    #     selecthosts = self.scanlists.selectedItems()

    #     scanhost = self.hosts.text()
    #     reshost = self.scanresults.findItems(scanhost, MatchContains)

    #     if scanhost != "" and reshost <= 0:
    #         print(reshost)
    #         return "host", scanhost
                        
    #     if selecthosts:
    #         for ip in selecthosts:
    #             ip = ip.text()
    #             uqueue.put(ip)

    #     else:
    #         for i in range(self.scanlists.count()):
    #             ip = str(self.scanlists.item(i).text())
    #             uqueue.put(ip)

    #     return "hosts", uqueue

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    scanform = ScanForm()
    scanform.show()
    sys.exit(app.exec_())
