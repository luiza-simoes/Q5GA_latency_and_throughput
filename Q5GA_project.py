import re
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

path_resources = os.path.join(os.path.dirname(sys.argv[0]), "resources.py")
sys.path.append(path_resources)
import resources

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QImage, QPainter
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def latency_graph(lines):                                        
    
    data = []
    for line in lines:
        if 'time=' in line:
            start = line.find('time=') + len('time=')
            end = line.find('ms')
            time = float(line[start:end].strip())
            hour = re.search(r'(\d{2}:\d{2}:\d{2})', line).group(1)
            data.append([hour, time])
            
        elif 'Zeit=' in line:
            start = line.find('Zeit=') + len('Zeit=')
            end = line.find('ms')
            time = float(line[start:end].strip())
            try:
                hour = re.search(r'(\d{2}:\d{2}:\d{2})', line).group(1)
            except:
                hour = ""
                
            data.append([hour, time])          
    
    df = pd.DataFrame(data, columns=['Hour', 'Time'])

    jitter_aux = [abs(df['Time'][i] - df['Time'][i+1]) for i in range(len(df) - 1)]
    jitter_df = pd.DataFrame(jitter_aux)
 
    return df['Time'], jitter_df


def throughput_graph(lines):   
    
    data_throughput = []
    for line in lines:
        if 'MBytes' in line:
            line_data = line.strip().split()
            transfer = float(line_data[4])
            bitrate = float(line_data[6])
            data_throughput.append((transfer, bitrate))
    
    df = pd.DataFrame(data_throughput, columns=['Transfer', 'Bitrate'])
    jitter_aux = [abs(df['Bitrate'][i] - df['Bitrate'][i+1]) for i in range(len(df) - 1)]
    jitter_df = pd.DataFrame(jitter_aux)
    
    return df['Bitrate'], jitter_df


def export_images(self, fig, filename_noformat):
    
    reply = QtWidgets.QMessageBox(self)
    reply.setWindowTitle('Message')
    reply.setText("Please, choose a file format.")

    pdf_button = reply.addButton(".pdf", QtWidgets.QMessageBox.YesRole)
    png_button = reply.addButton(".png", QtWidgets.QMessageBox.NoRole)
    cancel_button = reply.addButton(QtWidgets.QMessageBox.Cancel)
    
    QtWidgets.QApplication.processEvents()
    reply.exec_()
    
    
    def path_message(filename):
        
        fullfilepath = os.getcwd() + '\\' + filename
        fig.savefig(fullfilepath)
        message_box = QMessageBox()
        message_box.setWindowTitle("File path")
        message_box.setText("Your file was saved in " + fullfilepath)
        message_box.exec()
        
    if reply.clickedButton() == pdf_button:
        filename = filename_noformat + ".pdf"
        path_message(filename)
        
    elif reply.clickedButton() == png_button: 
        filename = filename_noformat + ".png"
        path_message(filename)
        
    elif reply.clickedButton() == cancel_button: 
        QtWidgets.QMessageBox.warning(self, "Error", "No file was saved.")

        
def get_title(filepath):
    
    filepath_title = filepath.rsplit("/", 1)[-1]   
    return filepath_title


def jitter_graph(self, data, chart_data, chart_title, file_path, data_csv):
    plt.rcParams['lines.linewidth'] = 1
    self.figure = Figure()
    self.figure.clear()
    ax = self.figure.add_subplot(111)
    ax.set_title(str("Jitter graphic from " + chart_title), fontweight='bold')
    ax.set_xlabel("Test time frame")
    ax.set_ylabel("Jitter")
        
    chart_data = data.plot.line(ax=ax, legend=False).get_figure()
    self.canvas = FigureCanvas(self.figure)
    self.scene = QGraphicsScene()
    self.scene.addWidget(self.canvas)
    self.graphicsView.setScene(self.scene)
            
    self.value_max = self.findChild(QLabel, 'value_max')  
    self.value_max.setText(str(round(data[0].max(),2)))
    self.value_min = self.findChild(QLabel, 'value_min')  
    self.value_min.setText(str(round(data[0].min(),2)))
    self.value_mean = self.findChild(QLabel, 'value_mean') 
    self.value_mean.setText(str(round(data[0].mean(),2)))          
    self.value_jitter = self.findChild(QLabel, 'value_jitter')  
    self.value_jitter.setText("-")

    self.value_button = self.findChild(QPushButton, 'button_jitterchart')  
    self.value_button.setText("←  Return")

    self.button_jitterchart.clicked.connect(lambda: self.get_chart(file_path, data_csv))
    self.button_jitterchart.clicked.connect(lambda: self.value_button.setText("Generate Jitter chart  →"))
    
    def goto_export(self, chart_latency, doc_name):
        export_images(self, chart_latency, doc_name)
    
    graph_type = self.findChild(QLabel, 'label').text()
    self.button_export.clicked.connect(lambda: self.goto_export(chart_data, str("Q5GA_" + graph_type.lower() + "_jitter_graphic_" + chart_title.split(".")[0])))


