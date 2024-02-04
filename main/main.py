import sqlite3
from PyQt5 import uic
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

class CoffeeInfo(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setWindowTitle("Coffee Info")

        # Создание таблицы для отображения информации о кофе
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Название сорта', 'Степень обжарки', 
                                              'Молотый/в зернах', 'Описание вкуса', 
                                              'Цена', 'Объем упаковки'])
        
        # Загрузка информации о кофе из базы данных
        self.load_coffee_data()

        
    def load_coffee_data(self):
        # Подключение к базе данных
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coffees")
        coffee_data = cursor.fetchall()
        conn.close()

        # Заполнение таблицы информацией о кофе
        self.table.setRowCount(0)
        for i, coffee in enumerate(coffee_data):
            self.table.insertRow(i)
            for j, value in enumerate(coffee):
                item = QTableWidgetItem(str(value))
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoffeeInfo()
    window.show()
    sys.exit(app.exec())
