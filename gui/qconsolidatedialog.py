# -*- coding: utf-8 -*-

"""
***************************************************************************
    qconsolidatedialog.py
    ---------------------
    Date                 : February 2012
    Copyright            : (C) 2012-2018 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'February 2012'
__copyright__ = '(C) 2012-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

from qgis.core import QgsSettings
from qgis.gui import QgsGui, QgsFileWidget

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(os.path.join(pluginPath, "ui", "qconsolidatedialogbase.ui"))


class QConsolidateDialog(BASE, WIDGET):
    def __init__(self, parent=None):
        super(QConsolidateDialog, self).__init__(parent)
        self.setupUi(self)

        QgsGui.instance().enableAutoGeometryRestore(self)

        self.fwOutputDirectory.setStorageMode(QgsFileWidget.GetDirectory)
        self.fwOutputDirectory.setDialogTitle(self.tr("Select directory"))
        self.fwOutputDirectory.setDefaultRoot(QgsSettings().value("qconsolidat/lastDirectory", os.path.expanduser("~"), str))
        self.fwOutputDirectory.fileChanged.connect(self.updateOutputDirectory)

        self.btnOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnClose = self.buttonBox.button(QDialogButtonBox.Close)

    def updateOutputDirectory(self, dirPath):
        self.fwOutputDirectory.setDefaultRoot(dirPath)
        QgsSettings().setValue("qconsolidate/lastDirectory", os.path.dirname(dirPath))

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        self._saveSettings()

        dirName = self.fwOutputDirectory.filePath()
        if dirName == "":
            iface.messageBar().pushWarning(
                self.tr("Path is not set"),
                self.tr("Output directory is not set. Please specify output "
                        "directory and try again."))
            return

        #~ # create directory for layers if not exists
        #~ d = QDir(outputDir)
        #~ if d.exists("layers"):
            #~ res = QMessageBox.question(self,
                                       #~ self.tr("Directory exists"),
                                       #~ self.tr("Output directory already contains 'layers' subdirectory. " +
                                               #~ "Maybe this directory was used to consolidate another project. Continue?"),
                                       #~ QMessageBox.Yes | QMessageBox.No
                                      #~ )
            #~ if res == QMessageBox.No:
                #~ return
        #~ else:
            #~ if not d.mkdir("layers"):
                #~ QMessageBox.warning(self,
                                    #~ self.tr("QConsolidate: Error"),
                                    #~ self.tr("Can't create directory for layers.")
                                   #~ )
                #~ return

        #~ # copy project file
        #~ projectFile = QgsProject.instance().fileName()
        #~ f = QFile(projectFile)
        #~ newProjectFile = outputDir + "/" + QFileInfo(projectFile).fileName()
        #~ f.copy(newProjectFile)

        #~ # start consolidate thread that does all real work
        #~ self.workThread = consolidatethread.ConsolidateThread(self.iface, outputDir, newProjectFile)
        #~ self.workThread.rangeChanged.connect(self.setProgressRange)
        #~ self.workThread.updateProgress.connect(self.updateProgress)
        #~ self.workThread.processFinished.connect(self.processFinished)
        #~ self.workThread.processInterrupted.connect(self.processInterrupted)
        #~ self.workThread.processError.connect(self.processError)

        #~ self.btnClose.setText(self.tr("Cancel"))
        #~ self.buttonBox.rejected.disconnect(self.reject)
        #~ self.btnClose.clicked.connect(self.stopProcessing)

        #~ self.workThread.start()

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def logMessage(self, message, level=Qgis.Info):
        QgsMessageLog.logMessage(message, "QConsolidate", level)

    def _restoreGui(self):
        self.progressBar.setValue(0)
        self.btnOk.setEnabled(True)
        self.btnClose.setEnabled(True)
