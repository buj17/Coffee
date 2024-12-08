import sqlite3
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QTableWidgetItem
from UI import addEditCoffeeForm_ui, main_ui


class Main(QMainWindow, main_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect('data/coffee.sqlite3')
        self.coffee_data = None
        self.load_table()

        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)

    def load_table(self):
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(('Название сорта', 'Степень обжарки', 'Молотый/В зернах',
                                                    'Описание вкуса', 'Цена', 'Объем упаковки'))

        self.get_coffee_data()

        for i, record in enumerate(self.coffee_data):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, element in enumerate(record[1:]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(element)))

        self.tableWidget.resizeColumnsToContents()

    def get_coffee_data(self):
        request = '''SELECT coffee.id,
       coffee.sort_title,
       coffee.degree_of_roasting,
       coffee.ground_or_grains,
       coffee.flavor_description,
       coffee.price,
       coffee.volume_of_packaging
  FROM coffee;
'''
        cursor = self.connection.cursor()
        self.coffee_data = cursor.execute(request).fetchall()

    def add_coffee(self):
        add_form = addEditCoffeeForm(self, Qt.WindowType.Window)
        add_form.show()

    def edit_coffee(self):
        try:
            selected_id = self.coffee_data[self.tableWidget.selectedItems()[0].row()][0]
            edit_form = addEditCoffeeForm(self, Qt.WindowType.Window, selected_id)
            edit_form.show()
        except IndexError:
            self.statusBar().showMessage('Ничего не выбрано')
        else:
            self.statusBar().clearMessage()

    def closeEvent(self, a0):
        self.connection.close()


class addEditCoffeeForm(QWidget, addEditCoffeeForm_ui.Ui_Form):
    def __init__(self, parent, flags, coffee_id=None):
        super().__init__(parent, flags)
        self.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.coffee_id = coffee_id
        self.connection = sqlite3.connect('data/coffee.sqlite3')

        if coffee_id:
            self.pushButton.setText('Редактировать')
            self.load_coffee()
            self.pushButton.clicked.connect(self.edit)
        else:
            self.pushButton.setText('Добавить')
            self.pushButton.clicked.connect(self.add)

    def add(self):
        if not all((self.sortNameEdit.text(),
                    self.degreeOfRoastingEdit.text(),
                    self.descriptionPlainTextEdit.toPlainText())):
            return
        request = f'''INSERT INTO coffee (
                       sort_title,
                       degree_of_roasting,
                       ground_or_grains,
                       flavor_description,
                       price,
                       volume_of_packaging
                   )
                   VALUES (
                       '{self.sortNameEdit.text()}',
                       '{self.degreeOfRoastingEdit.text()}',
                       '{self.comboBox.currentText()}',
                       '{self.descriptionPlainTextEdit.toPlainText()}',
                       {self.priceDoubleSpinBox.value()},
                       {self.volumeOfPackagingSpinBox.value()}
                   );'''
        cursor = self.connection.cursor()
        cursor.execute(request)
        self.connection.commit()
        self.close()
        self.parent().load_table()

    def edit(self):
        if not all((self.sortNameEdit.text(),
                    self.degreeOfRoastingEdit.text(),
                    self.descriptionPlainTextEdit.toPlainText())):
            return
        request = f'''UPDATE coffee
   SET sort_title = '{self.sortNameEdit.text()}',
       degree_of_roasting = '{self.degreeOfRoastingEdit.text()}',
       ground_or_grains = '{self.comboBox.currentText()}',
       flavor_description = '{self.descriptionPlainTextEdit.toPlainText()}',
       price = {self.priceDoubleSpinBox.value()},
       volume_of_packaging = {self.volumeOfPackagingSpinBox.value()}
 WHERE coffee.id = {self.coffee_id};
'''
        cursor = self.connection.cursor()
        cursor.execute(request)
        self.connection.commit()
        self.close()
        self.parent().load_table()

    def load_coffee(self):
        request = f'''SELECT coffee.sort_title,
       coffee.degree_of_roasting,
       coffee.ground_or_grains,
       coffee.flavor_description,
       coffee.price,
       coffee.volume_of_packaging
  FROM coffee
 WHERE coffee.id = {self.coffee_id};
'''
        cursor = self.connection.cursor()
        data = cursor.execute(request).fetchone()
        sort_title, degree_of_roasting, ground_or_grains, flavor_description, price, volume_of_packaging = data
        self.sortNameEdit.setText(sort_title)
        self.degreeOfRoastingEdit.setText(degree_of_roasting)
        self.comboBox.setCurrentText(ground_or_grains)
        self.descriptionPlainTextEdit.setPlainText(flavor_description)
        self.priceDoubleSpinBox.setValue(price)
        self.volumeOfPackagingSpinBox.setValue(volume_of_packaging)

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