uipath_home = os.path.join(os.path.dirname(sys.argv[0]), "Quick5GAnalyser_home.ui")
uipath_latency = os.path.join(os.path.dirname(sys.argv[0]), "Quick5GAnalyser_latency.ui")
uipath_throughput = os.path.join(os.path.dirname(sys.argv[0]), "Quick5GAnalyser_throughput.ui")
uipath_comparison = os.path.join(os.path.dirname(sys.argv[0]), "Quick5GAnalyser_compare.ui")


class HomeWindow(QMainWindow):
     
    def __init__(self):                              
        super(HomeWindow, self).__init__()
        uic.loadUi(uipath_home, self)
        self.setWindowTitle("Quick 5G Analyser")
        
        self.button_latencyanalysis.clicked.connect(self.goto_latencyscreen)
        self.button_throughputanalysis.clicked.connect(self.goto_throughputscreen)
        self.button_comparegraphics.clicked.connect(self.goto_comparisonscreen)
        
        self.Luiza = self.findChild(QLabel, 'Luiza')  
        self.Luiza.setText('Developed by Luiza Souza Simoes (<a href="mailto:luizassimoes@hotmail.com?subject=Quick%205G%20Analyser%20-%20Contact%20Questions">luizassimoes@hotmail.com</a>)')
        self.Luiza.setStyleSheet("color: black;")
        self.Luiza.setOpenExternalLinks(True)
        self.Luiza.linkActivated.connect(self.goto_email)        
        
    def goto_latencyscreen(self):
        widget.setCurrentIndex(1)
        
    def goto_throughputscreen(self):
        widget.setCurrentIndex(2)

    def goto_comparisonscreen(self):
        widget.setCurrentIndex(3)

    def goto_email(self, url):
        QDesktopServices.openUrl(QUrl(url))

