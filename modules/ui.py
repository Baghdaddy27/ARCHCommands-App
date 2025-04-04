import sys
import os
import json
import pyperclip
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QSizePolicy, QFrame, QListWidget, 
    QListWidgetItem, QCheckBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from modules.command_manager import CommandManager
from modules.config import README_PATH

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
ICON_PATH = os.path.join(os.path.dirname(__file__), "../assets/ARCHMD.ico")
LOGO_PATH = os.path.join(ASSET_DIR, "ARCHMD.png")

class CommandReferenceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Arch Linux Command Reference")
        self.resize(1360, 750)
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.checkbox_layout = None
        self.select_all_checkbox = None
        self.json_checkboxes = []
        self.browse_widget = None
        self.command_manager = CommandManager()

        # Central widget
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Left panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "../assets/ARCHMD.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("<h2 style='white-space: normal;'>Arch Commands</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)

        author_label = QLabel("<small><i>Made by Baghdaddy27</i></small>")
        author_label.setAlignment(Qt.AlignCenter)

        left_panel.addWidget(logo_label)
        left_panel.addWidget(title_label)
        left_panel.addWidget(author_label)

        # Buttons
        browse_btn = QPushButton("📂 Browse Categories")
        search_btn = QPushButton("🔎 Search Commands")
        readme_btn = QPushButton("📖 View README")

        browse_btn.clicked.connect(self.show_browse)
        search_btn.clicked.connect(self.show_search)
        readme_btn.clicked.connect(self.show_readme)

        left_panel.addWidget(browse_btn)
        left_panel.addWidget(search_btn)
        left_panel.addWidget(readme_btn)
        left_panel.addStretch()

        # --- Import/Export Section ---
        import_label = QLabel("<b>Manage Commands</b>")
        import_btn = QPushButton("📥 Import Commands")
        export_btn = QPushButton("📤 Export Commands")

        import_btn.clicked.connect(self.import_commands)
        export_btn.clicked.connect(self.export_commands)

        left_panel.addWidget(import_label)
        left_panel.addWidget(import_btn)
        left_panel.addWidget(export_btn)

        # Right panel
        self.display_area = QScrollArea()
        self.display_area.setWidgetResizable(True)
        self.command_table = None

        # Assemble layout
        left_frame = QFrame()
        left_frame.setLayout(left_panel)
        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(self.display_area, 2)

    def show_browse(self):
        self.display_area.takeWidget()

        # Create container widget
        self.browse_widget = QWidget()
        browse_layout = QVBoxLayout(self.browse_widget)

        # Select/Deselect All checkbox
        self.select_all_checkbox = QCheckBox("Select / Deselect All")
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_checkboxes)
        browse_layout.addWidget(self.select_all_checkbox)

        # List checkboxes for each JSON file
        self.json_checkboxes = []
        json_files = self.command_manager.list_json_files()
        self.checkbox_layout = QVBoxLayout()

        for file in json_files:
            box = QCheckBox(file)
            self.json_checkboxes.append(box)
            self.checkbox_layout.addWidget(box)

        scroll_content = QWidget()
        scroll_content.setLayout(self.checkbox_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)
        browse_layout.addWidget(scroll_area)

        # Open Selected button
        open_btn = QPushButton("Open Selected")
        open_btn.clicked.connect(self.open_selected_jsons)
        browse_layout.addWidget(open_btn)

        self.display_area.setWidget(self.browse_widget)


    def show_readme(self):
        self.display_area.clear()
        if os.path.exists(README_PATH):
            with open(README_PATH, "r", encoding="utf-8") as f:
                content = f.read()
                self.display_area.setPlainText(content)
        else:
            self.display_area.setText("README.md not found.")

    def show_search(self):
        # Remove the previous widget inside display_area if it exists
        current_widget = self.display_area.widget()
        if current_widget:
            current_widget.deleteLater()

        # Create a new widget for the search functionality
        search_widget = QWidget()

        # Create a new layout for the search bar and results
        search_layout = QVBoxLayout()

        # Create a search input field
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search for commands...")

        # Create a search button
        search_button = QPushButton("Search")

        # Add the search input and search button to the layout
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)

        # Create a QTableWidget to display search results
        self.search_results_area = QTableWidget()
        self.search_results_area.setColumnCount(4)
        self.search_results_area.setHorizontalHeaderLabels(["Function", "Command", "Description", "Category"])

        # Add the results table to the layout
        search_layout.addWidget(self.search_results_area)

        # Create a container to display the layout
        search_widget.setLayout(search_layout)

        # Set the widget inside the display_area to the new search_widget
        self.display_area.setWidget(search_widget)

        # Connect the search button to the search method, passing only the input text
        search_button.clicked.connect(lambda: self.perform_search(search_input.text()))  # Only passing the text

    def perform_search(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self.display_area.setPlainText("Please enter a search query.")
            return

        # Search all JSON files (not limited to selected ones)
        search_results = self.command_manager.search(query)

        # Debugging: Ensure we have the correct search results
        print(f"Search Results: {search_results}")  # For debugging

        # Update the results table
        self.update_search_results(search_results)

    def update_search_results(self, results):
        # Clear the previous search results
        self.search_results_area.setRowCount(0)

        # If there are no results, inform the user
        if not results:
            self.search_results_area.setRowCount(1)
            self.search_results_area.setItem(0, 0, QTableWidgetItem("No results found"))
            return

        row = 0
        for category, commands in results.items():
            for name, details in commands.items():
                self.search_results_area.insertRow(row)
                self.search_results_area.setItem(row, 0, QTableWidgetItem(name))  # Function
                self.search_results_area.setItem(row, 1, QTableWidgetItem(details.get('command', '')))  # Command
                self.search_results_area.setItem(row, 2, QTableWidgetItem(details.get('description', '')))  # Description
                self.search_results_area.setItem(row, 3, QTableWidgetItem(category))  # Category
                row += 1

        self.search_results_area.resizeColumnsToContents()

    def toggle_all_checkboxes(self):
        checked = self.select_all_checkbox.isChecked()
        for box in self.json_checkboxes:
            box.setChecked(checked)

    def open_selected_jsons(self):
        selected_files = [box.text() for box in self.json_checkboxes if box.isChecked()]
        if not selected_files:
            self.display_area.setPlainText("⚠️ No files selected.")
            return

        data = self.command_manager.load_selected_files(selected_files)

        table = QTableWidget()
        self.command_table = table
        rows = sum(len(cmds) for cmds in data.values())
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Function", "Command", "Category (File)"])
        table.setRowCount(rows)

        row = 0
        for category, cmds in data.items():
            for name, detail in cmds.items():
                table.setItem(row, 0, QTableWidgetItem(name))  # Function name
                table.setItem(row, 1, QTableWidgetItem(detail.get("command", "")))
                table.setItem(row, 2, QTableWidgetItem(category))
                row += 1

        table.resizeColumnsToContents()
        self.display_area.setWidget(table)

    def import_commands(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or not all(
                isinstance(v, dict) and "command" in v and "description" in v for v in data.values()
            ):
                raise ValueError("Invalid JSON format. Must be a dictionary of command objects with 'command' and 'description'.")

            dest_path = os.path.expanduser(f"~/ARCHCommands/commands/{os.path.basename(file_path)}")
            shutil.copyfile(file_path, dest_path)

            self.command_manager.refresh()
            self.display_area.setText(f"✅ Successfully imported: {os.path.basename(file_path)}\nCategories refreshed.")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"❌ Failed to import JSON:\n{str(e)}")

    def export_commands(self):
        QMessageBox.information(self, "Coming Soon", "Export functionality will be added later.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommandReferenceApp()
    window.show()
    sys.exit(app.exec_())
