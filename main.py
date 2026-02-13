from collector import DataCollector
from key_reader import getch
import os
from rich.console import Console
import random
import pandas as pd
import pygame
import sys
from pathlib import Path

# Add tools directory to path for imports
tools_dir = os.path.join(os.path.dirname(__file__), "tools")
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

from convert_svgs import find_inkscape, convert_svg_to_png


console = Console()


class ImageLoader:
    """Loads and scales images for pygame, with SVG support and caching"""

    def __init__(self, search_dirs=None):
        """
        Initialize the ImageLoader

        Args:
            search_dirs: List of directories to search for images. If None, uses default dirs.
        """

        stratagem_icons_dir = os.path.join(
            os.path.dirname(__file__), "resources", "stratagem_icons"
        )
        arrows_dir = os.path.join(os.path.dirname(__file__), "resources", "arrows")
        cache_dir = os.path.join(os.path.dirname(__file__), ".svg_cache")

        self.search_dirs = search_dirs or [stratagem_icons_dir, arrows_dir]
        self.cache_dir = cache_dir
        self.inkscape_path = None  # Lazily initialized on first SVG conversion

        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _convert_svg_to_png(self, svg_path):
        """Convert SVG file to PNG and cache it using shared converter"""
        svg_name = os.path.basename(svg_path)
        cache_file = os.path.join(self.cache_dir, svg_name.replace(".svg", ".png"))

        # Check if PNG is already cached
        if not os.path.exists(cache_file):
            # Lazily find Inkscape on first conversion
            if self.inkscape_path is None:
                self.inkscape_path = find_inkscape()
                if not self.inkscape_path:
                    raise FileNotFoundError(
                        "Inkscape not found. Please install Inkscape from https://inkscape.org/release/"
                    )
            
            # Use the shared convert_svg_to_png function
            convert_svg_to_png(svg_path, cache_file, self.inkscape_path)

        return cache_file

    def _find_image(self, filename):
        """Find image file in search directories"""
        for directory in self.search_dirs:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
        raise FileNotFoundError(f"Image '{filename}' not found in search directories")

    def load(self, filename, size=None, scale=None):
        """
        Load and scale an image

        Args:
            filename: Name of the image file (e.g., 'Stratagem_Arrow_Upsvg.svg')
            size: Tuple (width, height) to scale to. If provided, overrides scale.
            scale: Float multiplier for scaling (e.g., 2.0 for 2x). Ignored if size is provided.

        Returns:
            pygame.Surface ready to blit to screen
        """
        # Find the image file
        image_path = self._find_image(filename)

        # Load image
        if filename.endswith(".svg"):
            png_path = self._convert_svg_to_png(image_path)
            img = pygame.image.load(png_path).convert_alpha()
        else:
            img = pygame.image.load(image_path).convert_alpha()

        # Scale image
        if size is not None:
            img = pygame.transform.scale(img, size)
        elif scale is not None and scale != 1.0:
            img = pygame.transform.scale_by(img, scale)

        return img


