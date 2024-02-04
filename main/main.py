import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QComboBox, QTextEdit, QHBoxLayout, QMessageBox
import sqlite3
from PyQt5 import uic


class InfoCoffee(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setWindowTitle("Магазин кофе")

        # Создание кнопок "Добавить" "Изменить"
        self.addButton.clicked.connect(self.open_add_form)
        self.updateButton.clicked.connect(self.open_add_form)

        # Создание таблицы для отображения информации о кофе
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Название сорта', 'Степень обжарки', 'Молотый/в зернах', 'Описание вкуса', 'Цена', 'Объем упаковки(в кг.)'])
        #self.conn = sqlite3.connect("coffee.sqlite")
        #self.c = self.conn.cursor()

        # Загрузка информации о кофе из базы данных
        self.load_coffee_data()

            
    def open_add_form(self):
        button = QApplication.instance().sender()
        if button == self.addButton:
            add_form = AddCoffee()
            add_form.exec_()
        else:
            #self.show_edit_form()
            rows = [i.row() for i in self.table.selectedItems()]
            if not rows:
                QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования.")
                return
            ids = rows[0] + 1
            coffee_id = ids
            edit_form = AddCoffee(coffee_id)
            edit_form.exec_()
       # При закрытии формы добавления обновляем информацию о кофе
        self.load_coffee_data()


    def load_coffee_data(self):
        # Подключение к базе данных
        self.conn = sqlite3.connect("coffee.sqlite")
        self.c = self.conn.cursor()
        # Выполнение запроса к базе данных для получения информации о кофе
        coffee_data = self.c.execute("SELECT * FROM coffees").fetchall()
        
        # Закрытие соединения с базой данных
        self.conn.close()
        # Заполнение таблицы информацией о кофе
        self.table.setRowCount(0)
        for i, coffee in enumerate(coffee_data):
            self.table.insertRow(i)
            for j, value in enumerate(coffee):
                item = QTableWidgetItem(str(value))
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()


class AddCoffee(QDialog):
    def __init__(self, coffee_id=-1):
        super().__init__()
        self.form_values = {}
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.setWindowTitle("Добавить запись/Редактировать запись")
        self.setModal(True)
        self.coffee_id = coffee_id
        self.load_data()
        # отображение выбранной записи при редактировании
        if self.coffee_id != -1:
            self.load_initial_values()
        
        self.saveButton.clicked.connect(self.save_coffee)
        self.cancelButton.clicked.connect(self.reject)

    # Загружаем значения из базы данных в QComboBox
    def load_data(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        self.roast_combo.clear()
        self.ground_combo.clear()
        cur.execute('SELECT DISTINCT degree FROM coffees')
        degrees = cur.fetchall()
        for degree in degrees:
            self.roast_combo.addItem(degree[0])
        cur.execute('SELECT DISTINCT kind_coffee FROM coffees')
        kinds= cur.fetchall()
        for kind in kinds:
            self.ground_combo.addItem(kind[0])
        con.close()

    # Загружаем поля выбранной записи при редактировании
    def load_initial_values(self):
        self.load_data()
        con = sqlite3.connect("coffee.sqlite")
        cur = con.cursor()
        cur.execute("SELECT * FROM coffees WHERE id=?", (self.coffee_id,))
        coffee = list(cur.fetchone())
        self.nameLineEdit.setText(coffee[1])
        self.roast_combo.setCurrentText(str(coffee[2]))
        self.ground_combo.setCurrentText(coffee[3])
        self.description_input.setPlainText(coffee[4])
        self.priceLineEdit.setText(str(coffee[5]))
        self.volumeLineEdit.setText(str(coffee[6]))
    
    #получение данных с формы
    def get_form_values(self):
        
        self.form_values["sort"] = self.nameLineEdit.text()
        self.form_values["roast"] = self.roast_combo.currentText()
        self.form_values["ground"] = self.ground_combo.currentText()
        self.form_values["description"] = self.description_input.toPlainText()
        self.form_values["price"] = (self.priceLineEdit.text())
        self.form_values["volume"] = (self.volumeLineEdit.text())
        
        return self.form_values

    def save_coffee(self):
        values = self.get_form_values()
       
        #обработка ввода данных
        if not values["sort"] or not values["price"] or not values["volume"]:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        for el in [values["price"], values["volume"]]:
            if ',' in el:
                QMessageBox.warning(self, "Ошибка", "'В полях: цена и объем отделяйте дробную часть числа точкой!")
                return
        # Подключение к базе данных
        self.conn = sqlite3.connect("coffee.sqlite")
        self.c = self.conn.cursor()
        
        #выбор операции: добавления/редактирования
        if self.coffee_id != -1:
            values = self.get_form_values()
            self.c.execute("UPDATE coffees SET name=?, degree=?, kind_coffee=?, description=?, price=?, "
                           "volume=? WHERE id=?", 
                           (values["sort"], values["roast"], values["ground"],
                            values["description"], float(values["price"]), 
                            float(values["volume"]), self.coffee_id))
        else:
            self.c.execute("INSERT INTO coffees (name, degree, kind_coffee, description, price, volume) VALUES (?, ?, ?, ?, ?, ?)",
                            (values["sort"], values["roast"], values["ground"],
                            values["description"], float(values["price"]), float(values["volume"])))

        # Сохранение изменений в базе данных
        self.conn.commit()

        # Закрытие соединения с базой данных
        self.conn.close()

        # Закрытие формы добавления/редактирования
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InfoCoffee()
    window.show()
    sys.exit(app.exec())
