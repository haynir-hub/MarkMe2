"""
Player Selector - Dialog for selecting player marker style and name
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class PlayerSelector(QDialog):
    """Dialog for configuring player marker"""
    
    # Signal emitted when player is confirmed
    player_confirmed = pyqtSignal(str, str)  # name, style
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Player Marker")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # Player name
        name_group = QGroupBox("Player Name (Optional)")
        name_layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter player name...")
        name_layout.addWidget(self.name_input)
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Marker style
        style_group = QGroupBox("Marker Style")
        style_layout = QVBoxLayout()
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "🔺 Arrow above head",
            "⭕ 3D Floor Hoop (yellow)",
            "🔷 Blue Rectangle with corners",
            "💡 Light Column (alien beam)",
            "💠 Neon Ring (white glowing)",
            "💫 Pulse Circle (orange animated)",
            "🌈 Gradient Ring (purple with rotating glow)",
            "🎯 Dynamic Arrow (bouncing, sharp)",
            "⬡ Hexagon (futuristic)",
            "🎮 Crosshair (tactical targeting)",
            "🔥 Burning Flame (above head)"
        ])
        
        # Add description label that updates based on selection
        self.style_description = QLabel()
        self.style_description.setWordWrap(True)
        self.style_description.setStyleSheet("color: gray; font-size: 10px;")
        self.style_combo.currentIndexChanged.connect(self._update_description)
        self._update_description()  # Set initial description
        
        style_layout.addWidget(self.style_combo)
        style_layout.addWidget(self.style_description)
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.clicked.connect(self._on_confirm)
        self.confirm_btn.setDefault(True)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.confirm_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _update_description(self):
        """Update style description based on selection"""
        descriptions = {
            0: "Beautiful yellow arrow pointing down at player from above",
            1: "3D elliptical yellow hoop on floor - professional sports broadcast style",
            2: "Clean blue rectangle with corner highlights - modern & professional",
            3: "Light column from ceiling (like alien spaceship beam) - dramatic effect",
            4: "Modern white neon ring with glowing effect - eye-catching and stylish",
            5: "Orange pulsing circle that breathes - smooth animated effect",
            6: "Purple gradient ring with rotating glow - thick and prominent",
            7: "Sharp bouncing dynamic arrow - elegant and animated",
            8: "Futuristic hexagon outline - sci-fi tactical look",
            9: "Tactical crosshair targeting system - game-style precision",
            10: "Burning flame above player's head - perfect for hot players!"
        }
        desc = descriptions.get(self.style_combo.currentIndex(), "")
        self.style_description.setText(desc)
    
    def _on_confirm(self):
        """Handle confirm button click"""
        name = self.name_input.text().strip()
        if not name:
            name = f"Player {id(self)}"  # Default name
        
        style_map = {
            0: "arrow",
            1: "circle",
            2: "rectangle",
            3: "spotlight",
            4: "neon_ring",
            5: "pulse",
            6: "gradient",
            7: "dynamic_arrow",
            8: "hexagon",
            9: "crosshair",
            10: "flame"
        }
        style = style_map.get(self.style_combo.currentIndex(), "rectangle")
        
        self.player_confirmed.emit(name, style)
        self.accept()
    
    def get_selected_style(self) -> str:
        """Get selected marker style"""
        style_map = {
            0: "arrow",
            1: "circle",
            2: "rectangle",
            3: "spotlight",
            4: "outline"
        }
        return style_map.get(self.style_combo.currentIndex(), "rectangle")