class stratagemHero:
    def __init__(self, all_rows):
        self.current_script_path = os.path.abspath(__file__)
        self.stratagems_directory = os.path.join(
            os.path.dirname(self.current_script_path), "resources/codes/stratagems.csv"
        )
        self.mission_directory = os.path.join(
            os.path.dirname(self.current_script_path),
            "resources/codes/mission_stratagems.csv",
        )

        # Get paths to resource directories
        self.stratagem_icons_dir = os.path.join(
            os.path.dirname(__file__), "resources", "stratagem_icons"
        )
        self.arrows_dir = os.path.join(os.path.dirname(__file__), "resources", "arrows")
        self.cache_dir = os.path.join(os.path.dirname(__file__), ".svg_cache")

        self.all_rows = all_rows

        self.column_names = {
            "Department": 0,
            "Icon": 1,
            "Stratagem": 2,
            "Stratagem Codes": 3,
            "Cooldown": 4,
            "Cost": 5,
            "Unlock Level": 6,
            "Description": 7,
        }

        self.mission_column_names = {
            "Type": 0,
            "Icon": 1,
            "Stratagem": 2,
            "Stratagem Codes": 3,
            "Description": 4,
        }

        self.total_rows = 0
        for count in all_rows.values():
            self.total_rows += count

        self.stratagems_df = pd.read_csv(self.stratagems_directory, header=None)
        self.mission_df = pd.read_csv(self.mission_directory, header=None)

        self.search_dirs = [self.stratagem_icons_dir, self.arrows_dir]

        self.compatibility_mode = False

        console.print(f"stratagemHero initialized with {all_rows} stratagems.")

    def get_stratagem_table_entry(self, index, column_name: str):
        index += 1  # Adjust for header row in CSV files
        if index > self.total_rows:
            return None

        # Stratagems CSV
        if index <= self.all_rows[0]:
            if index < len(self.stratagems_df):
                col_idx = self.column_names[column_name]
                return self.stratagems_df.iloc[index, col_idx]

        # Mission CSV
        else:
            mission_index = index - self.all_rows[0]
            if mission_index < len(self.mission_df):
                col_idx = (
                    self.mission_column_names["Type"]
                    if column_name == "Department"
                    else self.mission_column_names[column_name]
                )
                return self.mission_df.iloc[mission_index, col_idx]

        return None

    def validate_stratagem_codes(self):
        codes = []
        # check if any index returns "None", an error or the header of the CSV file
        for i in range(self.total_rows):
            data = self.get_stratagem_table_entry(i, "Stratagem Codes")

            if not "Stratagem" in str(data):
                console.print(f"Stratagem code at index {i}: {data}")
                console.print(
                    "This is likely an issue with the csv file or the parsing process. Please check the CSV files and ensure they are formatted correctly."
                )
            elif "Codes" in str(data):
                console.print(f"Stratagem code at index {i}: {data}")
                console.print(
                    "This should NOT happen! This means the header row is being returned as data, which indicates an issue with the CSV file or the parsing process. Please check the CSV files and ensure they are formatted correctly."
                )
            else:
                codes.append(data)

        console.print(f"All {self.total_rows} stratagem codes validated!")
        # for idx, code in enumerate(codes):
        #    console.print(f"Index {idx}: {code}")
        # This means we now have all stratagems available by indexes from 0 to total_rows and are ignoring the header correctly.

    def get_compatibility_mode(self):
        answer = input("Do these arrows look normal? 🡄 🡅 🡆 🡇    ")
        match answer.lower():
            case "yes" | "y":
                console.print("Good. Proceeding as normal.")
                self.compatibility_mode = False
            case "no" | "n":
                console.print(
                    "Enabling compatibility mode. This may cause some formatting issues, but should allow the game to run on a wider range of systems."
                )
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
                    os.system("pause")
                    exit(0)
                case _:
                    console.print("Invalid input. Exiting...")
                    os.system("pause")
                    exit(0)

    def parse_stratagem_code(self, index):
        arrow_code = ""
        normal_code = []
        code = self.get_stratagem_table_entry(index, "Stratagem Codes")
        code = str(code) if code is not None else ""

        for part in code.split("|"):
            match part.strip():
                case _ if "Up" in part:
                    arrow_code += "🡅" if not self.compatibility_mode else "^"
                    normal_code.append("up")
                case _ if "Down" in part:
                    arrow_code += "🡇" if not self.compatibility_mode else "v"
                    normal_code.append("down")
                case _ if "Left" in part:
                    arrow_code += "🡄" if not self.compatibility_mode else "<"
                    normal_code.append("left")
                case _ if "Right" in part:
                    arrow_code += "🡆" if not self.compatibility_mode else ">"
                    normal_code.append("right")
        return arrow_code, normal_code

    def search_file(self, filename):
        """Searches for the exact file name in the following hierachy:
        1. Exact match
        2. Substring match
        3. Replaces spaces with underscores and matches the full file name.
        (Good for matching stratagem icon alts with their svg file paths.
        Also works for the arrows.)

        Returns the first match found."""
        for directory in self.search_dirs:
            # First try exact match
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path

            # If not found, try substring match
            for file in os.listdir(directory):
                if filename in file:
                    return os.path.join(directory, file)

            # If still not found, try replacing spaces with underscores and match full file name
            modified_filename = filename.replace(" ", "_")
            path = os.path.join(directory, modified_filename)
            if os.path.exists(path):
                return path

        raise FileNotFoundError(
            f"File '{filename}' and variant '{modified_filename}' not found in search directories with any matching strategy."
        )

    def run(self):
        # os.system('cls' if os.name == 'nt' else 'clear')
        stratagem = random.randint(0, self.total_rows - 1)
        completed_indices = 0
        split_code = ""
        arrow_code = ""
        normal_code = []

        key_lookup = {"up": "w", "down": "s", "left": "a", "right": "d"}

        # how do I get the pressed key in pygame
        pygame.init()
        screen = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption("Stratagem Hero - Press the correct keys in order!")

        loader = ImageLoader(search_dirs=[self.stratagem_icons_dir, self.arrows_dir])

        stratagem_icon_path = self.search_file(
            self.get_stratagem_table_entry(stratagem, "Icon")
        )

        stratagem_scaled = loader.load(stratagem_icon_path, size=(50, 50))

        def tint_surface(surface, color):
            tinted = surface.copy()
            tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            return tinted

        def load_new_stratagem():
            nonlocal stratagem, stratagem_scaled, completed_indices, update, split_code, arrow_code, normal_code
            stratagem = random.randint(0, self.total_rows - 1)
            completed_indices = 0
            stratagem_icon_path = self.search_file(
                self.get_stratagem_table_entry(stratagem, "Icon")
            )
            stratagem_scaled = loader.load(stratagem_icon_path, size=(50, 50))
            full_code = self.get_stratagem_table_entry(stratagem, "Stratagem Codes")
            split_code = str(full_code).split(" | ")
            update = True
            arrow_code, normal_code = self.parse_stratagem_code(stratagem)

        load_new_stratagem()  # Load the initial stratagem

        running = True
        update = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if pygame.key.name(event.key) == normal_code[completed_indices] or pygame.key.name(event.key) == key_lookup.get(normal_code[completed_indices], ""):
                        completed_indices += 1
                        update = True  # Trigger screen update to show progress
                        if completed_indices >= len(normal_code):
                            load_new_stratagem()  # Load a new stratagem when the current one is complete
                    else:
                        print(
                            f"Incorrect key! Expected '{normal_code[completed_indices]}' but got '{pygame.key.name(event.key)}'. Try again."
                        )

            if update:
                screen.fill((0, 0, 0))
                icon_x = (screen.get_width() - stratagem_scaled.get_width()) // 2
                screen.blit(stratagem_scaled, (icon_x, 50))  # draw stratagem icon

                arrow_size = 30
                arrow_spacing = 10
                total_width = (len(split_code) * arrow_size) + (
                    max(len(split_code) - 1, 0) * arrow_spacing
                )
                start_x = (screen.get_width() - total_width) // 2
                for index, code in enumerate(split_code):
                    arrow_path = self.search_file(code)
                    arrow_scaled = loader.load(
                        arrow_path, size=(arrow_size, arrow_size)
                    )
                    if index < completed_indices:
                        arrow_scaled = tint_surface(arrow_scaled, (255, 255, 0, 255))
                    x = start_x + index * (arrow_size + arrow_spacing)
                    screen.blit(arrow_scaled, (x, 200))  # draw arrow

                # how do I display the name of the stratagem between the icon and the arrows
                font = pygame.font.SysFont(None, 36)
                stratagem_name = self.get_stratagem_table_entry(stratagem, "Stratagem")
                text_surface = font.render(str(stratagem_name), True, (255, 255, 255))
                text_x = (screen.get_width() - text_surface.get_width()) // 2
                screen.blit(text_surface, (text_x, 150))

                pygame.display.flip()
                update = False


if __name__ == "__main__":
    console.print("Loading stratagems from the wiki . . .")
    collector = DataCollector("https://helldivers.wiki.gg/wiki/Stratagems")
    all_rows = collector.get_stratagems()
    console.print("Loading game now . . .")

    for key, value in all_rows.items():
        all_rows[key] = (
            value - 1
        )  # Subtract 1 to account for header row in each CSV file

    game = stratagemHero(all_rows)
    console.print("Game class initialised!")

    game.validate_stratagem_codes()
    console.print("Game loaded correctly!")

    os.system("pause")

    game.run()
