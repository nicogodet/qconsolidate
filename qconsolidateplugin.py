# -*- coding: utf-8 -*-

"""
***************************************************************************
    qconsolidateplugin.py
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


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import qconsolidatedialog
import aboutdialog

import resources_rc


class QConsolidatePlugin:
    def __init__(self, iface):
        self.iface = iface

        self.qgsVersion = unicode(QGis.QGIS_VERSION_INT)

        # For i18n support
        userPluginPath = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/qconsolidate"
        systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/qconsolidate"

        overrideLocale = QSettings().value("locale/overrideFlag", False, type=bool)
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value("locale/userLocale", "")

        if QFileInfo(userPluginPath).exists():
            translationPath = userPluginPath + "/i18n/qconsolidate_" + localeFullName + ".qm"
        else:
            translationPath = systemPluginPath + "/i18n/qconsolidate_" + localeFullName + ".qm"

        self.localePath = translationPath
        if QFileInfo(self.localePath).exists():
            self.translator = QTranslator()
            self.translator.load(self.localePath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        if int(self.qgsVersion) < 20000:
            qgisVersion = self.qgsVersion[0] + "." + self.qgsVersion[2] + "." + self.qgsVersion[3]
            QMessageBox.warning(self.iface.mainWindow(), "QConsolidate",
                                QCoreApplication.translate("QConsolidate", "QGIS %s detected.\n") % (qgisVersion) +
                                QCoreApplication.translate("QConsolidate", "This version of QConsolidate requires at least QGIS version 2.0.\nPlugin will not be enabled."))
            return None

        self.actionRun = QAction(QIcon(":/icons/qconsolidate.png"), "QConsolidate", self.iface.mainWindow())
        self.actionRun.setStatusTip(QCoreApplication.translate("QConsolidate", "Consolidates all layers from current QGIS project into one directory"))
        self.actionAbout = QAction(QIcon(":/icons/about.png"), "About QConsolidate", self.iface.mainWindow())

        self.actionRun.triggered.connect(self.run)
        self.actionAbout.triggered.connect(self.about)

        self.iface.addPluginToMenu(QCoreApplication.translate("QConsolidate", "QConsolidate"), self.actionRun)
        self.iface.addPluginToMenu(QCoreApplication.translate("QConsolidate", "QConsolidate"), self.actionAbout)
        self.iface.addToolBarIcon(self.actionRun)

    def unload(self):
        self.iface.removePluginMenu(QCoreApplication.translate("QConsolidate", "QConsolidate"), self.actionRun)
        self.iface.removePluginMenu(QCoreApplication.translate("QConsolidate", "QConsolidate"), self.actionAbout)
        self.iface.removeToolBarIcon(self.actionRun)

    def run(self):
        dlg = qconsolidatedialog.QConsolidateDialog(self.iface)
        dlg.exec_()

    def about(self):
        dlg = aboutdialog.AboutDialog()
        dlg.exec_()
