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

from qgis.core import Qgis, QgsMessageLog, QgsDataSourceUri

from qconsolidate.writers.directorywriter import DirectoryWriter, DirectoryWriterTask


class CopyWriter(DirectoryWriter):

    def __init__(self):
        super(CopyWriter, self).__init__()

    def name(self):
        return 'copydirectory'

    def displayName(self):
        return 'Copy to directory'

    def task(self, settings):
        return CopyWriterTask(settings)


class CopyWriterTask(DirectoryWriterTask):

    def __init__(self, settings):
        super(CopyWriterTask, self).__init__(settings)

        self.baseDirectory = self.settings['output']

    def packageVectorLayer(self, layer):
        safeLayerName = self._safeName(layer.name())

        destDirectory = self.LAYERS_DIR_NAME
        if 'groupLayers' in self.settings and self.settings['groupLayers']:
            destDirectory = os.path.join(self.LAYERS_DIR_NAME, *self._layerTreePath(layer))
            newPath = os.path.join(self.baseDirectory, destDirectory)
            if not os.path.isdir(newPath):
                os.makedirs(newPath)

        providerType = layer.providerType()
        if providerType == 'ogr':
            QgsMessageLog.logMessage(layer.name(), 'QConsolidate', Qgis.Info)
            QgsMessageLog.logMessage(layer.source(), 'QConsolidate', Qgis.Info)
            self._processGdalDatasource(layer, destDirectory)
        #~ elif providerType == 'memory':
            #~ newFile = './{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=safeLayerName)
            #~ self._exportVectorLayer(layer, newFile)
        #~ elif providerType in ('gpx', 'delimitedtext'):
            #~ filePath, layerPath = self._filePathFromUri(layer.source())
            #~ self._copyLayerFiles(filePath, self.dstDirectory)
            #~ newFile = './{dirName}/{fileName}?{layer}'.format(dirName=self.LAYERS_DIRECTORY, fileName=os.path.split(filePath)[1], layer=layerPath)
            #~ self._updateLayerSource(layer.id(), newFile)
        #~ elif providerType == 'spatialite':
            #~ uri = QgsDataSourceUri(layer.source())
            #~ filePath = uri.database()
            #~ self._copyLayerFiles(filePath, self.dstDirectory)
            #~ uri.setDatabase('./{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=os.path.split(filePath)[1]))
            #~ self._updateLayerSource(layer.id(), uri.uri())
        #~ elif providerType in ('DB2', 'mssql', 'oracle', 'postgres', 'wfs'):
            #~ if 'exportRemote' in self.settings and self.settings['exportRemote']:
                #~ newFile = './{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=safeLayerName)
                #~ self._exportVectorLayer(layer, newFile)
        else:
            QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType), 'QConsolidate')

    def packageRasterLayer(self, layer):
        pass
        #~ providerType = layer.providerType()
        #~ if providerType == 'gdal':
            #~ self._processGdalDatasource(layer)
        #~ elif providerType in 'wms':
            #~ if 'exportRemote' in self.settings and self.settings['exportRemote']:
                #~ newFile = './{dirName}/{fileName}'.format(dirName=self.LAYERS_DIRECTORY, fileName=safeLayerName)
                #~ self._exportRasterLayer(layer, newFile)
        #~ else:
            #~ QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType), 'QConsolidate')

    def _processGdalDatasource(self, layer, destDirectory):
        uri = layer.source()
        filePath = layer.source()
        newLayerSource = './{dirName}/{fileName}'.format(dirName=destDirectory, fileName=os.path.split(filePath)[1])
        if uri.startswith(('/vsizip/', '/vsigzip/', '/vsitar/')):
            m = self.gdalVsi.search(uri)
            if m is not None:
                prefix = m.group(1)
                filePath = m.group(2)
                layerPath = m.group(4)
                newLayerSource = '{vsi}./{dirName}/{fileName}/{layer}'.format(vsi=prefix, dirName=destDirectory, fileName=os.path.split(filePath)[1], layer=layerPath)
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
                newLayerSource = './{dirName}/{fileName}|{layer}'.format(dirName=destDirectory, fileName=os.path.split(filePath)[1], layer=layerPath)

        self._copyLayerFiles(filePath, os.path.join(self.baseDirectory, destDirectory))
        self._updateLayerSource(layer.id(), newLayerSource)
