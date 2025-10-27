from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from view.tab_widget_base import TabWidgetBase
import matplotlib
    
class Plot(TabWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        matplotlib.use("Qt5Agg")
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def removeByLabel(self, label):
        for line in self.axes.get_lines():
            if line.get_label() == label:
                line.remove()
                break
    
    def renameLayers(self, renamePairs):
        update = False
        for line in self.axes.get_lines():
            label = line.get_label() 
            if label in renamePairs.keys():
                line.set_label(renamePairs[label])
                update = True
        if update:
            self.axes.legend()
            self.canvas.draw()
    
    def addLayer(self, label, df, column):
        self.removeByLabel(label)
        self.axes.plot(df[column], label=label, **{'marker':'x'})
        self.axes.legend()
        self.canvas.draw()
        return

    def removeLayer(self, label, column = None):
        self.removeByLabel(label)
        self.axes.legend()
        self.canvas.draw()
        return

    def reload(self, df, label, x_col = None, y_col= None):
        self.removeByLabel(label)
        if x_col and y_col:
            self.axes.plot(df[x_col], df[y_col], label=label)
        elif y_col:
            self.axes.plot(df[y_col], label=label)
        else:
            # Plot all columns
            for col in df.columns:
                self.axes.plot(df[col], label=label)

        self.axes.legend()
        self.canvas.draw()
    
    def clear(self):
        self.axes.clear()
        self.canvas.draw()

    def updateViewResult(self, results):
        for dsd, obj in results.items():
            self.addLayer(dsd,obj,dsd)