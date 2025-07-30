# CPU/GPU Monitor

一个极简美观的 Windows CPU/GPU 温度与使用率监控工具，基于 Python + PyQt5。

A minimal and elegant Windows CPU/GPU temperature and usage monitor, built with Python + PyQt5.

---

## 功能特色 Features

- 实时显示 CPU/GPU 使用率与温度
- 极简深色主题，窗口可拖动、置顶
- 资源占用极低，界面美观
- 支持多 GPU（显示首块）

- Real-time display of CPU/GPU usage and temperature
- Minimal dark theme, draggable and always-on-top window
- Very low resource usage, beautiful UI
- Multi-GPU support (shows the first GPU)

---

## 截图 Screenshot


![Uploading 微信截图_20250730224101.png…]()

---

## 安装依赖 Installation

```bash
pip install -r requirements.txt
```

---

## 运行方法 How to Run

1. 下载并运行 [Open Hardware Monitor](https://openhardwaremonitor.org/)，并在其 Options 里勾选“Start web server on port 8085”。
2. Download and run [Open Hardware Monitor](https://openhardwaremonitor.org/), and enable "Start web server on port 8085" in Options.

2. 运行本程序 / Run this program:

```bash
python cpu_gpu_monitor.py
```

---

## 依赖 Dependencies

- Python 3.7+
- psutil
- GPUtil
- requests
- PyQt5

---

## 许可证 License

MIT License