class LatencyWindow(QMainWindow):
    
    def __init__(self):                                         
        super(LatencyWindow, self).__init__()
        uic.loadUi(uipath_latency, self)
        self.setWindowTitle("Quick 5G Analyser - Latency")
        
        self.button_importfile.clicked.connect(self.upload_csv)
        self.button_home.clicked.connect(self.goto_home)
        self.button_throughputanalysis.clicked.connect(self.goto_throughputscreen)
        self.button_comparegraphics.clicked.connect(self.goto_comparisonscreen)
        
    def goto_home(self):
        widget.setCurrentIndex(0)

    def goto_throughputscreen(self):
        widget.setCurrentIndex(2)

    def goto_comparisonscreen(self):
        widget.setCurrentIndex(3)
        
    def goto_jitterchart(self, data, chart_data, chart_title, file_path, data_csv):   
        self.button_export.disconnect()
        jitter_graph(self, data, chart_data, chart_title, file_path, data_csv)
        
    def goto_export(self, chart_latency, doc_name):
        export_images(self, chart_latency, doc_name)


    def upload_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", 
                                                   "", "Text Files (*.txt);;All Files (*)", 
                                                   options=options)                       

        data_csv = []        
                                                     
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data_csv = f.readlines()
                        
            except Exception as e:
                try:
                    with open(file_path, 'r', encoding='charmap') as f:
                        data_csv = f.readlines()
                except Exception as e:
                    pass
                    #print("Error opening file:")
        
        self.get_chart(file_path, data_csv)

    
    def get_chart(self, file_path, data_csv):
        
        chart_title = get_title(file_path)
        
        data, jitter = latency_graph(data_csv)
        chart_latency = self.generate_line_chart(data, chart_title, data_csv)
        
        if chart_latency is not None:
            
            self.value_max = self.findChild(QLabel, 'value_max')  
            self.value_max.setText(str(round(data.max(),2)))
            self.value_min = self.findChild(QLabel, 'value_min')  
            self.value_min.setText(str(round(data.min(),2)))
            self.value_mean = self.findChild(QLabel, 'value_mean') 
            self.value_mean.setText(str(round(data.mean(),2)))          
            self.value_jitter = self.findChild(QLabel, 'value_jitter')  
            self.value_jitter.setText(str(round(jitter[0].mean(), 2)))
            
            self.button_export.disconnect()
            self.button_export.clicked.connect(lambda: self.goto_export(chart_latency, "Q5GA_latency_graphic_" + chart_title.split(".")[0]))
            self.button_jitterchart.clicked.connect(lambda: self.goto_jitterchart(jitter, chart_latency, chart_title,
                                                                                  file_path, data_csv))

        return chart_latency, data_csv
    
    
    def generate_line_chart(self, data, chart_title, data_csv):
        plt.rcParams['lines.linewidth'] = 1
        self.figure = Figure()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_title(chart_title)
        ax.set_xlabel("Test time frame")
        ax.set_ylabel("Ping duration (ms)")
        
        if self.radioButton.isChecked():
            if data.max() > 4*data.mean():
                ax.set_ylim(0.8*data.min(), 1.5*data.mean())
            else:
                pass
        else:
            pass
        
        chart_latency = None
        
        try:
            chart_latency = data.plot.line(ax=ax).get_figure()
            self.canvas = FigureCanvas(self.figure)
            self.scene = QGraphicsScene()
            self.scene.addWidget(self.canvas)
            self.graphicsView.setScene(self.scene)

            self.graphicsView.fitInView(self.scene.itemsBoundingRect())
        except:
            if data_csv == []:
                QtWidgets.QMessageBox.warning(self, "Error", "Please select a file.")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Wrong file type.")
            
        return chart_latency
        
    
class ThroughputWindow(QMainWindow):
    
    def __init__(self):                                         
        super(ThroughputWindow, self).__init__()
        uic.loadUi(uipath_throughput, self)
        self.setWindowTitle("Quick 5G Analyser - Throughput")
        
        self.button_importfile.clicked.connect(self.upload_csv)
        self.button_home.clicked.connect(self.goto_home)
        self.button_latencyanalysis.clicked.connect(self.goto_latencyscreen)
        self.button_comparegraphics.clicked.connect(self.goto_comparisonscreen)
        
        
    def goto_home(self):
        widget.setCurrentIndex(0)
        
    def goto_latencyscreen(self):
        widget.setCurrentIndex(1)

    def goto_comparisonscreen(self):
        widget.setCurrentIndex(3)

    def goto_export(self, chart_throughput, chart_title):
        export_images(self, chart_throughput, "Q5GA_throughput_graphic_" + chart_title.split(".")[0])
    

    def upload_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", 
                                                   "", "Text Files (*.txt);;All Files (*)", 
                                                   options=options)                       
        data_csv = []          
                                                     
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data_csv = f.readlines()
            except Exception as e:
                try:
                    with open(file_path, 'r', encoding='charmap') as f:
                        data_csv = f.readlines()
                except Exception as e:
                    pass
                    #print("Error opening file:", e)
        
        self.get_chart(file_path, data_csv)    
        
      
    def get_chart(self, file_path, data_csv):
        
        chart_title = get_title(file_path)           
         
        data, jitter = throughput_graph(data_csv)
        chart_throughput = self.generate_line_chart(data, chart_title, data_csv)
        
        if chart_throughput is not None:
            self.value_max = self.findChild(QLabel, 'value_max')  
            self.value_max.setText(str(round(data.max(),2)))
            self.value_min = self.findChild(QLabel, 'value_min')  
            self.value_min.setText(str(round(data.min(),2)))
            self.value_mean = self.findChild(QLabel, 'value_mean') 
            self.value_mean.setText(str(round(data.mean(),2)))          
            
            self.button_export.disconnect()
            self.button_export.clicked.connect(lambda: self.goto_export(chart_throughput, chart_title))
            
        
        return chart_throughput
    
    
    def generate_line_chart(self, data, chart_title, data_csv):
        plt.rcParams['lines.linewidth'] = 1
        self.figure = Figure()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_title(chart_title)
        ax.set_xlabel("Test time frame")
        ax.set_ylabel("Mbits/sec")
        
        chart_throughput = None
        
        try:
            chart_throughput = data.plot.line(ax=ax).get_figure()
            self.canvas = FigureCanvas(self.figure)
            self.scene = QGraphicsScene()
            self.scene.addWidget(self.canvas)
            self.graphicsView.setScene(self.scene)

            self.graphicsView.fitInView(self.scene.itemsBoundingRect())
        except:
            if data_csv == []:
                QtWidgets.QMessageBox.warning(self, "Error", "Please select a file.")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Wrong file type.")
        
        return chart_throughput

    
