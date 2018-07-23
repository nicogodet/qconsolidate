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
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMessageBox

from qgis.core import QgsSettings
from qgis.gui import QgsGui, QgsFileWidget

from qconsolidate.writers import writersRegistry

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(os.path.join(pluginPath, 'ui', 'qconsolidatedialogbase.ui'))


class QConsolidateDialog(BASE, WIDGET):
    def __init__(self, parent=None):
        super(QConsolidateDialog, self).__init__(parent)
        self.setupUi(self)

        QgsGui.instance().enableAutoGeometryRestore(self)

        settings = QgsSettings()
        self.fwOutputDirectory.setStorageMode(QgsFileWidget.GetDirectory)
        self.fwOutputDirectory.setDialogTitle(self.tr('Select directory'))
        self.fwOutputDirectory.setDefaultRoot(settings.value('qconsolidate/lastOutputDirectory', os.path.expanduser('~'), str))
        self.fwOutputDirectory.fileChanged.connect(self.updateOutputDirectory)

        for writer in sorted(writersRegistry.keys()):
            self.cmbWriter.addItem(writersRegistry[writer].displayName(), writer)
            self.stackedWidget.addWidget(writersRegistry[writer].widget())

        writer = QgsSettings().value('qconsolidate/writer', 'copydirectory', str)
        idx = self.cmbWriter.findData(writer)
        self.cmbWriter.setCurrentIndex(idx)
        self.stackedWidget.setCurrentIndex(idx)
        self.cmbWriter.currentIndexChanged.connect(self.writerChanged)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def updateOutputDirectory(self, filePath):
        self.fwOutputDirectory.setDefaultRoot(filePath)
        QgsSettings().setValue('qconsolidate/lastOutputDirectory', os.path.dirname(filePath))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(filePath != '')

    def writerChanged(self, index):
        self.stackedWidget.setCurrentIndex(index)

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        if os.path.isdir(os.path.join(self.fwOutputDirectory.filePath(), 'layers')):
            res = QMessageBox.question(self,
                                       self.tr('Directory exists'),
                                       self.tr('Destination directory already has "layers" subdirectory. '
                                               'Probably it already contains data from another project. Continue?'),
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No
                                         )
            if res != QMessageBox.Yes:
                return

        self._saveSettings()
        QDialog.accept(self)

    def _saveSettings(self):
        settings = QgsSettings()
        settings.setValue('qconsolidate/writer', self.cmbWriter.currentData())

    def task(self):
        settings = dict()
        settings['output'] = self.fwOutputDirectory.filePath()
        settings['exportRemote'] = self.chkExportRemote.isChecked()

        widget = self.stackedWidget.currentWidget()
        if hasattr(widget, 'settings'):
            settings.update(widget.settings())

        task = writersRegistry[self.cmbWriter.currentData()].task(settings)
        return task
