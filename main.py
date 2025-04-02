from textual.app import App, ComposeResult
from textual.containers import Grid, VerticalScroll
from textual.widgets import Header, Footer, Button, Label
import json
import os
import pyperclip
from config import COMMANDS_DIR

class CommandUI(App):
    TITLE = "Arch Linux Command Reference"

    def __init__(self):
        super().__init__()
        self.commands = self.load_commands()

    def load_commands(self):
        """Loads commands dynamically from JSON files in COMMANDS_DIR."""
        commands = {}
        if not os.path.exists(COMMANDS_DIR):
            os.makedirs(COMMANDS_DIR)

        for file in os.listdir(COMMANDS_DIR):
            if file.endswith(".json"):
                category = file.replace(".json", "").title()
                with open(os.path.join(COMMANDS_DIR, file), "r", encoding="utf-8") as f:
                    commands[category] = json.load(f)
        return commands

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.main_menu()
        yield Footer()

    def main_menu(self):
        """Creates the main menu UI."""
        return Grid(
            Button("🔎 Search Commands", id="search"),
            Button("📂 View Categories", id="categories"),
            Button("⬆️ Import Commands", id="import"),
            Button("⬇️ Export Commands", id="export"),
            Button("📖 README", id="readme"),
            Button("❌ Quit", id="quit"),
            classes="menu"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles all button interactions properly."""
        button_id = event.button.id

        if button_id == "quit":
            self.exit()
        elif button_id == "categories":
            self.show_categories()
        elif button_id.startswith("category_"):
            category_name = button_id.replace("category_", "").replace("_", " ")
            self.show_commands(category_name)
        elif button_id.startswith("cmd_"):
            command_name = button_id.replace("cmd_", "").replace("_", " ")
            self.copy_command_to_clipboard(command_name)
        elif button_id == "search":
            self.show_search()
        elif button_id == "import":
            self.show_import()
        elif button_id == "export":
            self.show_export()
        elif button_id == "readme":
            self.show_readme()

    def show_categories(self):
        """Displays available command categories properly."""
        self.clear()
        self.mount(Header("Select a Category"), VerticalScroll(*[
            Button(category, id=f"category_{category.lower().replace(' ', '_')}") for category in self.commands.keys()
        ]), Footer())

    def show_commands(self, category):
        """Displays commands within the selected category properly."""
        self.clear()
        self.mount(Header(f"Category: {category}"), VerticalScroll(*[
            Button(f"**{command}**\n{details.get('description', 'No description available.')}", 
                   id=f"cmd_{command.lower().replace(' ', '_')}")
            for command, details in self.commands.get(category, {}).items()
        ]), Footer())

    def copy_command_to_clipboard(self, command_name):
        """Copies the selected command to the clipboard."""
        for category, cmds in self.commands.items():
            for cmd_name, cmd_details in cmds.items():
                if command_name.lower() == cmd_name.lower():
                    pyperclip.copy(cmd_details['command'])
                    self.notify(f"Copied: {cmd_details['command']}", severity="info")
                    return

    def show_search(self):
        """Placeholder for search functionality (to be implemented)."""
        self.clear()
        self.mount(Header("🔎 Search Commands (Coming Soon)"), Button("⬅ Back to Menu", id="back_to_menu"), Footer())

    def show_import(self):
        """Placeholder for import functionality."""
        self.clear()
        self.mount(Header("⬆ Import Commands (Coming Soon)"), Button("⬅ Back to Menu", id="back_to_menu"), Footer())

    def show_export(self):
        """Placeholder for export functionality."""
        self.clear()
        self.mount(Header("⬇ Export Commands (Coming Soon)"), Button("⬅ Back to Menu", id="back_to_menu"), Footer())

    def show_readme(self):
        """Displays README file content."""
        readme_path = os.path.expanduser("~/ARCHCommands/README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as file:
                readme_content = file.read()
        else:
            readme_content = "README file not found."

        self.clear()
        self.mount(Header("📖 README"), Label(readme_content), Button("⬅ Back to Menu", id="back_to_menu"), Footer())

    def on_mount(self):
        """Handles when UI loads, ensuring screen refresh works."""
        self.show_main_menu()

    def show_main_menu(self):
        """Resets UI back to the main menu."""
        self.clear()
        self.mount(Header(), self.main_menu(), Footer())

if __name__ == "__main__":
    app = CommandUI()
    app.run()
