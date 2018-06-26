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

from qgis.PyQt import uic

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(os.path.join(pluginPath, 'ui', 'directorywriterwidgetbase.ui'))


class DirectoryWriterWidget(BASE, WIDGET):
    def __init__(self, parent=None):
        super(DirectoryWriterWidget, self).__init__(parent)
        self.setupUi(self)

    def settings(self):
        config = dict()
        config['groupLayers'] = self.chkGroupLayers.isChecked()
        #config['driverName'] = self.cmbExportFormat.currentData()

        return config
