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

from qgis.core import Qgis, QgsProject, QgsMapLayer, QgsMessageLog, QgsVectorFileWriter, QgsDataSourceUri

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
            self._processGdalDatasource(layer)
        elif providerType == 'memory':
            newFile = './{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=safeLayerName)
            self._exportVectorLayer(layer, newFile)
        elif providerType in ('gpx', 'delimitedtext'):
            filePath, layerPath = self._filePathFromUri(layer.source())
            self._copyLayerFiles(filePath, self.dstDirectory)
            newFile = './{dirName}/{fileName}?{layer}'.format(dirName=self.LAYERS_DIRECTORY, fileName=os.path.split(filePath)[1], layer=layerPath)
            self._updateLayerSource(layer.id(), newFile)
        elif providerType == 'spatialite':
            uri = QgsDataSourceUri(layer.source())
            filePath = uri.database()
            self._copyLayerFiles(filePath, self.dstDirectory)
            uri.setDatabase('./{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=os.path.split(filePath)[1]))
            self._updateLayerSource(layer.id(), uri.uri())
        elif providerType in ('DB2', 'mssql', 'oracle', 'postgres', 'wfs'):
            if 'exportRemote' in self.settings and self.settings['exportRemote']:
                newFile = './{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=safeLayerName)
                self._exportVectorLayer(layer, newFile)
        else:
            QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType), 'QConsolidate')

    def packageRasterLayer(self, layer):
        providerType = layer.providerType()
        if providerType == 'gdal':
            self._processGdalDatasource(layer)
        elif providerType in 'wms':
            if 'exportRemote' in self.settings and self.settings['exportRemote']:
                newFile = './{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=safeLayerName)
                self._exportRasterLayer(layer, newFile)
        else:
            QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType), 'QConsolidate')

    def packagePluginLayer(self, layer):
        QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=layer.providerType()), 'QConsolidate')

    def _processGdalDatasource(self, layer):
        uri = layer.source()
        filePath = layer.source()
        newFile = './{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=os.path.split(filePath)[1])
        if uri.startswith(('/vsizip/', '/vsigzip/', '/vsitar/')):
            m = self.gdalVsi.search(uri)
            if m is not None:
                prefix = m.group(1)
                filePath = m.group(2)
                layerPath = m.group(4)
                newFile = '{vsi}./{dirName}/{fileName}/{layer}'.format(vsi=prefix, dirName=self.LAYERS_DIRECTORY, fileName=os.path.split(filePath)[1], layer=layerPath)
        else:
            # ignore other virtual filesystems
            if uri.startswith('/vsi'):
                prefix = uri.slit('/')[0]
                QgsMessageLog.logMessage('Not supported GDAL virtual filesystem layer "{layerType}"'.format(layerType=prefix), 'QConsolidate')
                return

            # handle multiple layers in the single dataset
            if '|' in uri:
                filePath = uri.split('|')[0]
                layerPath = uri.split('|')[1]
                newFile = './{dirName}/{fileName}|{layer}'.format(dirName=self.LAYERS_DIRECTORY, fileName=os.path.split(filePath)[1], layer=layerPath)

        self._copyLayerFiles(filePath, self.dstDirectory)
        self._updateLayerSource(layer.id(), newFile)

    def _layerTreePath(self, layer):
        groups = []
        root = QgsProject.instance().layerTreeRoot()
        node = root.findLayer(layer.id())
        while node.parent() is not None:
            groups.append(node.parent().name())
            node = node.parent()

        if len(groups) != 1:
            groups.reverse()
            groups = groups[1:]

        return groups
