from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from view.tab_widget_base import TabWidgetBase
import matplotlib
    
class Plot(TabWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        matplotlib.use("Qt5Agg")
        self.__figure = Figure()
        self.__canvas = FigureCanvas(self.__figure)
        self.__axes = self.__figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.__canvas)
        self.setLayout(layout)

    def removeByLabel(self, label):
        for line in self.__axes.get_lines():
            if line.get_label() == label:
                line.remove()
                break
    
    def renameLayers(self, renamePairs, args = None):
        pairs = {}
        columns = args.get('columns')
        if columns:
            for col in columns:
                for old, new in renamePairs.items():
                    pairs.update({
                        old+col : new+col
                    })
        else:
            pairs = renamePairs

        update = False
        for line in self.__axes.get_lines():
            label = line.get_label() 
            if label in pairs.keys():
                line.set_label(pairs[label])
                update = True
        if update:
            self.redraw()
    
    def addLayer(self, label, df, columns):
        if len(columns) == 1:
            self.removeByLabel(label)
            self.__axes.plot(df[columns[0]], label=label, **{'marker':'x'})
        else:
            for column in columns:
                name = label+column
                self.removeByLabel(name)
                self.__axes.plot(df[column], label=name, **{'marker':'x'})
        self.redraw()
        return

    def removeLayer(self, label, columns = None):
        if columns:
            for col in columns:
                name = label + col
                self.removeByLabel(name)
        else:
            self.removeByLabel(label)
        self.redraw()
        return
    
    def redraw(self):
        self.__axes.relim()
        self.__axes.autoscale_view()

        handles, labels = self.__axes.get_legend_handles_labels()
        if handles:
            self.__axes.legend()
        else:
            leg = self.__axes.get_legend()
            if leg:
                leg.remove()
        
        self.__canvas.draw()
    
    def clear(self):
        self.__axes.clear()
        self.__canvas.draw()

    def updateViewResult(self, results):
        for dsd, obj in results.items():
            self.addLayer(dsd,obj,[dsd])