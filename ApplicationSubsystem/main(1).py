import os
import sys
import pandas as pd
import qdarkstyle
from PyQt5.Qt import *
from PyQt5 import QtCore, QtWidgets

from calc import analyze_signal, shape
from myShow import Ui_MainWindow as myShow_
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class GraphDialog(QDialog):
    def __init__(self, data,start_time, end_time):
        super().__init__()
        self.data = data
        self.setWindowTitle(f'CSV Data Graph:pressure')
        self.setFixedSize(800, 600)  # Set window size
        # self.setWindowFlag(Qt.WindowCloseButtonHint, False)  # Disable close button
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.initUI(self.data,start_time, end_time)

    def initUI(self,data,start_time, end_time):
        self.figure.clf()  # Clear previous graphics
        self.ax = self.figure.add_subplot(111)
        cluster = data['cluster']
        self.ax.plot(cluster, data["pressure"], label=f"Sensor pressure", color="red")

        self.ax.set_xlabel("Time (ms)")
        self.ax.set_ylabel("Pressure (kPa)")
        self.ax.set_title("Random Signals from {} to {} ms".format(start_time, end_time))
        self.ax.legend(loc='upper left')
        self.canvas.draw()

    def saveImage(self, path):
        try:
            self.figure.savefig(path, format='jpeg', dpi=300)  # Save as JPEG file
            QMessageBox.information(self, "Success", f"Image saved to {path}", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to save image：{str(e)}", QMessageBox.Cancel)


class myShow(myShow_, QMainWindow):
    def __init__(self):
        super(myShow, self).__init__()
        self.setupUi(self)
        self.data = None
        self.graph_dialogs = None
        self.setWindowTitle('CSV File Reader')
        self.openCsv.clicked.connect(self.open_csv)
        self.applyTimeRange_1.clicked.connect(self.TimeRange)
        self.savefcsv_1.clicked.connect(self.savecsvFun_1)
        self.saveimage_1.clicked.connect(self.saveimageFun_1)
    def saveimageFun_1(self):
        try:
            graph_dialog = self.graph_dialogs
            if graph_dialog is not None:
                options = QFileDialog.Options()
                file_path, _ = QFileDialog.getSaveFileName(self, 'Select save path', '', 'JPEG Files (*.jpeg)', options=options)
                if file_path:
                    graph_dialog.saveImage(file_path)

            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please draw the image first", QtWidgets.QMessageBox.Cancel)
        except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Warning", str(e), QtWidgets.QMessageBox.Cancel)

    def savecsvFun_1(self):
        try:
            if self.data is not None:
                start_time = float(self.lineEditStart_1.text().strip())
                end_time = float(self.lineEditEnd_1.text().strip())
                filtered_data = self.data[(self.data['cluster'] >= start_time) & (self.data['cluster'] <= end_time)]
                # filtered_data = filtered_data[['cluster','pressure']]
                options = QFileDialog.Options()
                file_path, _ = QFileDialog.getSaveFileName(self, 'Select save path', '', 'CSV Files (*.csv)', options=options)
                if file_path:
                    filtered_data.to_csv(file_path,index=False)
                    QtWidgets.QMessageBox.information(self, "ok", "Export successful", QtWidgets.QMessageBox.Yes)
        except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Warning", str(e), QtWidgets.QMessageBox.Cancel)

    def TimeRange(self):
        # try:
        if self.data is not None:
            start_time = float(self.lineEditStart_1.text().strip())
            end_time = float(self.lineEditEnd_1.text().strip())
            filtered_data = self.data[(self.data['cluster'] >= start_time) & (self.data['cluster'] <= end_time)]
            if not filtered_data.empty:
                res1 = analyze_signal(filtered_data['pressure'], self.data['cluster'])
                shape1 = shape(self.data['cluster'])
                filtered_data['group'] = (filtered_data["explosion"] != filtered_data["explosion"].shift(1)).cumsum()
                df_ones = filtered_data[filtered_data["explosion"] == 1]
                result = df_ones.reset_index().groupby('group').agg(start=('index', 'first'), end=('index', 'last'),
                                                                    count=('index', 'count'))
               # Find the maximum length group
                max_length = result['count'].max()
                max_length_groups = result[result['count'] == max_length]
                maxtime = -1
                for _, max_length_info in max_length_groups.iterrows():
                    maxtime = max(maxtime, self.data['cluster'].iloc[max_length_info['end']] - self.data['cluster'].iloc[
                        max_length_info['start']])
                maxtime = round(maxtime,3)

                self.max_1.setText(str(res1["max_val"]) + " kPa")
                self.min_1.setText(str(res1["min_val"]) + " kPa")
                self.Avg_1.setText(str(res1["avg_val"]) + " kPa")
                self.frequency_1.setText(str(res1["dominant_freq"]) + " kPa")
                self.maxFftAmp_1.setText(str(res1["max_fft_magnitude"]))
                self.shape_1.setText(shape1)
                self.explosionTime_1.setText(str(maxtime)+ " ms" if result['count'].max() > 10 else "N/A")
                self.result_1.setText("NO" if result['count'].max() <= 10 else "Yes")

                self.create_graph_dialog(filtered_data,start_time, end_time)  # Create a new graphic popup
            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please check the cluster range, no matching data was found", QtWidgets.QMessageBox.Cancel)
        # except Exception as e:
        #         QtWidgets.QMessageBox.warning(self, "Warning", str(e), QtWidgets.QMessageBox.Cancel)

    def open_csv(self):
        csv_filename, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "*.csv")
        if csv_filename == "":
            QtWidgets.QMessageBox.warning(self, "Warning", "Please load data first", QtWidgets.QMessageBox.Cancel)
            return
       # Check if the extension is .csv
        if not os.path.splitext(csv_filename.lower())[1].lower() == ".csv":
            QtWidgets.QMessageBox.warning(self, "Warning", "Please load CSV format file", QtWidgets.QMessageBox.Cancel)
            return
        # Try to read the CSV file
        try:
            df = pd.read_csv(csv_filename)
            df = df.dropna()
        except pd.errors.EmptyDataError:
            QtWidgets.QMessageBox.warning(self, "Warning", f"document {csv_filename} is an empty file", QtWidgets.QMessageBox.Cancel)
            return False
        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(self, "Warning", f"document {csv_filename} does not exist", QtWidgets.QMessageBox.Cancel)
            return False

        # Check if required columns are included
        requireds = ["batch","delta_pressure"]
        if [col for col in requireds if col not in df.columns]:
            QtWidgets.QMessageBox.warning(self, "Warning", f"The CSV file is not appropriate",
                                           QtWidgets.QMessageBox.Cancel)
            return False

        required_columns = ["cluster","explosion","pressure"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            QtWidgets.QMessageBox.warning(self, "Warning", f"document {csv_filename} The following columns are missing: {', '.join(missing_columns)}",
                                           QtWidgets.QMessageBox.Cancel)
            return False
        self.data = df
        try:
            res1 = analyze_signal(self.data['pressure'], self.data['cluster'])
            shape1 = shape(self.data['cluster'])
            df['group'] = (df["explosion"] != df["explosion"].shift(1)).cumsum()
            df_ones = df[df["explosion"] == 1]
            result = df_ones.reset_index().groupby('group').agg(start=('index', 'first'), end=('index', 'last'),
                                                                count=('index', 'count'))
            # Find the maximum length group
            max_length = result['count'].max()
            max_length_groups = result[result['count'] == max_length]

            maxtime = -1
            for _, max_length_info in max_length_groups.iterrows():
                # print(f"start line: {max_length_info['start']}, end line: {max_length_info['end']}")
                maxtime = max(maxtime,df['cluster'].iloc[max_length_info['end']] - df['cluster'].iloc[max_length_info['start']])
            maxtime = round(maxtime,3)

            self.lineEditStart_1.setText(str(min(self.data['cluster'])))
            self.lineEditEnd_1.setText(str(max(self.data['cluster'])))
            self.max_1.setText(str(res1["max_val"]) + " kPa")
            self.min_1.setText(str(res1["min_val"]) + " kPa")
            self.Avg_1.setText(str(res1["avg_val"]) + " kPa")
            self.frequency_1.setText(str(res1["dominant_freq"]) + " kPa")
            self.maxFftAmp_1.setText(str(res1["max_fft_magnitude"]))
            self.shape_1.setText(shape1)
            self.explosionTime_1.setText(str(maxtime) + " ms" if result['count'].max() > 10 else "N/A")
            self.result_1.setText("NO" if result['count'].max() <= 10 else "Yes")

            self.create_graph_dialog(self.data,min(self.data['cluster']),max(self.data['cluster']))  # Create a new graphic popup
        except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Warning", str(e), QtWidgets.QMessageBox.Cancel)

    def create_graph_dialog(self,data,start_time, end_time):
        if self.data is not None:
            if self.graph_dialogs is None:
                graph_dialog = GraphDialog(data,start_time, end_time)
                self.graph_dialogs = graph_dialog
                graph_dialog.show()
            else:
                graph_dialog = self.graph_dialogs
                graph_dialog.close()
                graph_dialog.initUI(data,start_time, end_time)
                graph_dialog.show()

if __name__ == '__main__':
    # On high-resolution displays, application interface elements will automatically scale to fit the screen resolution.
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    win_myShow = myShow()  # login interface
    win_myShow.show()
    sys.exit(app.exec_())
