#!/usr/bin/env python3

import sys
import json
import webbrowser
import PyQt5
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QMainWindow, QListWidget, QStackedWidget,
    QListWidgetItem, QFrame, QProgressBar
)
from PyQt5.QtGui import QFont, QColor, QIcon, QCursor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve


class BluetoothApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bluetooth Scanner")

        self.adjustSize()
        self.setGeometry(200, 200, 900, 800)  # (x, y, width, height)

        self.setStyleSheet("background-color: #1e1e2f; color: white;")
        
        # Create and show preloader before initializing UI
        self.setup_preloader()
        self.show_preloader()
        
        # The initialize_app will now be called from update_progress when progress reaches 100%
        # No need for this timer anymore:
        # QTimer.singleShot(1500, self.initialize_app)

    def setup_preloader(self):
        # Create preloader widget
        self.preloader_widget = QWidget(self)
        self.preloader_widget.setGeometry(0, 0, self.width(), self.height())
        self.preloader_widget.setStyleSheet("background-color: #1e1e2f;")
        
        # Create layout for preloader
        preloader_layout = QVBoxLayout(self.preloader_widget)
        preloader_layout.setAlignment(Qt.AlignCenter)
        
        # Add app title
        title_label = QLabel("Bluetooth Scanner")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #5865F2; margin-bottom: 30px;")
        title_label.setAlignment(Qt.AlignCenter)
        preloader_layout.addWidget(title_label)
        
        # Add loading text
        loading_label = QLabel("Loading...")
        loading_label.setFont(QFont("Arial", 14))
        loading_label.setStyleSheet("color: #aab2bb; margin-bottom: 20px;")
        # loading_label.setAlignment(Qt.AlignCenter)
        preloader_layout.addWidget(loading_label)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #23272A;
                border-radius: 5px;
                border: 1px solid #5865F2;
            }
            QProgressBar::chunk {
                background-color: #5865F2;
                border-radius: 5px;
            }
        """)
        preloader_layout.addWidget(self.progress_bar)
        
        # Hide preloader initially
        self.preloader_widget.hide()

    def show_preloader(self):
        self.preloader_widget.show()
        
        # Animate progress bar
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(30)
        self.progress_value = 0

    def update_progress(self):
        self.progress_value += 2
        self.progress_bar.setValue(self.progress_value)
        
        if self.progress_value >= 100:
            self.progress_timer.stop()
            # Initialize the app when progress reaches 100%
            QTimer.singleShot(200, self.initialize_app)

    def hide_preloader(self):
        # Make sure timer is stopped
        if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
            self.progress_timer.stop()
            
        # Create fade out animation
        self.fade_out = QPropertyAnimation(self.preloader_widget, b"windowOpacity")
        self.fade_out.setDuration(500)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.OutQuad)
        self.fade_out.finished.connect(self.preloader_widget.hide)
        self.fade_out.start()

    def initialize_app(self):
        # Initialize the main UI
        self.initUI()
        # Hide the preloader
        self.hide_preloader()

    def initUI(self):
        main_layout = QHBoxLayout()

        # === Sidebar (Navigatie) ===
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(250)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2f;
                color: white;
            }
            QListWidget {
                background-color: #23272A;
                color: white;
                font-size: 17px;
                border: 2px solid #5865F2;
                padding: 5px;
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
            }
            QListWidget::item {
                padding: 15px;
                margin: 5px 0;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #5865F2;
                border-left: 5px solid white;
                font-weight: bold;
            }
            QListWidget::item:hover {
                background-color: #3A3F44;
            }
            QPushButton {
                background-color: #5865F2;
                color: white;
                font-size: 15px;
                padding: 10px;
                margin: 10px 0;
                border-radius: 8px;
                border: 2px solid #4a5bc8;
            }
            QPushButton:hover {
                background-color: #4a5bc8;
                border: 2px solid #3a4bb5;
            }
            QPushButton:pressed {
                background-color: #3a4bb5;
                border: 2px solid #2a3aa2;
            }
            QLabel {
                color: #aab2bb;
                padding: 10px;
                font-size: 17px;
            }
            QListWidget::item:selected {
                background-color: #7289DA;
            }
        """)


        # Voeg iconen toe met tekst aan de sidebar
        home_item = QListWidgetItem(QIcon("home.png"), "🏠 Home")
        data_item = QListWidgetItem(QIcon("data.png"), "📡 Data")
        
        self.sidebar.addItem(home_item)
        self.sidebar.addItem(data_item)

        self.sidebar.currentRowChanged.connect(self.switch_page)

        # === Pages ===
        self.pages = QStackedWidget()

        # === Home-pagina ===
        self.home_page = QWidget()
        home_layout = QVBoxLayout()

        intro_text = QLabel("Welkom bij de Bluetooth Scanner!\nMaak verbinding en ontdek apparaten in de buurt.")
        intro_text.setFont(QFont("Arial", 35, QFont.Bold))
        intro_text.setStyleSheet("color: #aab2bb; margin-top:10px; margin-bottom:10px;")
        home_layout.addWidget(intro_text)

        # Alinea 1: Over de Bluetooth Scanner
        scanner_info = QLabel(
            "Deze Bluetooth Scanner detecteert apparaten in de buurt en laat je de signaalsterkte (RSSI) zien. "
            "Handig om te bepalen hoe dichtbij een apparaat is en of het actief signalen uitzendt. "
            "Dit helpt bij netwerkbeheer, debugging en beveiligingstests."
        )
        # scanner_info.setFont(QFont("Arial"))
        scanner_info.setWordWrap(True)
        scanner_info.setStyleSheet("color: #d1d1e0; padding: 10px 20px;")
        home_layout.addWidget(scanner_info)

        # Alinea 2: Hacken & MAC-Spoofing
        hacking_info = QLabel(
            "Bluetooth-hacken wordt vaak gebruikt voor penetratietests en beveiligingsonderzoek. "
            "Een belangrijke tool hierbij is 'macchanger', waarmee je het MAC-adres van je apparaat kunt wijzigen. "
            "Dit maakt het moeilijker om getraceerd te worden en helpt bij het omzeilen van filters die apparaten blokkeren op basis van hun MAC-adres."
        )
        hacking_info.setWordWrap(True)
        hacking_info.setStyleSheet("color: #d1d1e0; padding: 10px 20px;")
        home_layout.addWidget(hacking_info)


        self.btn_tips = QPushButton("📌 Tips over Bluetooth")
        self.btn_aircrack = QPushButton("🔧 Aircrack-ng Info")
        self.btn_kali = QPushButton("🐉 Kali Linux Website")

        self.btn_tips.setStyleSheet("""
            background-color: #5865F2;
            color: white;
            font-size: 16px;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            margin-top: 200px;
        """)
        self.btn_aircrack.setStyleSheet("""
            background-color: #5865F2;
            color: white;
            font-size: 16px;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        """)
        self.btn_kali.setStyleSheet("""
            background-color: #5865F2;
            color: white;
            font-size: 16px;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        """)

        self.btn_tips.clicked.connect(lambda: self.open_link("https://www.bluetooth.com/learn-about-bluetooth/"))
        self.btn_aircrack.clicked.connect(lambda: self.open_link("https://www.aircrack-ng.org/"))
        self.btn_kali.clicked.connect(lambda: self.open_link("https://www.kali.org/"))

        # Voeg cursor pointer toe voor knoppen
        self.btn_tips.setCursor(Qt.PointingHandCursor)
        self.btn_aircrack.setCursor(Qt.PointingHandCursor)
        self.btn_kali.setCursor(Qt.PointingHandCursor)

        home_layout.addWidget(self.btn_tips)
        home_layout.addWidget(self.btn_aircrack)
        home_layout.addWidget(self.btn_kali)

        self.home_page.setLayout(home_layout)
        self.pages.addWidget(self.home_page)

        # === Data-pagina ===
        self.data_page = QWidget()
        data_layout = QVBoxLayout()

        data_intro = QLabel("🔍 Gevonden Bluetooth-apparaten:")
        data_intro.setFont(QFont("Arial", 12, QFont.Bold))
        data_intro.setStyleSheet("color: #aab2bb; padding: 10px 20px; text-align: center;")
        data_layout.addWidget(data_intro)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { background-color: #23272A; color: white; border-radius: 5px; }
            QListWidget::item-selected { background-color: #7289DA; }
        """)
        data_layout.addWidget(self.list_widget)

        self.button = QPushButton("🔄 Opnieuw laden")
        self.button.setStyleSheet("""
            background-color: #7289DA;
            color: white;
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
            margin: 20px 0;
        """)
        self.button.clicked.connect(self.load_data)

        # Voeg cursor pointer toe voor de "Opnieuw laden" knop
        self.button.setCursor(Qt.PointingHandCursor)
        data_layout.addWidget(self.button)

        self.data_page.setLayout(data_layout)
        self.pages.addWidget(self.data_page)

        # === Layouten combineren ===
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        intro_text.setObjectName("intro_text")
        scanner_info.setObjectName("paragraph")
        hacking_info.setObjectName("paragraph")

        self.load_data()

    def open_link(self, url):
        webbrowser.open(url)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    def load_data(self):
        try:
            with open("bluetooth_devices.json", "r") as file:
                data = json.load(file)

            self.list_widget.clear()

            # Sorteren op RSSI van sterk naar zwak
            data.sort(key=lambda x: x.get("rssi", -100), reverse=False)

            for device in data:
                mac = device.get("mac", "Onbekend")
                name = device.get("name", "Onbekend")
                rssi = device.get("rssi", "N/A")
                color = self.get_rssi_color(rssi)
                item_text = f"{name} ({mac}) - 🔋 Signaal: {rssi} dBm"

                item = QListWidgetItem(item_text)
                item.setForeground(color)
                self.list_widget.addItem(item)

        except (FileNotFoundError, json.JSONDecodeError):
            self.list_widget.addItem("❌ Geen geldige data gevonden.")

    def get_rssi_color(self, rssi):
        if not rssi.lstrip("-").isdigit():
            return QColor("#808080")
            
        rssi_int = int(rssi)    
        if rssi_int >= -42:
            return QColor("#00FF00")  # Groen (zeer sterk signaal)
        elif rssi_int >= -50:
            return QColor("#FFFF00")  # Geel (goed signaal)
        elif rssi_int >= -65:
            return QColor("#FFA500")  # Oranje (matig signaal)
        else:
            return QColor("#FF0000")  # Rood (zwak signaal)
        


        
    def resizeEvent(self, event):
        # Update preloader size and position to match window
        if hasattr(self, 'preloader_widget'):
            self.preloader_widget.setGeometry(0, 0, self.width(), self.height())
            
        # Check if pages attribute exists before trying to access it
        if not hasattr(self, 'pages'):
            # If pages doesn't exist yet (during preloader), just call the parent method
            super().resizeEvent(event)
            return
            
        # Rest of the existing resizeEvent code
        # Haal de breedte van het venster op
        width = self.width()

        # Bereken een schaalfactor voor de fontgrootte
        base_size = 16  # Startgrootte
        scale_factor = width / 1000  
        new_size = max(int(base_size * scale_factor), 20)  

        # Lettergroottes instellen
        intro_size = max(int(25 * scale_factor), 35)  # Minimaal 25px
        paragraph_size = max(int(17 * scale_factor), 25)  # Minimaal 20px

        # Pas stijlen toe op de tekst
        self.pages.setStyleSheet(f"""
            QLabel#intro_text {{
                font-size: {intro_size}px;
            }}
            QLabel#paragraph {{
                font-size: {paragraph_size}px;
            }}
        """)

        # Pas de lettergrootte toe op sidebar en labels
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                font-size: {new_size}px;
            }}
        """)
        # self.pages.setStyleSheet(f"""
        #     QLabel {{
        #         font-size: {new_size}px;
        #     }}
        # """)

        # Pas de lettergrootte toe op de knoppen
        self.btn_tips.setStyleSheet(f"""
            background-color: #5865F2;
            color: white;
            font-size: {new_size}px;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        """)
        self.btn_aircrack.setStyleSheet(f"""
            background-color: #5865F2;
            color: white;
            font-size: {new_size}px;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        """)
        self.btn_kali.setStyleSheet(f"""
            background-color: #5865F2;
            color: white;
            font-size: {new_size}px;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        """)
        self.button.setStyleSheet(f"""
            background-color: #7289DA;
            color: white;
            font-size: {new_size}px;
            padding: 10px;
            border-radius: 5px;
            margin: 20px 0;
        """)

        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BluetoothApp()
    window.showNormal()  # Zorg ervoor dat het venster niet gemaximaliseerd start
    sys.exit(app.exec_())
