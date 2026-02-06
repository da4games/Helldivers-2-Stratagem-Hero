from collector import DataCollector
import os


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
        
        print(f"stratagemHero initialized with {all_rows} stratagems.")
    
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
            data = self.get_stratagem_table_entry_code(i)
            
            if not "Stratagem" in str(data):
                print(f"Stratagem code at index {i}: {data}")
        
        print(f"All {self.total_rows} stratagem codes validated!")
        # This means we now have all stratagems available by indexes from 0 to total_rows and are ignoring the header correctly.
    
    
    def get_compatibility_mode(self):
        answer = input("Do these arrows look normal? 🡄 🡅 🡆 🡇    ")
        match answer.lower():
            case "yes" | "y":
                print("Good. Proceeding as normal.")
                self.compatibility_mode = False
            case "no" | "n":
                print("Enabling compatibility mode. This may cause some formatting issues, but should allow the game to run on a wider range of systems.")
                self.compatibility_mode = True
            case _:
                print("Invalid input, defaulting to compatibility mode.")
                self.compatibility_mode = True
        
        if self.compatibility_mode:
            answer = input("Do these arrow replacements look normal? < > ^ v    ")
            match answer.lower():
                case "yes" | "y":
                    print("Good. Proceeding with compatibility mode enabled.")
                case "no" | "n":
                    print("In this case: Tough luck. Exiting...")
                    os.system('pause')
                    exit(0)
                case _:
                    print("Invalid input. Exiting...")
                    os.system('pause')
                    exit(0)
    
    
    def parse_stratagem_code(self, index):
        arrow_code = ""
        code = self.get_stratagem_table_entry_table_entry(index, "Stratagem Codes")
        for part in code.split("|"):    
            match part.strip():
                case _ if "Up" in part:
                    arrow_code += "🡅 " if not self.compatibility_mode else "^ "
                case _ if "Down" in part:
                    arrow_code += "🡇 " if not self.compatibility_mode else "v "
                case _ if "Left" in part:
                    arrow_code += "🡄 " if not self.compatibility_mode else "< "
                case _ if "Right" in part:
                    arrow_code += "🡆 " if not self.compatibility_mode else "> "
        return arrow_code
    
    
    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Welcome to Stratagem Hero!")
        print(self.parse_stratagem_code(1))
    

if __name__ == "__main__":
    print("Loading stratagems from the wiki...")
    collector = DataCollector("https://helldivers.wiki.gg/wiki/Stratagems")
    all_rows = collector.get_stratagems()
    print("Loading game now...")
    
    for key, value in all_rows.items():
        all_rows[key] = value - 1  # Subtract 1 to account for header row in each CSV file
        
    game = stratagemHero(all_rows)
    print("Game class initialised!")
    
    game.validate_stratagem_codes()    
    print("Game loaded correctly!")
    
    os.system('pause')
    
    os.system('cls' if os.name == 'nt' else 'clear')
    game.get_compatibility_mode()
    
    game.run()