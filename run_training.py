"""
Main entry point for the Training Ecosystem.
Supports both GUI mode and Headless mode for command-line execution.
"""
import sys
import threading
from src.training.app import TrainingApp
from src.training.gui import TrainingGUI
from src.training.cli import TrainingCLI

def main():
    is_headless = "--headless" in sys.argv
    
    # Initialize the core application logic
    app = TrainingApp(arena_width=640, arena_height=480)
    
    print("\n[SYSTEM] Neural Mouse Interface Ready.")
    
    if is_headless:
        print("[SYSTEM] Headless Mode active. Use console for commands.")
        print("[SYSTEM] Type '/help' for a list of commands.\n")
        cli = TrainingCLI(app)
        cli.run()
    else:
        print("[SYSTEM] GUI Mode active. Use mouse/keyboard or console for commands.")
        # Start CLI in a background thread so it can listen to commands while GUI runs
        cli = TrainingCLI(app)
        threading.Thread(target=cli.run, daemon=True).start()
        
        gui = TrainingGUI(app)
        gui.run()

if __name__ == "__main__":
    main()
