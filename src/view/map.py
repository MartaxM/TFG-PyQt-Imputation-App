import io
import folium # pip install folium
from PyQt5.QtWebEngineWidgets import QWebEngineView # pip install PyQtWebEngine
from PyQt5.QtWidgets import QSizePolicy
from view.tab_widget_base import TabWidgetBase
import re

class Map(QWebEngineView, TabWidgetBase):
    def __init__(self, 
                 coordinates = (37.1697964193299, -3.59594140201807), 
                 title = 'Mapa',
                 zoom = 15):
        super().__init__()
        # Variables
        self.__title = title
        self.__centralCoors = coordinates
        self.__zoom = zoom
        self.__layers = {}
        self.__map = self.__getNewMap()
        # save map data to data object
        data = io.BytesIO()
        self.__map.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def addLayer(self, label, df, columns):
        if label in self.__layers.keys():
            self.__layers.pop(label)
        layer = folium.FeatureGroup(name=label)
        layer.add_to(self.__map)
        self.addMarkers(df, layer, label, columns)
        self.__layers.update({label:layer})
        self.reload()
        return

    def removeLayer(self, label, columns = None):
        if label in self.__layers.keys():
            self.__layers.pop(label)
            self.__map = self.__getNewMap()
            for layer in self.__layers.values():
                layer.add_to(self.__map)

            data = io.BytesIO()
            self.__map.save(data, close_file=False)
            self.setHtml(data.getvalue().decode())
        return
    
    def renameLayers(self, renamePairs, args = None):
        df = args.get('df')
        columns = args.get('columns')
        if df and columns:
            for old, new in renamePairs.items():
                if old in self.__layers.keys():
                    self.__layers.pop(old)
                    layer = folium.FeatureGroup(name=new)
                    layer.add_to(self.__map)
                    self.addMarkers(df[old], layer, new, columns)
                    self.__layers.update({new:layer})
        
        data = io.BytesIO()
        self.__map.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())

    def __getNewMap(self):
        return folium.Map(
            title = self.__title ,
        	zoom_start=self.__zoom,
        	location=self.__centralCoors,
            prefer_canvas=True,
        )

    def reload(self):
        bounds = []
        for fg in self.__layers.values():
            for child in fg._children.values():
                if hasattr(child, 'location'):
                    bounds.append(child.location)

        if bounds:
            self.__map.fit_bounds(bounds)

        data = io.BytesIO()
        self.__map.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())

    def addMarker(self, row, parent, label, columns):
        popup = self.createPopup(row, label)
        
        average = 0
        lenth = 0
        for col in columns:
            value = row.get(col, None)
            if value:
                average += value
                lenth += 1
        if lenth != 0:
            average = average / lenth

        c = '#43d9de'
        if average > 35.4:
            c = '#ff0000'
        elif average < 12.0:
            c = '#70ff00'
        folium.CircleMarker(
            [row["lat"], row["long"]],
            fill_color = c, color = c ,
            radius=8, fill_opacity=0.7,
            popup=popup,
            lazy=True
            ).add_to(parent)
       
    def addMarkers(self, df, parent, label, columns):
        df.apply(self.addMarker,axis=1,args=([parent, label, columns]))

    def createPopup(self, row, label):
        html = f"""
            <h2> {str(row["lat"])  + ", " + str(row["long"])} </h2>
            <table>
                <tr>
                    <th>From: </th>
                    <th>{label}</th>
                </tr>
            """
        
        for key, value in row.items():
            html = html + f"""
                    <tr>
                        <th>{key}</th>
                        <th>{value}</th>
                    </tr>
                """

        html = html + f"""
            </table>
        """

        iframe = folium.IFrame(html=html, width=315, height=200)
        popup = folium.Popup(iframe, max_width=2650)
        return popup
        
    def updateViewResult(self, results):
        for dsd, obj in results.items():
            self.addLayer(obj['label'],obj['df'],[dsd])

    

    