class ComparisonWindow(QMainWindow):
    
    def __init__(self):                                          
        super(ComparisonWindow, self).__init__()
        uic.loadUi(uipath_comparison, self)
        self.setWindowTitle("Quick 5G Analyser - Comparison")
        
        chart_comparison1 = self.button_importfile.clicked.connect(self.upload_csv)
        chart_comparison2 = self.button_importfile2.clicked.connect(self.upload_csv2)
        self.button_home.clicked.connect(self.goto_home)
        self.button_latencyanalysis.clicked.connect(self.goto_latencyscreen)
        self.button_throughputanalysis.clicked.connect(self.goto_throughputscreen)
        
        
    def goto_home(self):
        widget.setCurrentIndex(0)
        
    def goto_latencyscreen(self):
        widget.setCurrentIndex(1)

    def goto_throughputscreen(self):
        widget.setCurrentIndex(2)

    def goto_export(self, chart_comparison, savedfilename):
        export_images(self, chart_comparison, savedfilename)
        

    def upload_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", 
                                                   "", "Text Files (*.txt);;All Files (*)", 
                                                   options=options)       
        data_csv = []  
                                                             
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data_csv = f.readlines()
            except Exception as e:
                try:
                    with open(file_path, 'r', encoding='charmap') as f:
                        data_csv = f.readlines()
                except Exception as e:
                    print("Error opening file:", e)
                
        chart_title = get_title(file_path)
        
        if self.radbutton_latency.isChecked():        
            data, jitter = latency_graph(data_csv)
            chart_comparison1 = self.generate_line_chart(data, chart_title, data_csv)
            
        elif self.radbutton_throughput.isChecked():
            data, jitter = throughput_graph(data_csv)
            chart_comparison1 = self.generate_line_chart(data, chart_title, data_csv)
            self.value_jitter_1 = self.findChild(QLabel, 'value_jitter_2')  
            self.value_jitter_1.setText(str("-"))
            
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Please, select a test type.")
                    
        
        if chart_comparison1 is not None:
            self.value_max = self.findChild(QLabel, 'value_max')  
            self.value_max.setText(str(round(data.max(),2)))
            self.value_min = self.findChild(QLabel, 'value_min')  
            self.value_min.setText(str(round(data.min(),2)))
            self.value_mean = self.findChild(QLabel, 'value_mean') 
            self.value_mean.setText(str(round(data.mean(),2)))  
            
            if self.radbutton_latency.isChecked():             
                self.value_jitter = self.findChild(QLabel, 'value_jitter')  
                self.value_jitter.setText(str(round(jitter[0].mean(), 2)))
            
            try:
                self.button_export.disconnect()
                self.button_export.clicked.connect(lambda: self.goto_export(chart_comparison1, "Q5GA_comparison_graphic_" + chart_title.split(".")[0]))
            except:
                QtWidgets.QMessageBox.warning(self, "Error", "To export more graphics, use the 'Latency test' or the 'Throughput test' tabs.")
                
        return chart_comparison1
    
    def generate_line_chart(self, data, chart_title, data_csv):
        plt.rcParams['lines.linewidth'] = 1
        self.figure = Figure()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_title(chart_title)
        
        if data.max() > 4*data.mean():
            ax.set_ylim(0.8*data.min(), 1.5*data.mean())
        else:
            pass   
        
        chart_comparison1 = None
        
        try:
            chart_comparison1 = data.plot.line(ax=ax).get_figure()
            ax.set_xlabel("")
            self.canvas = FigureCanvas(self.figure)
            self.scene = QGraphicsScene()
            self.scene.addWidget(self.canvas)
            self.graphicsView.setScene(self.scene)
            
            self.graphicsView.fitInView(self.scene.itemsBoundingRect())
        except:
            if data_csv == []:
                QtWidgets.QMessageBox.warning(self, "Error", "Please select a file.")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Wrong file type.")
            
        
        return chart_comparison1
        
    def upload_csv2(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", 
                                                   "", "Text Files (*.txt);;All Files (*)", 
                                                   options=options)                       
        data_csv = []          
                                                     
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data_csv = f.readlines()
            except Exception as e:
                try:
                    with open(file_path, 'r', encoding='charmap') as f:
                        data_csv = f.readlines()
                except Exception as e:
                    print("Error opening file:", e)
                   
        if self.radbutton_latency.isChecked():        
            data, jitter = latency_graph(data_csv)
            
        elif self.radbutton_throughput.isChecked():
            data, jitter = throughput_graph(data_csv)
            self.value_jitter_2 = self.findChild(QLabel, 'value_jitter_2')  
            self.value_jitter_2.setText("-")
        
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Please, select a test type.")
        
        chart_title = get_title(file_path)
        chart_comparison2 = self.generate_line_chart2(data, chart_title, data_csv)
        
        if chart_comparison2 is not None:
            self.value_max = self.findChild(QLabel, 'value_max_2')  
            self.value_max.setText(str(round(data.max(),2)))
            self.value_min = self.findChild(QLabel, 'value_min_2')  
            self.value_min.setText(str(round(data.min(),2)))
            self.value_mean = self.findChild(QLabel, 'value_mean_2') 
            self.value_mean.setText(str(round(data.mean(),2)))       
            
            if self.radbutton_latency.isChecked():     
                self.value_jitter = self.findChild(QLabel, 'value_jitter_2')  
                self.value_jitter.setText(str(round(jitter[0].mean(), 2)))
      
            try:
                self.button_export.disconnect()
                self.button_export.clicked.connect(lambda: self.goto_export(chart_comparison2, "Q5GA_comparison_graphic_" + chart_title.split(".")[0]))
            except:
                QtWidgets.QMessageBox.warning(self, "Error", "To export more graphics, use the 'Latency test' or the 'Throughput test' tabs.")
        
        return chart_comparison2
    
    def generate_line_chart2(self, data, chart_title, data_csv):
        plt.rcParams['lines.linewidth'] = 1
        self.figure = Figure()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_title(chart_title)
        
        if data.max() > 4*data.mean():
            ax.set_ylim(0.8*data.min(), 1.5*data.mean())
        else:
            pass
        
        chart_comparison2 = None
        
        try:
            chart_comparison2 = data.plot.line(ax=ax).get_figure()
            ax.set_xlabel("")
            self.canvas = FigureCanvas(self.figure)
            self.scene = QGraphicsScene()
            self.scene.addWidget(self.canvas)
            self.graphicsView2.setScene(self.scene)
     
            self.graphicsView2.fitInView(self.scene.itemsBoundingRect())
        except:
            if data_csv == []:
                QtWidgets.QMessageBox.warning(self, "Error", "Please select a file.")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Wrong file type.")
            
        return chart_comparison2
    
    
app = QApplication([])
    
if __name__ == '__main__':

    homescreen = HomeWindow()
    latencyscreen = LatencyWindow()
    throughputscreen = ThroughputWindow()
    comparisonscreen = ComparisonWindow()
    widget = QStackedWidget() 
    widget.addWidget(homescreen)
    widget.addWidget(latencyscreen)
    widget.addWidget(throughputscreen)
    widget.addWidget(comparisonscreen)
    widget.show()
    widget.setFixedHeight(650)
    widget.setFixedWidth(935)
    app.exec_()