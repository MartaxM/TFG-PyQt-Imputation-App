import io
import folium # pip install folium
from PyQt5.QtWebEngineWidgets import QWebEngineView # pip install PyQtWebEngine
from PyQt5.QtWidgets import QSizePolicy
from view.tab_widget_base import TabWidgetBase

class Map(QWebEngineView, TabWidgetBase):
    def __init__(self, 
                 coordinates = (37.1697964193299, -3.59594140201807), 
                 title = 'Mapa',
                 zoom = 15):
        super().__init__()
        # Variables
        self.title = title
        self.centralCoors = coordinates
        self.zoom = zoom
        self.layers = {}
        self.map = self.getNewMap()
        # save map data to data object
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def addLayer(self, label, df, column):
        if label in self.layers.keys():
            self.layers.pop(label)
        layer = folium.FeatureGroup(name=label)
        layer.add_to(self.map)
        self.addMarkers(df, layer, label)
        self.layers.update({label:layer})
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())
        return

    def removeLayer(self, label, column = False):
        if label in self.layers.keys():
            self.layers.pop(label)
            self.map = self.getNewMap()
            for layer in self.layers.values():
                layer.add_to(self.map)

            data = io.BytesIO()
            self.map.save(data, close_file=False)
            self.setHtml(data.getvalue().decode())
        return
    
    def renameLayers(self, renamePairs, df):
        for old, new in renamePairs.items():
            if old in self.layers.keys():
                self.layers.pop(old)
                layer = folium.FeatureGroup(name=new)
                layer.add_to(self.map)
                self.addMarkers(df[old], layer, new)
                self.layers.update({new:layer})
        
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())

    def setCentralCoor(self, coordinates):
        self.centralCoors = coordinates

    def setTitle(self, title):
        self.title = title

    def setZoom(self, zoom):
        self.zoom = zoom

    def getNewMap(self):
        return folium.Map(
            title = self.title ,
        	zoom_start=self.zoom,
        	location=self.centralCoors,
            prefer_canvas=True,
        )

    def reload(self ,df_list, label):
        #self.addMarkers(df)
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        # update webView
        self.setHtml(data.getvalue().decode())

    def addMarker(self, row, parent, label):
        popup = self.createPopup(row, label)
        
        c = '#43d9de'
        if row['SDS_P1'] > 10.0:
            c = '#ff0000'
        elif row['SDS_P1'] < 5.0:
            c = '#70ff00'
        folium.CircleMarker(
            [row["lat"], row["long"]],
            fill_color = c, color = c ,
            radius=8, fill_opacity=0.7,
            popup=popup
            ).add_to(parent)
        # folium.Marker(
        #     [row["lat"], row["long"]],
        #     fill_color = c, color = c ,
        #     radius=8, fill_opacity=0.7,
        #     popup=popup,
        #     icon=folium.DivIcon(
        #         icon_size=(150,36),
        #         icon_anchor=(7,20),
        #         html='<div style="font-size: 18pt; color : "'
        #         + c
        #         + '>' 
        #         + str(row['SDS_P1'])
        #         + '</div>',
        #         )
        #     ).add_to(self.map)
       

    def addMarkers(self, df, parent, label):
        df.apply(self.addMarker,axis=1,args=([parent, label]))
        # for name, values in df.items():
        #     print('{name}: {value}'.format(name=name, value=values[0]))
        #popup = self.createPopup

    def createPopup(self, row, label):
        html=f"""
            <h2> {str(row["lat"])  + ", " + str(row["long"])} </h2>
            <table>
                <tr>
                    <th>From: </th>
                    <th>{label}</th>
                </tr>
                <tr>
                    <th>time</th>
                    <th>{row["time"]}</th>
                </tr>
                <tr>
                    <th>sensorid</th>
                    <th>{row["sensorid"]}</th>
                </tr>
                <tr>
                    <th>software_version</th>
                    <th>{row["software_version"]}</th>
                </tr>
                <tr>
                    <th>SDS_P1</th>
                    <th>{row["SDS_P1"]}</th>
                </tr>
                <tr>
                    <th>SDS_P2</th>
                    <th>{row["SDS_P2"]}</th>
                </tr>
                <tr>
                    <th>BME280_temperature</th>
                    <th>{row["BME280_temperature"]}</th>
                </tr>
                <tr>
                    <th>BME280_pressure</th>
                    <th>{row["BME280_pressure"]}</th>
                </tr>
                <tr>
                    <th>BME280_humidity</th>
                    <th>{row["BME280_humidity"]}</th>
                </tr>
            </table> 
            """
        iframe = folium.IFrame(html=html, width=315, height=200)
        popup = folium.Popup(iframe, max_width=2650)
        return popup
        
    def updateViewResult(self, results):
        for dsd, obj in results.items():
            self.addLayer(obj['label'],obj['df'],dsd)

    

    