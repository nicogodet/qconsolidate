# -*- coding: utf-8 -*-

"""
***************************************************************************
    directorywriterwidget.py
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

from qgis.PyQt import uic

from qgis.core import QgsVectorFileWriter

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(os.path.join(pluginPath, 'ui', 'directorywriterwidgetbase.ui'))


class DirectoryWriterWidget(BASE, WIDGET):
    def __init__(self, parent=None):
        super(DirectoryWriterWidget, self).__init__(parent)
        self.setupUi(self)

        drivers = QgsVectorFileWriter.ogrDriverList()
        self.cmbVectorFormat.blockSignals(True)
        for driver in drivers:
            self.cmbVectorFormat.addItem(driver.longName, driver.driverName)
        self.cmbVectorFormat.blockSignals(False)

        topPriority = []
        lowPriority = []
        gdal.AllRegister()
        driverCount = gdal.GetDriverCount()
        for i in range(driverCount):
            driver = gdal.GetDriver(i)
            metadata = driver.GetMetadata()
            if ('DCAP_CREATE' in metadata and metadata['DCAP_CREATE'] == 'YES') and ('DCAP_RASTER' in metadata and metadata['DCAP_RASTER'] == 'YES'):
                shortName = driver.ShortName
                longName = driver.LongName
                if shortName in ('MEM', 'VRT'):
                    continue
                elif shortName == 'GTiff':
                    topPriority.insert(1, (longName, shortName))
                elif shortName == 'GPKG':
                    topPriority.insert(2, (longName, shortName))
                else:
                    lowPriority.append((longName, shortName))

        topPriority.extend(sorted(lowPriority))
        self.cmbRasterFormat.blockSignals(True)
        for driver in topPriority:
            self.cmbRasterFormat.addItem(driver[0], driver[1])
        self.cmbRasterFormat.blockSignals(False)

    def settings(self):
        config = dict()
        config['groupLayers'] = self.chkGroupLayers.isChecked()
        config['vectorFormat'] = self.cmbVectorFormat.currentData()

        return config
