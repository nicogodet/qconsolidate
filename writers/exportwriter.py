# -*- coding: utf-8 -*-

"""
***************************************************************************
    exportwriter.py
    ---------------------
    Date                 : July 2018
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
__date__ = 'July 2018'
__copyright__ = '(C) 2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import Qgis, QgsMessageLog, QgsDataSourceUri

from qconsolidate.writers.directorywriter import (DirectoryWriter,
                                                  DirectoryWriterTask
                                                 )


class ExportWriter(DirectoryWriter):

    def __init__(self):
        super(ExportWriter, self).__init__()

    def name(self):
        return 'exportdirectory'

    def displayName(self):
        return self.tr('Export to directory')

    def task(self, settings):
        return ExportWriterTask(settings)


class ExportWriterTask(DirectoryWriterTask):

    def __init__(self, settings):
        super(ExportWriterTask, self).__init__(settings)

        self.baseDirectory = self.settings['output']

    def consolidateVectorLayer(self, layer):
        safeLayerName = self._safeName(layer.name())

        destDirectory = self.LAYERS_DIR_NAME
        if 'groupLayers' in self.settings and self.settings['groupLayers']:
            destDirectory = os.path.join(self.LAYERS_DIR_NAME, *self._layerTreePath(layer))
            newPath = os.path.join(self.baseDirectory, destDirectory)
            if not os.path.isdir(newPath):
                os.makedirs(newPath)

        newFile = os.path.join(self.baseDirectory, destDirectory, safeLayerName)

        providerType = layer.providerType()
        if providerType in ('ogr', 'memory', 'gpx', 'delimitedtext', 'spatialite'):
            self._exportVectorLayer(layer, newFile, 'ogr')
            self._exportLayerStyle(layer, newFile)
        elif providerType in ('DB2', 'mssql', 'oracle', 'postgres', 'wfs'):
            if 'exportRemote' in self.settings and self.settings['exportRemote']:
                self._exportVectorLayer(layer, newFile, 'ogr')
                self._exportLayerStyle(layer, newFile)
        else:
            QgsMessageLog.logMessage(self.tr('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType)), 'QConsolidate', Qgis.Info)

    def consolidateRasterLayer(self, layer):
        safeLayerName = self._safeName(layer.name())

        destDirectory = self.LAYERS_DIR_NAME
        if 'groupLayers' in self.settings and self.settings['groupLayers']:
            destDirectory = os.path.join(self.LAYERS_DIR_NAME, *self._layerTreePath(layer))
            newPath = os.path.join(self.baseDirectory, destDirectory)
            if not os.path.isdir(newPath):
                os.makedirs(newPath)

        newFile = os.path.join(self.baseDirectory, destDirectory, safeLayerName)

        providerType = layer.providerType()
        if providerType == 'gdal':
            self._exportRasterLayer(layer, newFile)
            self._exportLayerStyle(layer, newFile)
        elif providerType in ('wms'):
            if 'exportRemote' in self.settings and self.settings['exportRemote']:
                self._exportRasterLayer(layer, newFile, 'gdal')
                self._exportLayerStyle(layer, newFile)
        else:
            QgsMessageLog.logMessage(self.tr('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType)), 'QConsolidate', Qgis.Info)
