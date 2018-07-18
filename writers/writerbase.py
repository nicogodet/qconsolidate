# -*- coding: utf-8 -*-

"""
***************************************************************************
    writerbase.py
    ---------------------
    Date                 : March 2018
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
__date__ = 'March 2018'
__copyright__ = '(C) 2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import re
import shutil
import xml.etree.ElementTree as ET

from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget

from qgis.core import Qgis, QgsProject, QgsMapLayer, QgsMessageLog, QgsTask, QgsVectorFileWriter

RASTER_SIZE = 2000


class WriterBase:

    def __init__(self):
        pass

    def name(self):
        return 'base'

    def displayName(self):
        return 'Base'

    def widget(self):
        return QWidget()

    def task(self, settings):
        return WriterTaskBase(settings)


class WriterTaskBase(QgsTask):

    consolidateComplete = pyqtSignal()
    errorOccurred = pyqtSignal(str)

    badChars = re.compile(r'[&:\(\)\-\,\'\.\/ ]')
    gdalVsi = re.compile(r'(\/vsi.*?\/)(\/?.*(\.zip|\.t?gz|\.tar))\/?(.*)')

    LAYERS_DIR_NAME = 'layers'

    def __init__(self, settings):
        QgsTask.__init__(self, 'QConsolidate')

        self.settings = settings

        self.project = None
        self.projectFile = None
        self.baseDirectory = os.path.join(self.settings['output'], self.LAYERS_DIR_NAME)

        self.error = ''

    def run(self):
        self.packageProject()

        layersDirectory = os.path.join(self.settings['output'], self.LAYERS_DIR_NAME)
        if not os.path.isdir(layersDirectory):
            os.mkdir(layersDirectory)

        layers = QgsProject.instance().mapLayers()
        total = 100.0 / len(layers)

        for count, layer in enumerate(layers.values()):
            QgsMessageLog.logMessage('Consolidating {layer}.'.format(layer=layer.name()), 'QConsolidate', Qgis.Info)
            if self.isCanceled():
                break

            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                self.packageVectorLayer(layer)
            elif layerType == QgsMapLayer.RasterLayer:
                self.packageRasterLayer(layer)
            elif layerType == QgsMapLayer.PluginLayer:
                self.packagePluginLayer(layer)

            self.setProgress(int(count * total))

        self.project.write(self.projectFile)

        return True

    def finished(self, result):
        if result:
            self.consolidateComplete.emit()
        else:
            self.errorOccurred.emit(self.error)

    def packageProject(self):
        projectFile = QgsProject.instance().fileName()
        fileName = os.path.basename(projectFile)
        if projectFile:
            shutil.copy(projectFile, self.settings['output'])
            self.projectFile = os.path.join(self.settings['output'], fileName)
        else:
            # FIXME: save project in temporary files?
            self.projectFile = os.path.join(self.settings['output'], 'project.qgs')
            QgsProject.instance().write(self.projectFile)

        self.project = ET.parse(self.projectFile)

    def packageVectorLayer(self, layer):
        raise NotImplementedError('Needs to be implemented by subclasses.')

    def packageRasterLayer(self, layer):
        raise NotImplementedError('Needs to be implemented by subclasses.')

    def packagePluginLayer(self, layer):
        raise NotImplementedError('Needs to be implemented by subclasses.')

    def _updateLayerSource(self, layerId, newSource):
        # update layer source in the layer tree section.
        element = self.project.find('*//layer-tree-layer/[@id="{}"]'.format(layerId))
        element.set('source', newSource)

        # update layer source in the project layers section
        element = self.project.find('./projectlayers/maplayer/[id="{}"]'.format(layerId))
        element.find('datasource').text = newSource

    def _safeName(self, layerName):
        return self.badChars.sub('', layerName).title().replace(' ', '')
