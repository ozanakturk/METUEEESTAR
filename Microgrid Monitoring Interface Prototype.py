from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
import datetime
import sys
import csv
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')


# MplsCanvas class is used with matplotlib for implementing plotting tool to the PyQt5 application
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig1, ax = plt.subplots(figsize=(width, height), dpi=dpi)
        self.fig = fig1
        self.ax = ax
        super(MplCanvas, self).__init__(fig1)


# This class is used to create "datetime" variables according to user selected dates
class Variables:
    def __init__(self, location, start_total=0, end_total=0):
        self.location = location
        self.day = []
        self.month = []
        self.year = []
        self.hour = []
        self.minute = []
        self.active_power = []
        self.complex_power = []
        self.apparent_power = []
        self.total_power = []
        self.read_data(start_total, end_total)

    def read_data(self, start_total, end_total):
        with open(self.location, 'r', newline='') as f:
            f.readline()
            reader = f.readlines()

            for line in reader:
                line = line.split('\t')
                temp_day = int(line[0].split('/')[1])
                temp_month = int(line[0].split('/')[0])
                temp_year = int(line[0].split('/')[2])

                temp = int(line[1].split(':')[0])
                if line[1].split(' ')[1][0] == 'P' and temp != 12:
                    temp_hour = temp + 12
                elif (line[1].split(' ')[1][0] == 'P' and temp == 12) or (
                        line[1].split(' ')[1][0] == 'A' and temp != 12):
                    temp_hour = temp
                else:
                    temp_hour = temp - 12

                temp_minute = int(line[1].split(':')[1])
                temp_total = temp_minute + temp_hour * 60 + temp_day * 24 * 60 + temp_month * 30 * 24 * 60 + temp_year * 365 * 24 * 60

                if start_total <= temp_total <= end_total:
                    self.minute.append(temp_minute)
                    self.hour.append(temp_hour)
                    self.day.append(temp_day)
                    self.month.append(temp_month)
                    self.year.append(temp_year)
                    self.active_power.append(line[2].split('.')[0])
                    self.complex_power.append(line[3].split('.')[0])
                    self.apparent_power.append(line[4].split('.')[0])
                    self.total_power.append(line[5].split('.')[0])


# This class takes time information
class Date:
    def __init__(self, hour=0, minute=0, day=0, month=0, year=0):
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month
        self.year = year


# This class represents a window containing three tabs and displays them when called
class TabWidget(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        # Setting title to the main window, adding tabs and showing the tabs
        self.setWindowTitle('Microgrid Monitoring Interface Prototype')
        self.setGeometry(351, 173, 1204, 725)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.addTab(Window(), 'First Tab')
        self.tabWidget.addTab(Window2(), 'Second Tab')
        self.tabWidget.addTab(Window3(), 'Third Tab')

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tabWidget)

        self.setLayout(vbox)

        # Displaying the window in full screen
        self.show()


