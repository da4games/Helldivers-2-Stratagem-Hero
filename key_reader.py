"""
Cross-platform non-blocking key reader for Windows and Linux.
Uses only Python standard library.
"""

import sys
import os


class NonBlockingKeyReader:
    """Reads individual key presses without blocking or requiring Enter."""
    
    def __init__(self):
        self.platform = sys.platform
        if self.platform.startswith("linux"):
            self._init_linux()
        elif self.platform == "win32":
            self._init_windows()
        else:
            raise NotImplementedError(f"Unsupported platform: {self.platform}")
    
    def _init_linux(self):
        """Initialize terminal for Linux/Unix."""
        import termios
        import tty
        
        self.termios = termios
        self.tty = tty
        self.fd = sys.stdin.fileno()
        self.original_settings = termios.tcgetattr(self.fd)
        
        # Set terminal to raw mode
        tty.setraw(self.fd)
    
    def _init_windows(self):
        """Initialize for Windows."""
        import msvcrt
        self.msvcrt = msvcrt
    
    def read_key(self):
        """
        Read a single key press without blocking.
        
        Returns:
            str: The character pressed, or None if no key is available (Linux only).
        """
        try:
            if self.platform.startswith("linux"):
                import select
                # Check if there's input available (non-blocking)
                ready, _, _ = select.select([sys.stdin], [], [], 0)
                if ready:
                    return sys.stdin.read(1)
                return None
            elif self.platform == "win32":
                # Windows - msvcrt.getch() is blocking but works reliably
                if self.msvcrt.kbhit():  # Check if a key is available
                    key = self.msvcrt.getch()
                    # Handle special keys and encoding
                    if key == b'\x00' or key == b'\xe0':  # Extended key prefix
                        prefix = key
                        next_key = self.msvcrt.getch()
                        # Map common arrow keys to human-readable names
                        arrows = {
                            b'H': 'UP',
                            b'P': 'DOWN',
                            b'K': 'LEFT',
                            b'M': 'RIGHT'
                        }
                        name = arrows.get(next_key)
                        if name:
                            return name
                        return f"<SPECIAL:0x{next_key.hex()}:{prefix.hex()}>"
                    # Regular key: decode to text
                    try:
                        return key.decode('utf-8', errors='ignore')
                    except Exception:
                        return repr(key)
                return None
        except Exception as e:
            print(f"Error reading key: {e}", file=sys.stderr)
            return None
    
    def cleanup(self):
        """Restore terminal settings (important for Linux)."""
        if self.platform.startswith("linux"):
            import termios
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.original_settings)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.cleanup()


def demo():
    """Demonstrate key reading."""
    print("Non-blocking Key Reader Demo")
    print("Press 'q' to quit, or any other key to see it...")
    print()
    
    try:
        with NonBlockingKeyReader() as reader:
            while True:
                key = reader.read_key()
                if key:
                    if key == 'q':
                        print("Exiting...")
                        break
                    
                    if key in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                        print(f"Arrow key pressed: {key}")
                    # If key is a single character, show its ASCII code.
                    # Multi-character keys (arrows, escape sequences, or
                    # Windows special markers) should be displayed safely
                    # without calling ord() which expects a single char.
                    if len(key) == 1:
                        print(f"Key pressed: '{key}' (ASCII: {ord(key)})")
                    else:
                        print(f"Key pressed: {repr(key)}")
    except KeyboardInterrupt:
        print("\nInterrupted")


if __name__ == "__main__":
    demo()
