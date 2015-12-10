# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InterfaceExperiment
                                 A QGIS plugin
 try creating a functional interface for flood
                             -------------------
        begin                : 2015-12-04
        copyright            : (C) 2015 by fbot
        email                : f.j.bot@student.tudelft.nl
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load InterfaceExperiment class from file InterfaceExperiment.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .InterfaceExperimentModule import InterfaceExperiment
    return InterfaceExperiment(iface)