# This is the main window. It contains the following:
# some labels (simple texts),
# two time selection widgets,
# four checkboxes for power type selection,
# plot and table widgets,
# and "save" & "export" buttons
class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        # Creating a layout that will keep our items in the order of our choice
        self.gridLayoutWidget = QtWidgets.QWidget()
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # Creating two labels and adding them the the layout
        self.label_1 = QtWidgets.QLabel("From")
        self.label_2 = QtWidgets.QLabel("To")
        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        # Creating two date selection panels and giving them default times
        self.dateTimeEdit_1 = QtWidgets.QDateTimeEdit(self.gridLayoutWidget)
        self.dateTimeEdit_2 = QtWidgets.QDateTimeEdit(self.gridLayoutWidget)

        self.temp_def_start = QtCore.QDateTime(2017, 11, 20, 0, 0)
        self.temp_def_end = QtCore.QDateTime(2017, 11, 20, 1, 0)
        self.dateTimeEdit_1.setDateTime(self.temp_def_start)
        self.dateTimeEdit_2.setDateTime(self.temp_def_end)

        self.gridLayout.addWidget(self.dateTimeEdit_1, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.dateTimeEdit_2, 1, 1, 1, 1)

        # Creating four checkboxes for the user to toggle
        self.checkBox_1 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_1.setText("Active Power")
        self.checkBox_2 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_2.setText("Complex Power")
        self.checkBox_3 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_3.setText("Apparent Power")
        self.checkBox_4 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_4.setText("Total Power")
        self.gridLayout.addWidget(self.checkBox_1, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.checkBox_2, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.checkBox_3, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.checkBox_4, 3, 1, 1, 1)

        # Creating two radio buttons for user to select
        self.radioButton_1 = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.radioButton_1.setText("Plot")
        self.radioButton_2 = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.radioButton_2.setText("Table")
        self.gridLayout.addWidget(self.radioButton_1, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.radioButton_2, 5, 1, 1, 1)

        # Opening space for the plot widget (it will be declared again in the plot function)
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.sc, self)
        layout_1 = QtWidgets.QVBoxLayout()
        layout_1.addWidget(toolbar)
        layout_1.addWidget(self.sc)
        self.gridLayout.addLayout(layout_1, 6, 0, 1, 1)

        # Creating the table section
        self.tableWidget = QtWidgets.QTableWidget(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.tableWidget, 6, 1, 1, 1)

        # Creating the legend placement combobox
        self.label_3 = QtWidgets.QLabel("Legend Placement:")
        self.gridLayout.addWidget(self.label_3, 7, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.comboBox.addItems(["Lower Right", "Upper Right", "Lower Left", "Upper Left"])
        self.gridLayout.addWidget(self.comboBox, 7, 1, 1, 1)

        # Configuring the layout
        layout_2 = QtWidgets.QHBoxLayout()
        layout_2.addWidget(self.label_3)
        layout_2.addWidget(self.comboBox)
        layout_2.addStretch()

        # Adding buttons at the bottom
        self.button_1 = QtWidgets.QPushButton("Save")
        self.button_2 = QtWidgets.QPushButton("Export")

        # Configuring the layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.gridLayoutWidget)

        layout_3 = QtWidgets.QHBoxLayout()
        layout_3.addStretch()
        layout_3.addWidget(self.button_1)
        layout_3.addWidget(self.button_2)
        layout_3.addStretch()

        main_layout.addLayout(layout_2)
        main_layout.addLayout(layout_3)

        self.setLayout(main_layout)

        # Creating the data holder variable my_list
        self.my_list = None

        # Connecting functions to click events of buttons
        self.button_1.clicked.connect(self.save)
        self.button_2.clicked.connect(self.export)

    # This function reads data for the given interval from database (.txt file) and calls other functions
    def save(self):

        # Deciding the time interval and getting data from a .txt file
        start_end = []
        for date in [self.dateTimeEdit_1, self.dateTimeEdit_2]:
            start_end.append(date.time().minute() + \
                             date.time().hour() * 60 + \
                             date.date().day() * 24 * 60 + \
                             date.date().month() * 30 * 24 * 60 + \
                             date.date().year() * 365 * 24 * 60)

        location = 'MEAS 112 -- SD Card.txt'
        self.my_list = Variables(location, start_end[0], start_end[1])

        # Calling other functions according to the radio buttons
        if self.radioButton_1.isChecked():
            self.plot()
        elif self.radioButton_2.isChecked():
            self.table()

    # This function plots the data on the plot widget
    def plot(self):

        # Creating the plot widget, with a navigation toolbar
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.sc, self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)
        self.gridLayout.addLayout(layout, 6, 0, 1, 1)

        # This variable keeps the time data in datetime.datetime format
        # The reason for creating this variable is that matplotlib takes time input in this format
        x = []
        for i in range(len(self.my_list.minute)):
            x.append(datetime.datetime(self.my_list.year[i],
                                       self.my_list.month[i],
                                       self.my_list.day[i],
                                       self.my_list.hour[i],
                                       self.my_list.minute[i], 0))

        # This list stores zeros and ones according to which checkbox is checked
        is_checked = [
            self.checkBox_1.isChecked(),
            self.checkBox_2.isChecked(),
            self.checkBox_3.isChecked(),
            self.checkBox_4.isChecked()
        ]

        # This list used for displaying the names of the power types on the legend
        data_names = [
            'Active Power',
            'Complex Power',
            'Apparent Power',
            'Total Power'
        ]

        # This variable stores the power information
        data = [
            self.my_list.active_power,
            self.my_list.complex_power,
            self.my_list.apparent_power,
            self.my_list.total_power
        ]

        # Here, the power data is plotted according to is_checked variable and the legend is created
        for i in range(4):
            if is_checked[i]:
                self.sc.ax.plot(x, [int(j) for j in data[i]], label=data_names[i])
                self.sc.ax.set_facecolor('#eafff5')

        # Adjusting the display of the plot and naming axes
        plt.xticks(rotation=30)
        self.sc.ax.set_xlabel('Time')
        self.sc.ax.set_ylabel('Power')
        self.sc.ax.grid(True)

        # Setting the legend location as an example for combobox on this prototype
        if self.comboBox.currentText() == 'Lower Right':
            self.sc.ax.legend(loc='lower right')
        elif self.comboBox.currentText() == 'Upper Right':
            self.sc.ax.legend(loc='upper right')
        elif self.comboBox.currentText() == 'Lower Left':
            self.sc.ax.legend(loc='lower left')
        elif self.comboBox.currentText() == 'Upper Left':
            self.sc.ax.legend(loc='upper left')

    # This function puts the data to the table
    def table(self):

        # Setting the row and column numbers of the table widget
        row_count = len(self.my_list.minute)
        column_count = self.checkBox_1.isChecked() + self.checkBox_2.isChecked() + self.checkBox_3.isChecked() + self.checkBox_4.isChecked()
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Putting the selected power type names on the headers
        count = -1
        if self.checkBox_1.isChecked():
            count += 1
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(count, item)
            item = self.tableWidget.horizontalHeaderItem(count)
            item.setText('Active Power')
        if self.checkBox_2.isChecked():
            count += 1
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(count, item)
            item = self.tableWidget.horizontalHeaderItem(count)
            item.setText('Complex Power')
        if self.checkBox_3.isChecked():
            count += 1
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(count, item)
            item = self.tableWidget.horizontalHeaderItem(count)
            item.setText('Apparent Power')
        if self.checkBox_4.isChecked():
            count += 1
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(count, item)
            item = self.tableWidget.horizontalHeaderItem(count)
            item.setText('Total Power')

        # Putting the data on the table
        for i in range(row_count):

            # Converting the hours and minutes from 1 a.m notation to 13:00 notation
            temp_hour = str(self.my_list.hour[i])
            if int(temp_hour) < 10:
                temp_hour = '0' + temp_hour
            temp_minute = str(self.my_list.minute[i])
            if int(temp_minute) < 10:
                temp_minute = '0' + temp_minute

            # Constructing the time text
            text = str(self.my_list.month[i]) + "/" + str(self.my_list.day[i]) + "/" + str(
                self.my_list.year[i]) + " " + temp_hour + ":" + temp_minute

            # Setting the time text on the left most column
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)
            item = self.tableWidget.verticalHeaderItem(i)
            item.setText(text)

            # Setting the power data on the appropriate places
            count = -1
            if self.checkBox_1.isChecked():
                count += 1
                self.tableWidget.setItem(i, count, QtWidgets.QTableWidgetItem(self.my_list.active_power[i]))
            if self.checkBox_2.isChecked():
                count += 1
                self.tableWidget.setItem(i, count, QtWidgets.QTableWidgetItem(self.my_list.complex_power[i]))
            if self.checkBox_3.isChecked():
                count += 1
                self.tableWidget.setItem(i, count, QtWidgets.QTableWidgetItem(self.my_list.apparent_power[i]))
            if self.checkBox_4.isChecked():
                count += 1
                self.tableWidget.setItem(i, count, QtWidgets.QTableWidgetItem(self.my_list.total_power[i]))

    # This function exports the data on the selected time interval into another .csv file
    def export(self):

        # Creating a .csv file
        with open('exported_data.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for i in range(len(self.my_list.minute)):
                text = []

                # Changing the hour and minute format same as in the plot function
                temp_hour = str(self.my_list.hour[i])
                if int(temp_hour) < 10:
                    temp_hour = '0' + temp_hour
                temp_minute = str(self.my_list.minute[i])
                if int(temp_minute) < 10:
                    temp_minute = '0' + temp_minute

                text.append(str(self.my_list.month[i]) + "/" + str(self.my_list.day[i]) + "/" + str(
                    self.my_list.year[i]) + " " + temp_hour + ":" + temp_minute)

                if self.checkBox_1.isChecked():
                    text.append(' Active Power: ' + self.my_list.active_power[i])
                if self.checkBox_2.isChecked():
                    text.append(' Complex Power: ' + self.my_list.complex_power[i])
                if self.checkBox_3.isChecked():
                    text.append(' Apparent Power: ' + self.my_list.apparent_power[i])
                if self.checkBox_4.isChecked():
                    text.append(' Total Power: ' + self.my_list.total_power[i])

                writer.writerow(text)


class Window2(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel('This is the second tab')
        v_box = QtWidgets.QVBoxLayout()
        v_box.addStretch()
        v_box.addWidget(self.label)
        v_box.addStretch()
        h_box = QtWidgets.QHBoxLayout()
        h_box.addStretch()
        h_box.addLayout(v_box)
        h_box.addStretch()

        self.setLayout(h_box)


class Window3(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel('This is the third tab')
        v_box = QtWidgets.QVBoxLayout()
        v_box.addStretch()
        v_box.addWidget(self.label)
        v_box.addStretch()
        h_box = QtWidgets.QHBoxLayout()
        h_box.addStretch()
        h_box.addLayout(v_box)
        h_box.addStretch()

        self.setLayout(h_box)


app = QtWidgets.QApplication(sys.argv)
my_window = TabWidget()
sys.exit(app.exec_())
