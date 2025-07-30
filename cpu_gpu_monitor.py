import sys
import psutil
import GPUtil
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QFont

class DataWorker(QThread):
    data_ready = pyqtSignal(float, str, str, str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.paused = False
        psutil.cpu_percent(interval=None)
    def run(self):
        while self.running:
            if not self.paused:
                cpu_usage = psutil.cpu_percent(interval=None)
                cpu_temp = self.get_cpu_temp()
                gpu_usage, gpu_temp = self.get_gpu_info()
                self.data_ready.emit(cpu_usage, cpu_temp, gpu_usage, gpu_temp)
            self.msleep(5000)
    def stop(self):
        self.running = False
        self.wait()
    def pause(self):
        self.paused = True
    def resume(self):
        self.paused = False
    def get_cpu_temp(self):
        try:
            response = requests.get('http://localhost:8085/data.json', timeout=1)
            data = response.json()
            for hardware in data['Children'][0]['Children']:
                if hardware['Text'].startswith('CPU'):
                    for sensor in hardware['Children'][0]['Children']:
                        if sensor['Text'].startswith('Temperature'):
                            return str(sensor['Value'])
        except Exception:
            return "N/A"
        return "N/A"
    def get_gpu_info(self):
        gpus = GPUtil.getGPUs()
        if not gpus:
            return "N/A", "N/A"
        gpu = gpus[0]
        return f"{gpu.load * 100:.1f}", f"{gpu.temperature}"

class MonitorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(220, 90)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(2)
        # 设置窗体背景色为深色
        self.setStyleSheet("background: #23272e;")

        info_layout = QGridLayout()
        info_layout.setSpacing(1)
        label_font = QFont("Segoe UI", 9)
        value_font = QFont("Segoe UI", 11, QFont.Bold)

        # CPU
        cpu_usage_text = QLabel("CPU")
        cpu_usage_text.setFont(label_font)
        cpu_usage_text.setStyleSheet("color: #bfc7d5;")
        self.cpu_usage_label = QLabel("--%")
        self.cpu_usage_label.setFont(value_font)
        self.cpu_usage_label.setStyleSheet("color: #4fc3f7;")

        cpu_temp_text = QLabel("温度")
        cpu_temp_text.setFont(label_font)
        cpu_temp_text.setStyleSheet("color: #bfc7d5;")
        self.cpu_temp_label = QLabel("--°C")
        self.cpu_temp_label.setFont(value_font)

        # GPU
        gpu_usage_text = QLabel("GPU")
        gpu_usage_text.setFont(label_font)
        gpu_usage_text.setStyleSheet("color: #bfc7d5;")
        self.gpu_usage_label = QLabel("--%")
        self.gpu_usage_label.setFont(value_font)
        self.gpu_usage_label.setStyleSheet("color: #4fc3f7;")

        gpu_temp_text = QLabel("温度")
        gpu_temp_text.setFont(label_font)
        gpu_temp_text.setStyleSheet("color: #bfc7d5;")
        self.gpu_temp_label = QLabel("--°C")
        self.gpu_temp_label.setFont(value_font)

        info_layout.addWidget(cpu_usage_text, 0, 0)
        info_layout.addWidget(self.cpu_usage_label, 0, 1)
        info_layout.addWidget(cpu_temp_text, 0, 2)
        info_layout.addWidget(self.cpu_temp_label, 0, 3)
        info_layout.addWidget(gpu_usage_text, 1, 0)
        info_layout.addWidget(self.gpu_usage_label, 1, 1)
        info_layout.addWidget(gpu_temp_text, 1, 2)
        info_layout.addWidget(self.gpu_temp_label, 1, 3)

        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        info_widget.setStyleSheet("""
            QWidget {
                background: #2d323b;
                border-radius: 4px;
            }
            QLabel {
                color: #bfc7d5;
            }
        """)
        main_layout.addWidget(info_widget)

        self.setLayout(main_layout)
        self._drag_pos = None

        self.worker = DataWorker()
        self.worker.data_ready.connect(self.update_info)
        self.worker.start()

    def update_info(self, cpu_usage, cpu_temp, gpu_usage, gpu_temp):
        self.cpu_usage_label.setText(f"{cpu_usage}%")
        self.gpu_usage_label.setText(f"{gpu_usage}%")
        def color_temp(val):
            try:
                v = float(val)
                if v >= 80:
                    return "#ff5252"  # 红色
                elif v >= 70:
                    return "#ffb300"  # 橙色
                else:
                    return "#4fc3f7"  # 蓝色
            except:
                return "#bfc7d5"
        self.cpu_temp_label.setText(f"{cpu_temp}°C")
        self.cpu_temp_label.setStyleSheet(f"color: {color_temp(cpu_temp)};")
        self.gpu_temp_label.setText(f"{gpu_temp}°C")
        self.gpu_temp_label.setStyleSheet(f"color: {color_temp(gpu_temp)};")

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.worker.pause()
            else:
                self.worker.resume()
        super().changeEvent(event)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    def mouseReleaseEvent(self, event):
        self._drag_pos = None

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MonitorWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "错误", str(e))