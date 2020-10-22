# -*- coding: utf-8 -*-
from maya import cmds
from PySide2.QtWidgets import *
from PySide2.QtGui import *  
from PySide2.QtCore import * 
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance
from maya import OpenMayaUI

clipboard = QApplication.clipboard() 
#-------------------------------------------------------
# Base
#-------------------------------------------------------
def baseWindow():
    mainWindow = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindow), QWidget)
#-------------------------------------------------------
# " "内にsetting.iniを含めたパスを入れる
# 例 path = "C:\Program Files\PyWorks\saveAttr\setting.ini"
#-------------------------------------------------------    
path = " "
setting = QSettings(path, QSettings.IniFormat)  
#-------------------------------------------------------
# Main
#-------------------------------------------------------         
class Gui(QDialog):
    
    def __init__(self, parent=baseWindow()):
        super(Gui, self).__init__(parent)
        self.design()
        self.load()

    def design(self):
        self.setWindowFlags(Qt.Dialog|Qt.WindowCloseButtonHint)
        self.setWindowTitle("Save Attribute ver1.0")
        self.setMinimumWidth(400)
        self.itemLabel = QLabel("Name")
        self.itemEdit = QLineEdit()
        self.itemList = QTreeWidget()
        self.removeButton = QPushButton("Remove")
        self.clearButton = QPushButton("Clear")
        headerName = ["Item", "Attribute", "Value"]
        self.itemList.setColumnCount(len(headerName))
        self.itemList.setHeaderLabels(headerName)
        # レイアウト
        upperLayout = QHBoxLayout()
        upperLayout.addWidget(self.itemLabel)
        upperLayout.addWidget(self.itemEdit)
        lowerLayout = QHBoxLayout()
        lowerLayout.addWidget(self.clearButton)
        lowerLayout.addWidget(self.removeButton)
        outputLayout = QVBoxLayout(self)
        outputLayout.addLayout(upperLayout)
        outputLayout.addWidget(self.itemList)
        outputLayout.addLayout(lowerLayout)
        # ウィジェットと関数を接続
        self.itemEdit.returnPressed.connect(self.addItem)
        self.removeButton.clicked.connect(self.removeItem)
        self.clearButton.clicked.connect(self.clearItem)
        self.itemList.itemDoubleClicked.connect(self.copy)
        
    def addItem(self):
        selection = mel.eval("$temp=$gChannelBoxName;")
        # アトリビュートのショートネームを取得
        self.attrList = []
        for i in range(3):
            if i == 0:
                self.attrList.append(cmds.channelBox(selection, q=True, sma=True))
            
            elif i == 1:
                self.attrList.append(cmds.channelBox(selection, q=True, ssa=True))
            
            elif i == 2:
                self.attrList.append(cmds.channelBox(selection, q=True, sha=True))
        
        # オブジェクトを取得
        if not self.attrList[0] == None:
            self.nodeList = cmds.channelBox(selection, q=True, mol=True)
        
        elif not self.attrList[1] == None:
            self.nodeList = cmds.channelBox(selection, q=True, sol=True)
        
        elif not self.attrList[2] == None:
            self.nodeList = cmds.channelBox(selection, q=True, hol=True)
            
        # リストからNoneを削除   
        self.attrList = [item for item in self.attrList if item][0]
        
        # アトリビュートのショートネームをロングネームに変換
        try:
            self.attrList = [cmds.attributeName("{}.{}".format(self.nodeList[0], 
            self.attrList[i]), l=True) for i in range(len(self.attrList))]
        
        except:
            pass

        # アトリビュートの値を取得   
        self.valueList = []
        for i in range(len(self.attrList)):
            self.valueList.append(cmds.getAttr("{}.{}".format(self.nodeList[0], self.attrList[i])))
        
        # ウィジェットに表示
        parentItem = QTreeWidgetItem([self.itemEdit.text()])
        self.itemList.addTopLevelItem(parentItem)
        for i in range(len(self.attrList)):
            childItem = QTreeWidgetItem(parentItem, ["", self.attrList[i], str(self.valueList[i])])

        # iniファイルに書き込み
        setting.beginGroup(self.itemEdit.text())
        setting.setValue("Attribute", self.attrList)
        setting.setValue("Value", self.valueList)
        setting.endGroup()
        
    def removeItem(self):
        try:
            # iniファイルから削除
            selectedItem = self.itemList.currentItem()
            value = selectedItem.text(0)
            setting.remove(value)
            
            # ウィジェットから削除
            item = str(self.itemList.currentIndex())
            index = item.split("(")[1].split(",")
            self.itemList.takeTopLevelItem(int(index[0])) 
        
        except:
            print("Item not selected"),
    
    def clearItem(self):
        # iniファイルから削除
        setting.clear()
        # ウィジェットから削除
        self.itemList.clear()

    def load(self):
        try:
            # iniファイルを開く
            with open(path) as f:
                lines = f.readlines()
            
            # グループごとに読み込み
            strip = [line.strip() for line in lines]
            groupName = [line for line in strip if line.startswith('[')]
    
            # ウィジェットに表示
            self.parentItem = []
            for i in range(len(groupName)):
                itemName = groupName[i].replace("[", "").replace("]", "")
                self.parentItem.append(QTreeWidgetItem([itemName]))
                self.itemList.addTopLevelItem(self.parentItem[i])
                
                for j in range(len(setting.value("{}/Attribute".format(itemName)))):
                    childItem = QTreeWidgetItem(self.parentItem[i], ["", 
                    setting.value("{}/Attribute".format(itemName))[j], 
                    str(setting.value("{}/Value".format(itemName))[j])])
        
        except:
            print("Please set the path or clear the item"),

    def copy(self): 
        # クリップボードにコピー
        selectedItem = self.itemList.currentItem()
        value = selectedItem.text(2)
        clipboard.setText(value)
        print("Copy"),
       
#-------------------------------------------------------
# Show
#-------------------------------------------------------  
def main():
    
    G = Gui()
    G.show()
    
if __name__ == '__main__':
    
    G = Gui()
    G.show()