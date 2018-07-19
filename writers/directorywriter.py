# -*- coding: utf-8 -*-

"""
***************************************************************************
    dicrectorywriter.py
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
import glob
import shutil

from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsVectorFileWriter, QgsRasterPipe, QgsRasterFileWriter

from qconsolidate.writers.writerbase import WriterBase, WriterTaskBase
from qconsolidate.gui.directorywriterwidget import DirectoryWriterWidget


class DirectoryWriter(WriterBase):

    def __init__(self):
        super(DirectoryWriter, self).__init__()

    def name(self):
        return 'directory'

    def displayName(self):
        return 'Directory'

    def widget(self):
        return DirectoryWriterWidget()

    def task(self, settings):
        return DirectoryWriterTask(settings)


class DirectoryWriterTask(WriterTaskBase):

    def __init__(self, settings):
        super(DirectoryWriterTask, self).__init__(settings)

    def packagePluginLayer(self, layer):
        QgsMessageLog.logMessage('Layers from the "{provider}" provider are currently not supported.'.format(provider=layer.providerType()), 'QConsolidate')

    def _filePathFromUri(self, uri):
        filePath = uri.split('?')[0]
        layerPath = uri.split('?')[1]
        if os.name == 'nt':
            # on Windows strip 'file:///' prefix from the path
            # FIXME: need to handle special case — LAN URI
            return filePath[8:] if filePath.startswith('file://') else filePath, layerPath
        else:
            # on Linux strip 'file://' prefix from the path
            return filePath[7:] if filePath.startswith('file://') else filePath, layerPath

    def _copyLayerFiles(self, layerPath, destDirectory):
        ''' Copy all files that belongs to the layer to the given directory
        '''
        wildcard = '{}.*'.format(os.path.splitext(layerPath)[0])
        for fileName in glob.iglob(wildcard):
            shutil.copy2(fileName, destDirectory)

    def _exportVectorLayer(self, layer, fileName):
        ''' Export given vector layer to the file using given format
        '''
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = self.settings['vectorFormat'] if 'vectorFormat' in self.settings else 'GPKG'
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        options.fileEncoding = 'utf-8'

        if os.path.splitext(fileName)[1] == '':
            formats = QgsVectorFileWriter.supportedFiltersAndFormats()
            for f in formats:
                if f.driverName == options.driverName and len(f.globs) > 0:
                    fileName = '{}.{}'.format(fileName, f.globs[0][:2])

        error = QgsVectorFileWriter.writeAsVectorFormat(layer, fileName, options)
        if error != QgsVectorFileWriter.NoError:
            QgsMessageLog.logMessage('Failed to process layer "{layer}": {message}.'.format(layer=layer.name(), message=error), 'QConsolidate')
        else:
            self._updateLayerSource(layer.id(), fileName)

    def _exportRasterLayer(self, layer, fileName):
        ''' Export given raster layer to the file
        '''
        provider = layer.dataProvider()
        k = float(provider.extent().width()) / float(provider.extent().height())

        pipe = QgsRasterPipe()
        if not pipe.set(provider.clone()):
            QgsMessageLog.logMessage('Failed to process layer "{layer}": Cannot set pipe provider.'.format(layer=layer.name()), 'QConsolidate')
            return

        if os.path.splitext(fileName)[1] == '':
            formats = QgsRasterFileWriter.extensionsForFormat('GTiff')
            if len(formats) > 0:
                fileName = '{}.{}'.format(fileName, formats[0])

        writer = QgsRasterFileWriter(fileName)
        writer.setOutputFormat('GTiff')
        writer.writeRaster(pipe, RASTER_SIZE * k, RASTER_SIZE, provider.extent(), provider.crs())
        self._updateLayerSource(layer.id(), fileName.replace(self.baseDirectory, '.'))

    def _layerTreePath(self, layer):
        ''' Retrieve all parent layer tree groups of the given layer
        '''
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