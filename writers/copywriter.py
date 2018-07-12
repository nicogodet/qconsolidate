# -*- coding: utf-8 -*-

"""
***************************************************************************
    copywriter.py
    ---------------------
    Date                 : April 2018
    Copyright            : (C) 2018 by Alexander Bruy
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
__date__ = 'April 2018'
__copyright__ = '(C) 2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import shutil
import xml.etree.ElementTree as ET

from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget

from qgis.core import Qgis, QgsProject, QgsMapLayer, QgsMessageLog, QgsVectorFileWriter

from qconsolidate.writers.writerbase import WriterBase, WriterTaskBase
from qconsolidate.gui.directorywriterwidget import DirectoryWriterWidget


class CopyWriter(WriterBase):

    def name(self):
        return 'copydirectory'

    def displayName(self):
        return 'Copy to directory'

    def widget(self):
        return DirectoryWriterWidget()

    def task(self, settings):
        return CopyWriterTask(settings)


class CopyWriterTask(WriterTaskBase):

    def packageVectorLayer(self, layer):
        safeLayerName = self._safeName(layer.name())

        providerType = layer.providerType()
        if providerType == 'ogr':
            # FIXME: need to handle GDAL's vsizip
            pass
        elif providerType == 'memory':
            newFile = os.path.join(self.layersDirectory, safeLayerName)
            self._exportVectorLayer(layer, newFile)
        elif providerType in ('gpx', 'delimitedtext'):
            filePath = self._filePathFromUri(layer.source())
            self._copyLayerFiles(filePath, self.layersDirectory)
            newFile = os.path.join(self.layersDirectory, os.path.split(filePath)[1])
            self._updateLayerSource(layer.id(), newFile, filePath)
        elif providerType == 'spatialite':
            pass
        elif providerType in ('DB2', 'mssql', 'oracle', 'postgres', 'wfs'):
            if 'exportRemote' in self.settings and self.settings['exportRemote']:
                newFile = os.path.join(self.layersDirectory, safeLayerName)
                self._exportVectorLayer(layer, newFile)
        else:
            QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType), 'QConsolidate')

    def packageRasterLayer(self, layer):
        providerType = layer.providerType()
        if providerType == 'gdal':
            # FIXME: need to handle subdatasets
            self._copyLayerFiles(layer.source(), self.layersDirectory)
            newFile = os.path.join(self.layersDirectory, os.path.split(layer.source())[1])
            self._updateLayerSource(layer.id(), newFile)
        elif providerType == 'wms':
            if 'exportRemote' in self.settings and self.settings['exportRemote']:
                newFile = os.path.join(self.layersDirectory, safeLayerName)
                self._exportRasterLayer(layer, newFile)
        else:
            QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType), 'QConsolidate')

    def packagePluginLayer(self, layer):
        QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=layer.providerType()), 'QConsolidate')
