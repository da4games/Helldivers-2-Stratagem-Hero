"""
Cross-platform non-blocking key reader for Windows and Linux.
Uses only Python standard library.
"""

import sys
import os


def getch():
    """
    Function used to get keyboard input https://stackoverflow.com/a/47548992
    """
    if os.name == "nt":
        import msvcrt

        while True:
            key = msvcrt.getch()
            try:
                return key.decode()
            except UnicodeDecodeError:  # A keypress couldn't be decoded
                # is it an arrow key?
                if key == b"\xe0":
                    key = msvcrt.getch()
                    if key == b"H":
                        return "up"
                    if key == b"P":
                        return "down"
                    if key == b"K":
                        return "left"
                    if key == b"M":
                        return "right"
    else:
        import sys, tty, termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        # Deal with arrow keys
        #print(ch)
        if ch == '\x1b':
            for i in range(2):
                ch = sys.stdin.read(1)
                sys.stdin.flush()
            if ch == 'A':
                return "up"
            elif ch == 'B':
                return "down"
            elif ch == 'C':
                return "right"
            elif ch == 'D':
                return "left"
        return ch


def demo():
    print("Press keys (press 'q' to quit):")
    while True:
        key = getch()
        print(f"You pressed: {key}")
        if key == 'q':
            break


if __name__ == "__main__":
    demo()

