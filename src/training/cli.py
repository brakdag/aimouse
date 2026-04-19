"""
CLI interface for the Training Ecosystem.
"""
import sys
from src.training.app import TrainingApp

class TrainingCLI:
    def __init__(self, app: TrainingApp):
        self.app = app

    def run(self):
        """Main CLI loop."""
        print("\n[SYSTEM] Neural Mouse Interface Ready (CLI Mode).")
        print("[SYSTEM] Type '/help' for a list of commands.\n")
        
        while True:
            try:
                cmd = input("CMD> ").strip().lower()
                self._process_command(cmd)
            except EOFError:
                break
            except Exception as e:
                print(f"[CLI ERROR] {e}")

    def _process_command(self, cmd):
        parts = cmd.split()
        if not parts:
            return
        
        main_cmd = parts[0]
        args = parts[1:]

        if main_cmd == "/start":
            self.app.start_training()
        elif main_cmd == "/pause":
            self.app.pause_training()
        elif main_cmd == "/resume":
            self.app.resume_training()
        elif main_cmd == "/stop":
            self.app.stop_training()
        elif main_cmd == "/status":
            print(f"[STATUS] Gen: {self.app.current_gen} | Best Fit: {self.app.best_fitness:.4f}")
        elif main_cmd == "/help":
            print("Available: /start, /pause, /resume, /stop, /status, /gen <n>, /popu <n>, /fps <n>, /elitism <f>, /spawn <n>, /cycle <n>, /mut_rate <f>, /mut_str <f>, /save <name>, /load [index/name], /help, /exit")
        elif main_cmd == "/exit":
            print("[SYSTEM] Exiting...")
            self.app.shutdown_requested = True
            sys.exit()
        elif main_cmd == "/gen":
            if args:
                try:
                    val = int(args[0])
                    self.app.set_generations(val)
                    print(f"[CONFIG] Generations set to {val}")
                except ValueError:
                    print("[CLI ERROR] Please provide a valid integer for /gen")
            else:
                print("[CLI ERROR] Usage: /gen <number>")
        elif main_cmd == "/popu":
            if args:
                try:
                    val = int(args[0])
                    self.app.set_population(val)
                    print(f"[CONFIG] Population set to {val}")
                except ValueError:
                    print("[CLI ERROR] Please provide a valid integer for /popu")
            else:
                print("[CLI ERROR] Usage: /popu <number>")
        elif main_cmd == "/fps":
            if args:
                try:
                    val = int(args[0])
                    self.app.set_fps(val)
                    print(f"[CONFIG] Simulation FPS set to {val}")
                except ValueError:
                    print("[CLI ERROR] Please provide a valid integer for /fps")
            else:
                print("[CLI ERROR] Usage: /fps <number>")
        elif main_cmd == "/elitism":
            if args:
                try:
                    val = float(args[0])
                    self.app.set_elitism(val)
                    print(f"[CONFIG] Elitism rate set to {val}")
                except ValueError:
                    print("[CLI ERROR] Please provide a valid float for /elitism (e.g. 0.2)")
            else:
                print("[CLI ERROR] Usage: /elitism <number>")
        elif main_cmd == "/spawn":
            if args:
                try:
                    val = int(args[0])
                    self.app.set_spawning(val)
                    print(f"[CONFIG] Spawning trials set to {val}")
                except ValueError:
                    print("[CLI ERROR] Please provide a valid integer for /spawn")
            else:
                print("[CLI ERROR] Usage: /spawn <number>")
        elif main_cmd == "/cycle":
            if args:
                try:
                    val = int(args[0])
                    self.app.set_cycles(val)
                    print(f"[CONFIG] Max cycles set to {val}")
                except ValueError:
                    print("[CLI ERROR] Please provide a valid integer for /cycle")
            else:
                print("[CLI ERROR] Usage: /cycle <number>")
        elif main_cmd == "/mut_rate":
            if args:
                try:
                    val = float(args[0])
                    self.app.set_mutation_rate(val)
                    print(f"[CONFIG] Mutation rate set to {val}")
                except ValueError:
                    print("[CLI ERROR] Please provide a valid float for /mut_rate (e.g. 0.2)")
            else:
                print("[CLI ERROR] Usage: /mut_rate <number>")
        elif main_cmd == "/mut_str":
            if args:
                try:
                    val = float(args[0])
                    self.app.set_mutation_strength(val)
                    print(f"[CONFIG] Mutation strength set to {val}")
                except ValueError:
                    print("[CLI ERROR] Please provide a valid float for /mut_str (e.g. 0.5)")
            else:
                print("[CLI ERROR] Usage: /mut_str <number>")
        elif main_cmd == "/save":
            if args:
                name = args[0]
                success, msg = self.app.save_model(name)
                if success:
                    print(f"[SYSTEM] Model saved successfully to {msg}")
                else:
                    print(f"[ERROR] Failed to save model: {msg}")
            else:
                print("[CLI ERROR] Usage: /save <name>")
        elif main_cmd == "/load":
            if not args:
                models = self.app.list_models()
                if not models:
                    print("[SYSTEM] No saved models found in models/ folder.")
                else:
                    print("\n--- Available Models ---")
                    for i, m in enumerate(models, 1):
                        print(f"{i}: {m}")
                    print("------------------------")
                    print("Usage: /load <index> or /load <filename>\n")
            else:
                identifier = args[0]
                success, msg = self.app.load_model(identifier)
                if success:
                    print(f"[SYSTEM] Model {msg} loaded as elite individual.")
                else:
                    print(f"[ERROR] Failed to load model: {msg}")
        else:
            print(f"[CLI] Unknown command: {main_cmd}. Type '/help' for list.")
