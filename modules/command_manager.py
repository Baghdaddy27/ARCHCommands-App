import json
import os
import glob
from modules.config import COMMANDS_DIR

class CommandManager:
    def __init__(self):
        self.commands_dir = os.path.expanduser("~/ARCHCommands/commands")
        self.commands = {}
        self.load_commands()

    def load_commands(self):
        """Load all commands from the JSON files in the commands directory."""
        self.commands = {}
        os.makedirs(COMMANDS_DIR, exist_ok=True)
        for filepath in glob.glob(os.path.join(COMMANDS_DIR, '*.json')):
            category = os.path.splitext(os.path.basename(filepath))[0].title()
            with open(filepath, 'r', encoding='utf-8') as file:
                self.commands[category] = json.load(file)

    def list_json_files(self):
        """Return a list of all JSON files in the commands directory."""
        return sorted(f for f in os.listdir(self.commands_dir) if f.endswith(".json"))

    def refresh(self):
        """Refresh the loaded commands from the JSON files."""
        self.load_commands()

    def search(self, query, selected_jsons=None):
        query = query.lower()
        results = {}

        # If specific files are selected, use them; otherwise, search through all files
        json_files = selected_jsons if selected_jsons else self.list_json_files()

        for file in json_files:
            with open(os.path.join(self.commands_dir, file), "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Search within the file's commands
            for category, cmds in data.items():
                matches = {
                    name: cmd for name, cmd in cmds.items()
                    if query in name.lower() or query in cmd.get('command', '').lower() or query in cmd.get('description', '').lower()
                }
                if matches:
                    results[category] = matches

        return results
