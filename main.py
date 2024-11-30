import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.connection = sqlite3.connect('coffee.sqlite3')
        self.tableWidget: QTableWidget = self.tableWidget
        self.coffee_data = None
        self.load_table()

    def load_table(self):
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(('Название сорта', 'Степень обжарки', 'Молотый/В зернах',
                                                    'Описание вкуса', 'Цена', 'Объем упаковки'))

        self.get_coffee_data()

        for i, record in enumerate(self.coffee_data):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, element in enumerate(record):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(element)))

        self.tableWidget.resizeColumnsToContents()

    def get_coffee_data(self):
        request = '''SELECT coffee.sort_title,
       coffee.degree_of_roasting,
       coffee.ground_or_grains,
       coffee.flavor_description,
       coffee.price,
       coffee.volume_of_packaging
  FROM coffee;
'''
        cursor = self.connection.cursor()
        self.coffee_data = cursor.execute(request).fetchall()

    def closeEvent(self, a0):
        self.connection.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
