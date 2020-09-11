from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(2)
        self.grid_layout.setVerticalSpacing(0)
        for col, c in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R']):
            for row, n in enumerate(range(1, 17)):
                if c == 'A' and n == 1 or c == 'A' and n == 16 or c == 'R' and n == 1 or c == 'R' and n == 16:
                    continue
                button = QPushButton(c + str(n))
                button.setFixedSize(26, 26)
                button.setStyleSheet(button_style)
                id = c + str(n)
                button.pressed.connect(lambda id=id: self.on_button_pressed(id))

                self.grid_layout.addWidget(button, row, col)

    def on_button_pressed(self, id):
        # plot_widget = PlotWidget(id)
        print("Button with id:", id)

