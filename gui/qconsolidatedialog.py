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


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *

from qgis.core import *
from qgis.gui import *

import consolidatethread
from ui.ui_qconsolidatedialogbase import Ui_QConsolidateDialog


class QConsolidateDialog(QDialog, Ui_QConsolidateDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface

        self.workThread = None

        self.btnOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnClose = self.buttonBox.button(QDialogButtonBox.Close)

        self.btnBrowse.clicked.connect(self.setOutDirectory)

    def setOutDirectory(self):
        outDir = QFileDialog.getExistingDirectory(self,
                                                  self.tr("Select output directory"),
                                                  "."
                                                 )
        if not outDir:
            return

        self.leOutputDir.setText(outDir)

    def accept(self):
        outputDir = self.leOutputDir.text()
        if not outputDir:
            QMessageBox.warning(self,
                                self.tr("QConsolidate: Error"),
                                self.tr("Output directory is not set. Please specify output directory.")
                               )
            return

        # create directory for layers if not exists
        d = QDir(outputDir)
        if d.exists("layers"):
            res = QMessageBox.question(self,
                                       self.tr("Directory exists"),
                                       self.tr("Output directory already contains 'layers' subdirectory. " +
                                               "Maybe this directory was used to consolidate another project. Continue?"),
                                       QMessageBox.Yes | QMessageBox.No
                                      )
            if res == QMessageBox.No:
                return
        else:
            if not d.mkdir("layers"):
                QMessageBox.warning(self,
                                    self.tr("QConsolidate: Error"),
                                    self.tr("Can't create directory for layers.")
                                   )
                return

        # copy project file
        projectFile = QgsProject.instance().fileName()
        f = QFile(projectFile)
        newProjectFile = outputDir + "/" + QFileInfo(projectFile).fileName()
        f.copy(newProjectFile)

        # start consolidate thread that does all real work
        self.workThread = consolidatethread.ConsolidateThread(self.iface, outputDir, newProjectFile)
        self.workThread.rangeChanged.connect(self.setProgressRange)
        self.workThread.updateProgress.connect(self.updateProgress)
        self.workThread.processFinished.connect(self.processFinished)
        self.workThread.processInterrupted.connect(self.processInterrupted)
        self.workThread.processError.connect(self.processError)

        self.btnClose.setText(self.tr("Cancel"))
        self.buttonBox.rejected.disconnect(self.reject)
        self.btnClose.clicked.connect(self.stopProcessing)

        self.workThread.start()

    def reject(self):
        QDialog.reject(self)

    def setProgressRange(self, maxValue):
        self.progressBar.setRange(0, maxValue)
        self.progressBar.setValue(0)

    def updateProgress(self):
        self.progressBar.setValue(self.progressBar.value() + 1)

    def processFinished(self):
        self.stopProcessing()
        self.restoreGui()

    def processInterrupted(self):
        self.restoreGui()

    def processError(self, message):
        QMessageBox.warning(self,
                            self.tr("QConsolidate: Error"),
                            message
                           )
        self.restoreGui()
        return

    def stopProcessing(self):
        if self.workThread is not None:
            self.workThread.stop()
            self.workThread = None

    def restoreGui(self):
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)

        QApplication.restoreOverrideCursor()
        self.buttonBox.rejected.connect(self.reject)
        self.btnClose.setText(self.tr("Close"))
        self.btnOk.setEnabled(True)
