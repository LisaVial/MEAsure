from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication
from plot_widget import PlotWidget

button_style = """
QPushButton {
    background-color: #8ab3e8;
    border-radius: 13;
    border: 0.5px solid black
}

QPushButton:hover {
    background-color: #FFFFFF;
}
"""

class MeaGrid(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        for col, c in enumerate(range(65, 83)):
            for row, n in enumerate(range(1, 17)):
                if col in [0, 17] and row in [0, 15]:
                    continue
                button = QPushButton(chr(c) + str(n))
                button.setFixedSize(26, 26)
                button.setStyleSheet(button_style)
                id = chr(c) + str(n)
                button.pressed.connect(lambda id=id: self.on_button_pressed(id))

                self.grid_layout.addWidget(button, row, col)

    def on_button_pressed(self, id):
        # plot_widget = PlotWidget(id)
        print("Button with id:", id)

