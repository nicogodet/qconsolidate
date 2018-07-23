# -*- coding: utf-8 -*-

"""
***************************************************************************
    geopackagewriter.py
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

from osgeo import gdal

from qgis.core import (Qgis,
                       QgsMessageLog,
                       QgsProject,
                       QgsMapLayer,
                       QgsVectorFileWriter,
                       QgsRasterDataProvider,
                       QgsRasterPipe,
                       QgsRasterFileWriter
                      )

from qconsolidate.writers.writerbase import WriterBase, WriterTaskBase

RASTER_SIZE = 2000


class GeopackageWriter(WriterBase):

    def __init__(self):
        super(GeopackageWriter, self).__init__()

    def name(self):
        return 'geopackage'

    def displayName(self):
        return self.tr('GeoPackage')

    def task(self, settings):
        return GeopackageWriterTask(settings)


class GeopackageWriterTask(WriterTaskBase):

    def __init__(self, settings):
        super(GeopackageWriterTask, self).__init__(settings)

        self.baseDirectory = self.settings['output']
        self.filePath = os.path.join(self.baseDirectory, self.LAYERS_DIR_NAME, 'layers.gpkg')

    def prepare(self):
        gdal.AllRegister()
        driver = gdal.GetDriverByName('GPKG')
        if driver is None:
            self.error = self.tr('"GeoPackage" driver not found.')
            return False

        ds = driver.Create(self.filePath, 0, 0, 0)
        if ds is None:
            self.error = self.tr('Failed to create database: {message}'.format(gdal.GetLastErrorMsg()))
            return False

        ds = None

    def consolidateVectorLayer(self, layer):
        exportLayer = False

        providerType = layer.providerType()
        if providerType in ('ogr', 'memory', 'gpx', 'delimitedtext', 'spatialite', 'grass'):
            exportLayer = True
        elif providerType in ('DB2', 'mssql', 'oracle', 'postgres', 'wfs'):
            if 'exportRemote' in self.settings and self.settings['exportRemote']:
                exportLayer = True
        else:
            QgsMessageLog.logMessage(self.tr('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType)), 'QConsolidate', Qgis.Info)

        if exportLayer:
            tableName = self._safeName(layer.name())
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = 'GPKG'
            options.layerName = tableName
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
            options.fileEncoding = 'utf-8'

            error, msg = QgsVectorFileWriter.writeAsVectorFormat(layer, self.filePath, options)
            if error != QgsVectorFileWriter.NoError:
                QgsMessageLog.logMessage(self.tr('Failed to export layer "{layer}": {message}.'.format(layer=layer.name(), message=msg)), 'QConsolidate', Qgis.Warning)
            else:
                newSource = '{filePath}|layername={layer}'.format(filePath=self.filePath.replace(self.baseDirectory, '.'), layer=tableName)
                self._updateLayerSource(layer.id(), newSource, 'ogr')

    def packageRasterLayer(self, layer):
        exportLayer = False

        providerType = layer.providerType()
        if providerType in ('gdal', 'grass'):
            exportLayer = True
        elif providerType in ('wms'):
            if 'exportRemote' in self.settings and self.settings['exportRemote']:
                exportLayer = True
        else:
            QgsMessageLog.logMessage(self.tr('Layers from the "{provider}" provider are currently not supported.'.format(provider=providerType)), 'QConsolidate', Qgis.Info)

        if exportLayer:
            provider = layer.dataProvider()

            cols = provider.xSize()
            rows = provider.ySize()
            if not provider.capabilities() & QgsRasterDataProvider.Size:
                k = float(provider.extent().width()) / float(provider.extent().height())
                cols = RASTER_SIZE * k
                rows = RASTER_SIZE

            pipe = QgsRasterPipe()
            if not pipe.set(provider.clone()):
                QgsMessageLog.logMessage(self.tr('Failed to export layer "{layer}": Cannot set pipe provider.'.format(layer=layer.name())), 'QConsolidate', Qgis.Warning)
                return

            tableName = self._safeName(layer.name())
            writer = QgsRasterFileWriter(self.filePath)
            writer.setOutputFormat('GPKG')
            writer.setCreateOptions(['APPEND_SUBDATASET=YES', 'RASTER_TABLE={table}'.format(table=tableName), ])

            error = writer.writeRaster(pipe, cols, rows, provider.extent(), provider.crs())
            if error != QgsRasterFileWriter.NoError:
                QgsMessageLog.logMessage(self.tr('Failed to export layer "{layer}": {message}.'.format(layer=layer.name(), message=error)), 'QConsolidate', Qgis.Warning)
            else:
                newSource = 'GPKG:{filePath}:{layer}'.format(filePath=self.filePath, layer=tableName)
                self._updateLayerSource(layer.id(), newSource, 'gdal')

    def consolidatePluginLayer(self, layer):
        QgsMessageLog.logMessage(self.tr('Plugin layers are currently not supported.', 'QConsolidate', Qgis.Info)

    def consolidateMeshLayer(self, layer):
        QgsMessageLog.logMessage(self.tr('Mesh layers are currently not supported.', 'QConsolidate', Qgis.Info)
