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

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def updateOutputDirectory(self, filePath):
        self.fwOutputDirectory.setDefaultRoot(filePath)
        QgsSettings().setValue("qconsolidate/lastDirectory", os.path.dirname(filePath))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(filePath != "")

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        QDialog.accept()
