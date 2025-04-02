import json
import os
import glob
from config import COMMANDS_DIR

class CommandManager:
    def __init__(self):
        self.commands = {}
        self.load_commands()

    def load_commands(self):
        self.commands = {}
        os.makedirs(COMMANDS_DIR, exist_ok=True)
        for filepath in glob.glob(os.path.join(COMMANDS_DIR, '*.json')):
            category = os.path.splitext(os.path.basename(filepath))[0].title()
            with open(filepath, 'r', encoding='utf-8') as file:
                self.commands[category] = json.load(file)

    def refresh(self):
        self.load_commands()

    def search(self, query):
        query = query.lower()
        results = {}
        for category, cmds in self.commands.items():
            matches = {name: cmd for name, cmd in cmds.items()
                       if query in name.lower() or query in cmd['command'].lower() or query in cmd['description'].lower()}
            if matches:
                results[category] = matches
        return results
