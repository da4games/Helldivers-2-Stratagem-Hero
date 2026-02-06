from collector import DataCollector
from key_reader import NonBlockingKeyReader
import os
from rich.console import Console
import random


console = Console()


class stratagemHero():
    def __init__(self, all_rows):
        self.current_script_path = os.path.abspath(__file__)
        self.stratagems_directory = os.path.join(os.path.dirname(self.current_script_path), "stratagems.csv")
        self.mission_directory = os.path.join(os.path.dirname(self.current_script_path), "mission_stratagems.csv")
        self.all_rows = all_rows
        
        self.column_names = {
            "Department": 0,
            "Icon": 1,
            "Stratagem": 2,
            "Stratagem Codes": 3,
            "Cooldown": 4,
            "Cost": 5,
            "Unlock Level": 6,
            "Description": 7
        }
        
        self.mission_column_names = {
            "Type": 0,
            "Icon": 1,
            "Stratagem": 2,
            "Stratagem Codes": 3,
            "Description": 4
        }
        
        self.total_rows = 0
        for count in all_rows.values():
            self.total_rows += count
        
        console.print(f"stratagemHero initialized with {all_rows} stratagems.")
    
    def get_stratagem_table_entry_table_entry(self, index, column_name: str):
        if index <= self.total_rows:
            if index <= self.all_rows[0]:
                with open(self.stratagems_directory, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if index < len(lines):
                        row = lines[index].strip()
                        column_index = self.column_names[column_name]
                        return row.split(",")[column_index]
            
            elif index > self.all_rows[0]:
                with open(self.mission_directory, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if index - self.all_rows[0] < len(lines):
                        row = lines[index - self.all_rows[0]].strip()
                        column_index = self.mission_column_names[column_name] if not column_name == "Department" else self.mission_column_names["Type"]
                        return row.split(",")[column_index]

        return "Index out of range"
    
            
    def validate_stratagem_codes(self):
        # check if any index returns "None", an error or the header of the CSV file
        for i in range(self.total_rows):
            data = self.get_stratagem_table_entry_table_entry(i, "Stratagem Codes")
            
            if not "Stratagem" in str(data):
                console.print(f"Stratagem code at index {i}: {data}")
        
        console.print(f"All {self.total_rows} stratagem codes validated!")
        # This means we now have all stratagems available by indexes from 0 to total_rows and are ignoring the header correctly.
    
    
    def get_compatibility_mode(self):
        answer = input("Do these arrows look normal? 🡄 🡅 🡆 🡇    ")
        match answer.lower():
            case "yes" | "y":
                console.print("Good. Proceeding as normal.")
                self.compatibility_mode = False
            case "no" | "n":
                console.print("Enabling compatibility mode. This may cause some formatting issues, but should allow the game to run on a wider range of systems.")
                self.compatibility_mode = True
            case _:
                console.print("Invalid input, defaulting to compatibility mode.")
                self.compatibility_mode = True
        
        if self.compatibility_mode:
            answer = input("Do these arrow replacements look normal? < > ^ v    ")
            match answer.lower():
                case "yes" | "y":
                    console.print("Good. Proceeding with compatibility mode enabled.")
                case "no" | "n":
                    console.print("In this case: Tough luck. Exiting...")
                    os.system('pause')
                    exit(0)
                case _:
                    console.print("Invalid input. Exiting...")
                    os.system('pause')
                    exit(0)
    
    
    def parse_stratagem_code(self, index):
        arrow_code = ""
        normal_code = []
        code = self.get_stratagem_table_entry_table_entry(index, "Stratagem Codes")
        for part in code.split("|"):    
            match part.strip():
                case _ if "Up" in part:
                    arrow_code += "🡅" if not self.compatibility_mode else "^"
                    normal_code.append("UP")
                case _ if "Down" in part:
                    arrow_code += "🡇" if not self.compatibility_mode else "v"
                    normal_code.append("DOWN")
                case _ if "Left" in part:
                    arrow_code += "🡄" if not self.compatibility_mode else "<"
                    normal_code.append("LEFT")
                case _ if "Right" in part:
                    arrow_code += "🡆" if not self.compatibility_mode else ">"
                    normal_code.append("RIGHT")
        return arrow_code, normal_code
    
    
    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        stratagem = random.randint(0, self.total_rows - 1)
        
        current_code_index = 0
        arrow_code, normal_code = self.parse_stratagem_code(stratagem)
        console.print(f"{self.get_stratagem_table_entry_table_entry(stratagem, 'Stratagem')}", highlight=False)
        prefix = arrow_code[:current_code_index]
        rest = arrow_code[current_code_index:]
        spaced_prefix = " ".join(list(prefix)) if prefix else ""
        spaced_rest = " ".join(list(rest)) if rest else ""
        sep = " " if spaced_prefix and spaced_rest else ""
        console.print(f"[yellow]{spaced_prefix}[/yellow]{sep}{spaced_rest}")
        
        with NonBlockingKeyReader() as reader:
            while current_code_index <= len(arrow_code) - 1:
                update = False
                # Check if it's a key press event with a valid scan code
                input = reader.read_key()
                if input:
                    key = input
                    
                    if key == 'DOWN' and normal_code[current_code_index] == "DOWN":
                        current_code_index += 1
                        update = True
                    elif key == 'UP' and normal_code[current_code_index] == "UP":
                        current_code_index += 1
                        update = True
                    elif key == 'RIGHT' and normal_code[current_code_index] == "RIGHT":
                        current_code_index += 1
                        update = True
                    elif key == 'LEFT' and normal_code[current_code_index] == "LEFT":
                        current_code_index += 1
                        update = True
                    elif key == 'w' and normal_code[current_code_index] == "UP":
                        current_code_index += 1
                        update = True
                    elif key == 'a' and normal_code[current_code_index] == "LEFT":
                        current_code_index += 1
                        update = True
                    elif key == 's' and normal_code[current_code_index] == "DOWN":
                        current_code_index += 1
                        update = True
                    elif key == 'd' and normal_code[current_code_index] == "RIGHT":
                        current_code_index += 1
                        update = True
                    else:
                        print(f"Pressed key: {repr(key)} does not match expected input for current code index {current_code_index}. Expected: {repr(normal_code[current_code_index])}")
                        continue
                
                if update:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    console.print(self.get_stratagem_table_entry_table_entry(stratagem, "Stratagem"), highlight=False)
                    # Print with spaces between each arrow in a single call.
                    # Split the string into characters and join with spaces so
                    # multi-arrow strings display as: 🡄 🡅 🡆 🡇
                    prefix = arrow_code[:current_code_index]
                    rest = arrow_code[current_code_index:]
                    spaced_prefix = " ".join(list(prefix)) if prefix else ""
                    spaced_rest = " ".join(list(rest)) if rest else ""
                    # If both parts exist, ensure there's a single separator.
                    sep = " " if spaced_prefix and spaced_rest else ""
                    console.print(f"[yellow]{spaced_prefix}[/yellow]{sep}{spaced_rest}")
    

if __name__ == "__main__":
    console.print("Loading stratagems from the wiki . . .")
    collector = DataCollector("https://helldivers.wiki.gg/wiki/Stratagems")
    all_rows = collector.get_stratagems()
    console.print("Loading game now . . .")
    
    for key, value in all_rows.items():
        all_rows[key] = value - 1  # Subtract 1 to account for header row in each CSV file
        
    game = stratagemHero(all_rows)
    console.print("Game class initialised!")
    
    game.validate_stratagem_codes()    
    console.print("Game loaded correctly!")
    
    os.system('pause')
    
    os.system('cls' if os.name == 'nt' else 'clear')
    game.get_compatibility_mode()
    
    game.run()