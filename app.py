"""
Video Markme - Main Application Entry Point
Desktop application for tracking players in videos and adding visual markers
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Video Markme")
    app.setOrganizationName("Video Markme")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


