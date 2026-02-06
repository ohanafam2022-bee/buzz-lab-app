import sys
import time

def type_text(text, delay=0.08):
    """Types text with a delay to simulate typing."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    # ANSI Color Codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"

    # Use raw string for ASCII art to handle backslashes more easily, 
    # but we need to inject colors, so we'll use format or string concatenation.
    # Here we simply construct it carefully.
    
    # Simple "HELLO WORLD" ASCII art
    art_lines = [
        r"  _    _      _ _         __          __       _     _ ",
        r" | |  | |    | | |        \ \        / /      | |   | |",
        r" | |__| | ___| | | ___     \ \  /\  / /__  _ __| | __| |",
        r" |  __  |/ _ \ | |/ _ \     \ \/  \/ / _ \| '__| |/ _` |",
        r" | |  | |  __/ | | (_) |     \  /\  / (_) | |  | | (_| |",
        r" |_|  |_|\___|_|_|\___/       \/  \/ \___/|_|  |_|\__,_|"
    ]

    print("\n" * 2)
    # Print with gradient-ish colors
    colors = [MAGENTA, MAGENTA, CYAN, CYAN, GREEN, GREEN]
    
    for i, line in enumerate(art_lines):
        color = colors[i % len(colors)]
        print(f"{color}{BOLD}{line}{RESET}")
    
    print("\n")
    time.sleep(0.5)
    
    # Typing effect for the message
    # Adding a blinking cursor effect style message
    message = f"{YELLOW}>> SYSTEM ONLINE...{RESET}"
    type_text(message, 0.05)
    
    time.sleep(0.3)
    
    final_message = f"{BOLD}{CYAN}>> Hello, World!{RESET}"
    type_text(final_message, 0.1)
    print("\n")

if __name__ == "__main__":
    main()
