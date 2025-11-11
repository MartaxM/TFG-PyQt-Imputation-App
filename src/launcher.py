from PyQt5.QtWidgets import QApplication, QSplashScreen, QLabel
from PyQt5.QtGui import QPixmap, QFont, QColor, QMovie
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import os, sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class BackendLoader(QThread):
    loaded = pyqtSignal()

    def run(self):
        """Run any heavy functions before main interface generates"""
        from app import readyModel
        readyModel()
        self.loaded.emit()

def create_main_window():
    from app import createViewController
    return createViewController()

if __name__ == '__main__':
    """Main funtion to launch app with launcher"""

    # Set app
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Loading screen
    splashImage = QPixmap(resource_path("assets/loadingSplash.png")).scaledToWidth(600)
    splash = QSplashScreen(splashImage)
    splash.setEnabled(False)
    splash.setFont(QFont("Verdana", 14))
    color = QColor("#aaf2c7")

    # Loading spinner
    loadingSpinnerLabel = QLabel(splash)
    loadingSpinnerSize = 48
    loadingSpinnerLabel.setGeometry(
        (splashImage.width() - loadingSpinnerSize)//2,
        (splashImage.height() - loadingSpinnerSize)//2,
        loadingSpinnerSize,
        loadingSpinnerSize
    )

    loadingSpinner = QMovie(resource_path("assets/loadingAnimation.gif"))
    loadingSpinner.setScaledSize(loadingSpinnerLabel.size())
    loadingSpinnerLabel.setMovie(loadingSpinner)
    loadingSpinner.start()
    splash.showMessage("Loading application...", Qt.AlignBottom | Qt.AlignRight, color)

    # Show loading screen
    splash.show()
    app.processEvents()

    def on_backend_ready():
        """Create main window when the model is ready"""
        splash.showMessage("Starting interface...", Qt.AlignBottom | Qt.AlignRight, color)
        loadingSpinner.stop()
        app.mainWindow, app.controller = create_main_window()
        QTimer.singleShot(300, lambda: splash.finish(app.mainWindow))
        app.mainWindow.show()
        app.mainWindow.raise_()
        app.mainWindow.activateWindow()
    
    loader = BackendLoader()
    loader.loaded.connect(on_backend_ready)
    loader.start()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')
