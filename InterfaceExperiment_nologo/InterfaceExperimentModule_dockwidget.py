# -*- coding: utf-8 -*-

"""
/***************************************************************************
 InterfaceExperimentDockWidget
                                 A QGIS plugin
 try creating a functional interface for flood
                             -------------------
        begin                : 2015-12-04
        git sha              : $Format:%H$
        copyright            : (C) 2015 by fbot
        email                : f.j.bot@student.tudelft.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Initialize Qt resources from file resources.py
import resources

import os
import os.path
import random
import csv

from PyQt4 import QtGui, QtCore, uic

from . import utility_functions as uf

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'InterfaceExperimentModule_dockwidget_base.ui'))


class InterfaceExperimentDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = QtCore.pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(InterfaceExperimentDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # define globals
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        # It looks like these are meant to connect dockwidget to open project. Not sure though.
        self.iface.projectRead.connect(self.updateLayers)
        self.iface.newProjectCreated.connect(self.updateLayers)

        # analysis
        self.graph = QgsGraph()
        self.tied_points = []
        self.setNetworkButton.clicked.connect(self.buildNetwork)
        self.shortestRouteButton.clicked.connect(self.calculateRoute)
        self.clearRouteButton.clicked.connect(self.deleteRoutes)
        self.shortestRouteLabel.hide()
        self.shortestRouteButton.hide()
        self.clearRouteButton.hide()

        # Save Image
        self.saveMapButton.clicked.connect(self.saveMap)
        self.saveMapPathButton.clicked.connect(self.selectFile)
        self.reportLabel.hide()

    def closeEvent(self, event):
        # disconnect interface signals
        self.iface.projectRead.disconnect(self.updateLayers)
        self.iface.newProjectCreated.disconnect(self.updateLayers)

        self.reportLabel.hide()
        self.saveMapPathEdit.clear()

        self.closingPlugin.emit()
        event.accept()

### Data Functions ###

    # General Functions (these seem like we need them, not sure though.
    def openScenario(self,filename=""):
        scenario_open = False
        scenario_file = os.path.join('/Users/Fanny/GitHub/GEO1005_ArnhemFlooding','basemap.qgs') ## Ad actual directory
        # check if file exists
        if os.path.isfile(scenario_file):
            self.iface.addProject(scenario_file)
            scenario_open = True
        else:
            last_dir = uf.getLastDir("InterfaceExperiment") # getLastDir(tool_name=''):
            new_file = QtGui.QFileDialog.getOpenFileName(self, "", last_dir, "(*.qgs)")
            if new_file:
                self.iface.addProject(new_file)
                scenario_open = True
        if scenario_open:
            self.updateLayers()

    def saveScenario(self):
        self.iface.actionSaveProject()


### Interface Specifications ###

    def getNetwork(selfs):
            roads_layer = uf.getLegendLayerByName(self.iface, "reduced_roads")
            if roads_layer:
                # see if there is an obstacles layer to subtract roads from the network
                obstacles_layer = uf.getgetLegenLayerByName(self.iface, "Obstacles")
                if obstacles_layer:
                    # retreive roads outside obstacles (inside = False)
                    features = uf.getFeaturesByIntersection(roads_layer, obstacles_layer, False)
                    # add these roads to a new temporary layer
                    road_network = uf.createTempLayer("temp_network", "LINESTRING", roads_layer.crs().postgisSrid(),[],[])
                    road_network.dataProvider().addFeatures(features)
                else:
                    road_network = roads_layer
                return road_network
            else:
                return

    def buildNetwork(self):
        self.network_layer = self.getNetwork()
        if self.network_layer:
            # get the points to be used as origin and destination -- This I wrote myself
            source_points = []

            # build the graph including these points
            if len(source_points) > 1:
                self.graph, self.tied_points = uf.makeUndirectedGraph(self.network_layer, source_points)
                # the tied points are the new source_points on the graph
                if self.graph and self.tied_points:
                    self.shortestRouteLabel.show()
                    self.shortestRouteButton.show()
        return

    def calculateRoute(self):
        # origin and destination must be in the set of tied_points
        options = len(self.tied_points)
        if options > 1:
            # origin and destination are given as an index in the tied_points list
            origin = 0
            destination = random.randint(1,options-1)
            # calculate the shortest path for the given origin and destination
            path = uf.calculateRouteDijkstra(self.graph, self.tied_points, origin, destination)
            # store the route results in temporary layer called "Routes"
            routes_layer = uf.getLegendLayerByName(self,iface, "Routes")
            # create one if it doesn't exist
            if not routes_layer:
                attributes = ["id"]
                types = [QtCore.QVariant.String]
                routes_layer = uf.createTempLayer("Routes", "LINESTRING", self.network_layer.crs().postgisSrid(), attributes, types)
                uf.loadTempLayer(routes_layer)
                routes_layer.setLayerName("Routes")
            # insert route line
            uf.insertTempFeatures(routes_layer, [path], [["testing",100.00]])
            self.refreshCanvas(routes_layer)
            self.clearRouteButton.show()

    def refreshCanvas(self, layer):
        if self.canvas.isCachingEnabled():
            layer.setCacheImage(None)
        else:
            self.canvas.refresh()


    # selecting a file for saving
    def selectFile(self):
        last_dir = uf.getLastDir("InterfaceExperiment")
        path = QtGui.QFileDialog.getSaveFileName(self, "Save map file", last_dir, "PNG (*.png)")
        if path.strip()!="":
            path = unicode(path)
            uf.setLastDir(path,"InterfaceExperiment")
            self.saveMapPathEdit.setText(path)

    # saving the current screen
    def saveMap(self):
        filename = self.saveMapPathEdit.text()
        if filename != '':
            self.canvas.saveAsImage(filename,None,"PNG")
            self.reportLabel.show()

