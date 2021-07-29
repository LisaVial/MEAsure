# overlay for main window that shows an animation and prevents interaction while active

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets


class AnimationOverlayWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.background_color = QtGui.QColor('darkGray',)
        self.background_color.setAlpha(175)

        self.setAttribute(QtCore.Qt.WA_NoMousePropagation, True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.animation_label = QtWidgets.QLabel()

        icon = QtGui.QIcon("./icons/heatmap_icon.png")
        self.movie = QtGui.QMovie("./icons/animation.gif")
        self.movie.setScaledSize(QtCore.QSize(512, 512))
        self.animation_label.setMovie(self.movie)
        layout.addWidget(self.animation_label)

        self.hide()  # hide initially


    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.save()
        painter.fillRect(self.pos().x(), self.pos().y(), self.width(), self.height(), self.background_color)
        painter.restore()

    def start(self):
        self.move(0, 0)
        self.resize(self.parent.size())
        self.movie.start()
        self.show()
        #self.activateWindow()

    def stop(self):
        self.hide()
        self.movie.stop()
