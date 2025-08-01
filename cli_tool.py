# MIT License - Copyright (c) 2025 Viktor Kirschner
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import shlex
import importlib.util
from pathlib import Path
import getpass
import subprocess
from datetime import datetime

# --- Colorama for terminal colors ---
import colorama
print(" ")
print(" ")
from colorama import init, Fore, Back, Style

init(autoreset=True)

# Felső blokk (nagy logó)
block1 = """
 █████╗  ██████╗ ███████╗███╗   ██╗████████╗██╗  ██╗
██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██║ ██╔╝
███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   █████╔╝
██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██╔═██╗
██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ██║  ██╗
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝
""".strip('\n').split('\n')

# Alsó blokk (szlogen)
block2 = """
██╗   ██╗ ██╗    ██████╗
██║   ██║███║   ██╔═████╗
██║   ██║╚██║   ██║██╔██║
╚██╗ ██╔╝ ██║   ████╔╝██║
 ╚████╔╝  ██║██╗╚██████╔╝
  ╚═══╝   ╚═╝╚═╝ ╚═════╝
""".strip('\n').split('\n')

colors = [
    Fore.LIGHTBLACK_EX,  # Sötétszürke
    Fore.BLUE,           # Kék
    Fore.CYAN,           # Cián
    Fore.LIGHTCYAN_EX,   # Világoscián
    Fore.WHITE           # Fehér
]

def print_colored_block(block_lines):
    extended_colors = colors[:]
    while len(extended_colors) < len(block_lines):
        extended_colors.append(colors[-1])
    for line, color in zip(block_lines, extended_colors):
        print(color + line)


print_colored_block(block1)
print()
print_colored_block(block2)
print(" ")
print("AgentK v1.0 – developed by Viktor Kirschner (July 2025)")
print("                      MIT License.")
print(" ")
print(" ")

print(
    f"⚠️ "
    f"{Fore.BLACK}{Back.YELLOW} CAUTION: {Style.RESET_ALL}"
    f"{Fore.LIGHTRED_EX}{Back.BLACK} This is an autonomous agent with full system access.  \n"
    f"{Fore.LIGHTRED_EX}{Back.BLACK} Use in sandboxed environments only. The author is not responsible for any damage caused."
)
print ("")


from ai_connector import get_ai_response_with_history, initialize_client

# --- Custom Exceptions for Flow Control ---
class TaskComplete(Exception):
    """Custom exception to signal the AI has finished the entire task."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class UserInputRequired(Exception):
    """Custom exception to signal the AI needs input from the user to continue."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# --- Constants ---
HANDLERS_DIR = "handlers"
PRIMING_PROMPT_FILE = "priming_prompt.txt"
LOG_FILE = "log.txt"
MEMORY_FILE = "memory.txt"
START_MARKER = "[CMD_START]"
END_MARKER = "[CMD_END]"

# --- State Variables ---
in_code_mode = False
new_command_name = ""
file_path_for_code = ""

# --- Logging and Printing Functions ---
def log_and_print(message="", end='\n', color=None):
    """Prints a message to the console with color and appends the raw message to the log file."""
    str_message = str(message)
    # Log the clean message without any color codes
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(str_message + end)

    # Print the colored message to the console
    if color:
        print(f"{color}{str_message}{Style.RESET_ALL}", end=end)
    else:
        print(str_message, end=end)

def log_message(message="", end='\n'):
    """Appends a message to the log file without printing to console."""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(str(message) + end)

# --- Core Functions ---

def setup_environment():
    """Ensures necessary directories and files exist."""
    Path(HANDLERS_DIR).mkdir(exist_ok=True)
    if not Path(PRIMING_PROMPT_FILE).exists():
        with open(PRIMING_PROMPT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Add your command documentation here for the AI to read.")
    if not Path(LOG_FILE).exists():
        Path(LOG_FILE).touch()
    if not Path(MEMORY_FILE).exists():
        Path(MEMORY_FILE).touch()


def parse_ai_command(response: str):
    """
    Extracts a command from the AI's response string.
    This version is more forgiving and will capture a command if the start
    marker is present, even if the end marker is missing.
    """
    start_index = response.find(START_MARKER)
    if start_index == -1:
        return None # No command marker found

    # We found a start marker, now look for the end marker *after* it
    command_text = response[start_index + len(START_MARKER):] # <-- THE FIX IS HERE
    end_index = command_text.find(END_MARKER)

    if end_index != -1:
        # Both markers were found, extract the command between them
        return command_text[:end_index].strip()
    else:
        # Only the start marker was found, so we assume the rest is the command
        return command_text.strip()

def save_new_command(name: str, code: str) -> str:
    """Saves a new command, cleaning it of all common AI-generated artifacts."""
    lines = code.strip().split('\n')
    
    if lines and lines[0].strip().startswith('```'):
        lines.pop(0)
    if lines and lines[-1].strip() == '```':
        lines.pop(-1)
        
    temp_lines = [line for line in lines if line.strip() != END_MARKER]
    temp_lines_2 = [line for line in temp_lines if not (START_MARKER in line and END_MARKER in line)]
    
    first_code_line_index = 0
    python_starters = ('import ', 'from ', 'def ', 'class ', '#', '"""', "'''")
    for i, line in enumerate(temp_lines_2):
        if line.strip().startswith(python_starters):
            first_code_line_index = i
            break
    
    cleaned_lines = temp_lines_2[first_code_line_index:]
    cleaned_code = '\n'.join(cleaned_lines)

    final_path = Path(HANDLERS_DIR) / f"{name}.py"
    if final_path.exists():
        return f"[ERROR] Command '{name}' already exists."
    try:
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)
        return f"[SUCCESS] Command '{name}' created and cleaned successfully."
    except Exception as e:
        return f"[ERROR] Failed to save command '{name}': {e}"

def process_and_save_memory(history: list):
    """Summarizes the conversation and appends it to the memory file."""
    log_and_print("[INFO] Task complete. Summarizing conversation for memory...")
    summarization_prompt = """
    You are a summarization AI. The user has provided a conversation history from a session with a tool-making AI agent. Your task is to create a concise summary of this session to be used as a memory for the AI in future sessions.
    The summary MUST include:
    1.  The user's original high-level goal.
    2.  A brief overview of the key steps the AI agent took.
    3.  A clear list of any new commands that were created. For each command, provide its name and a one-sentence description of its purpose and usage.
    4.  The final outcome of the task.
    Keep the summary factual and to the point. Do not include any conversational filler.
    """
    try:
        summary = get_ai_response_with_history(summarization_prompt, history)
        if START_MARKER in summary or END_MARKER in summary:
             summary = summary.split(START_MARKER)[0].strip()
        with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*20} MEMORY FROM COMPLETED TASK {'='*20}\n\n")
            f.write(summary)
        log_and_print(f"[SUCCESS] Memory summary appended to {MEMORY_FILE}.")
    except Exception as e:
        log_and_print(f"[ERROR] Failed to generate or save memory summary: {e}")

def save_arbitrary_file(file_path_str: str, code: str) -> str:
    """Saves content to an arbitrary file path, creating parent dirs. Overwrites if file exists."""
    try:
        project_dir = os.path.abspath(os.getcwd())
        target_path = os.path.abspath(file_path_str)
        if os.path.commonpath([project_dir, target_path]) != project_dir:
            return f"[ERROR] Security violation. Cannot write to file outside of project directory: '{file_path_str}'"
        final_path = Path(target_path)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        lines = code.strip().split('\n')
        if lines and lines[0].strip().startswith('```'): lines.pop(0)
        if lines and lines[-1].strip() == '```': lines.pop(-1)
        cleaned_code = '\n'.join(lines)
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)
        return f"[SUCCESS] File '{file_path_str}' was written successfully."
    except Exception as e:
        return f"[ERROR] An unexpected error occurred while writing to '{file_path_str}': {e}"


def execute_command(command_str: str) -> str:
    """Parses and executes a command, raising exceptions for flow control."""
    global in_code_mode, new_command_name, file_path_for_code
    try:
        parts = shlex.split(command_str)
        if not parts: return "[ERROR] Empty command."
        command_name = parts[0]
        args = parts[1:]
    except (ValueError, IndexError):
        return f"[ERROR] Invalid command syntax: '{command_str}'"

    # --- New Two-Step File Writing Handlers ---
    if command_name == 'create_file_begin':
        if not args:
            return "[ERROR] 'create_file_begin' requires a file path."
        file_path_for_code = args[0]
        return f"[INFO] Ready to create new file at '{file_path_for_code}'. Awaiting AI's code block."

    if command_name == 'modify_file_begin':
        if not args:
            return "[ERROR] 'modify_file_begin' requires a file path."
        file_path_for_code = args[0]
        return f"[INFO] Ready to modify file at '{file_path_for_code}'. Awaiting AI's code block."

    # --- Legacy Handler for simple commands ---
    if command_name == 'create_command_begin':
        if not args:
            return "[ERROR] 'create_command_begin' requires a command name."
        new_command_name = args[0]
        in_code_mode = True
        return f"[INFO] Entering multi-line code mode for new command '{new_command_name}'. Awaiting AI's code block."

    # --- Flow Control Handlers ---
    if command_name == 'task_complete':
        final_message = " ".join(args) if args else "Task completed."
        raise TaskComplete(final_message)

    if command_name == 'request_user_input':
        question = " ".join(args) if args else "What is your next step?"
        raise UserInputRequired(question)

    # --- System and Custom Command Handlers ---
    def handle_run_powershell(command_to_run: str = None, *args):
        if not command_to_run: return "[ERROR] No command provided to run_powershell."
        full_command = command_to_run + " " + " ".join(args)
        try:
            result = subprocess.run(["powershell", "-NoProfile", "-Command", full_command], capture_output=True, text=True, timeout=300, check=False, encoding='utf-8')
            if result.returncode != 0:
                return f"[POWERSHELL ERROR] Exit Code: {result.returncode}\n{result.stderr}"
            return result.stdout if result.stdout else "[INFO] PowerShell command ran with no output."
        except Exception as e:
            return f"[POWERSHELL ERROR] Failed to execute command: {e}"

    def handle_run_command(name: str = None, *args):
        if not name: return "[ERROR] Command name not provided."
        module_path = Path(HANDLERS_DIR) / f"{name}.py"
        if not module_path.exists():
            return f"[ERROR] Unknown command: '{name}'"
        try:
            command_to_execute = [sys.executable, str(module_path)] + list(args)
            result = subprocess.run(command_to_execute, capture_output=True, text=True, timeout=300, check=False, encoding='utf-8')
            if result.returncode != 0:
                return f"[EXECUTION ERROR] Command '{name}' failed: {result.stderr}"
            return result.stdout if result.stdout else f"[INFO] Command '{name}' ran successfully with no output."
        except Exception as e:
            return f"[EXECUTION ERROR] An unexpected error occurred while running '{name}': {e}"

    internal_handlers = {
        'run_powershell': handle_run_powershell
    }
    if command_name in internal_handlers:
        return internal_handlers[command_name](*args)
    
    return handle_run_command(command_name, *args)

# --- Command Handlers ---

def handle_run_powershell(command_to_run: str = None, *args):
    """Executes a PowerShell command."""
    if not command_to_run: return "[ERROR] No command provided to run_powershell."
    full_command = command_to_run + " " + " ".join(args)
    try:
        result = subprocess.run(["powershell", "-NoProfile", "-Command", full_command], capture_output=True, text=True, timeout=300, check=False)
        if result.returncode != 0:
            return f"[POWERSHELL ERROR] Exit Code: {result.returncode}\n{result.stderr}"
        return result.stdout if result.stdout else "[INFO] PowerShell command ran with no output."
    except Exception as e:
        return f"[POWERSHELL ERROR] Failed to execute command: {e}"

def handle_run_command(name: str = None, *args):
    """Executes a command script in a separate process and captures its output."""
    if not name:
        return "[ERROR] Command name not provided."
    module_path = Path(HANDLERS_DIR) / f"{name}.py"
    if not module_path.exists():
        return f"[ERROR] Unknown command: '{name}'"
    try:
        command_to_execute = [sys.executable, str(module_path)] + list(args)
        result = subprocess.run(
            command_to_execute, capture_output=True, text=True, timeout=300, check=False
        )
        if result.returncode != 0:
            error_output = result.stderr if result.stderr else "The script failed but produced no error message."
            return f"[EXECUTION ERROR] Command '{name}' failed with exit code {result.returncode}:\n{error_output}"
        return result.stdout if result.stdout else f"[INFO] Command '{name}' ran successfully with no output."
    except subprocess.TimeoutExpired:
        return f"[EXECUTION ERROR] Command '{name}' timed out after 300 seconds."
    except Exception as e:
        return f"[EXECUTION ERROR] An unexpected error occurred while running '{name}': {e}"

# --- Main REPL Loop ---
def main():
    """The main Read-Eval-Print Loop for the autonomous agent."""
    global in_code_mode, new_command_name, file_path_for_code
    
    colorama.init(autoreset=True)
    setup_environment()
    log_message(f"\n--- NEW SESSION STARTED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    log_and_print("--- AI Agent Tool Initialization ---")
    api_key = os.getenv("MOONSHOT_API_KEY") 
    if not api_key:
        log_and_print("INFO: API key environment variable not found.")
        try: 
            prompt = "Please enter your API key and press Enter: "
            log_message(prompt + "********")
            api_key = getpass.getpass(prompt)
        except (KeyboardInterrupt, EOFError): log_and_print("\nOperation cancelled. Exiting."); return
    if not initialize_client(api_key):
        log_and_print("Could not start the tool. Exiting."); return
        
    log_and_print("\nAI Agent CLI Tool")
    log_and_print("Enter your high-level goal.")
    try:
        with open(PRIMING_PROMPT_FILE, 'r', encoding='utf-8') as f:
            base_system_prompt = f.read()
        
        if Path(MEMORY_FILE).exists() and Path(MEMORY_FILE).stat().st_size > 0:
            log_and_print(f"[INFO] Loading memory from {MEMORY_FILE}...")
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                memory_content = f.read()
            system_prompt = f"{base_system_prompt}\n\n# PREVIOUS SESSION MEMORY\n---\n{memory_content}\n---"
        else:
            system_prompt = base_system_prompt
    except FileNotFoundError:
        log_and_print(f"[FATAL] Priming prompt '{PRIMING_PROMPT_FILE}' not found. Exiting."); return

    conversation_history = []
    
    while True:
        try:
            if not conversation_history:
                prompt_text = "\n👤 You: "
                log_and_print(prompt_text, color=Fore.YELLOW, end='')
                user_query = input()
                if not user_query.strip(): user_query = "[USER_SUBMITTED_EMPTY_PROMPT]"
                log_message(user_query)
                if user_query.lower() in ['exit', 'quit']: break
                conversation_history.append({"role": "user", "content": user_query})
            
            log_and_print(f"\n--- Autonomous Step ---")
            
            ai_response_text = get_ai_response_with_history(system_prompt, conversation_history)
            
            # --- Primary Check: Is the tool waiting for code? ---
            if file_path_for_code:
                log_and_print(f"🤖 AI intends to write the following code to '{file_path_for_code}':", color=Fore.CYAN)
                log_and_print(f"```python\n{ai_response_text}\n```", color=Fore.CYAN)
                
                result = save_arbitrary_file(file_path_for_code, ai_response_text)

                log_and_print(f"🛠️ Tool Output:\n{result}", color=Fore.GREEN)
                
                file_path_for_code = ""
                tool_feedback = f"The result of your file writing action was: {result}. What is your next step?"
                conversation_history.append({"role": "assistant", "content": ai_response_text})
                conversation_history.append({"role": "user", "content": tool_feedback})
                continue

            # --- Legacy Check: Waiting for a simple handler command ---
            if in_code_mode:
                log_and_print(f"🤖 AI intends to write the following code for '{new_command_name}':", color=Fore.CYAN)
                log_and_print(f"```python\n{ai_response_text}\n```", color=Fore.CYAN)
                result = save_new_command(new_command_name, ai_response_text)
                log_and_print(f"🛠️ Tool Output:\n{result}", color=Fore.GREEN)
                in_code_mode = False
                new_command_name = ""
                tool_feedback = f"The result of your 'create_command_begin' action was: {result}. What is your next step?"
                conversation_history.append({"role": "assistant", "content": ai_response_text})
                conversation_history.append({"role": "user", "content": tool_feedback})
                continue

            # --- Standard Command Execution Logic ---
            conversation_history.append({"role": "assistant", "content": ai_response_text})
            command_to_run = parse_ai_command(ai_response_text)

            if command_to_run:
                parts = ai_response_text.split(START_MARKER)
                before_command = parts[0]
                command_and_after = parts[1].split(END_MARKER)
                command_part = command_and_after[0]
                after_command = command_and_after[1] if len(command_and_after) > 1 else ""
                print(f"{Fore.CYAN}🤖 AI: {before_command}", end='')
                print(f"{Fore.RED}{START_MARKER}{command_part}{END_MARKER}", end='')
                print(f"{Fore.CYAN}{after_command}{Style.RESET_ALL}")
                log_message(f"🤖 AI: {ai_response_text}")
            else:
                log_and_print(f"🤖 AI: {ai_response_text}", color=Fore.CYAN)

            if command_to_run:
                execution_result = execute_command(command_to_run)
                if execution_result is None: execution_result = "[INFO] Command ran with no output."
                log_and_print("-" * 20)
                log_and_print(f"🛠️ Tool Output:\n{execution_result}", color=Fore.GREEN)
                log_and_print("-" * 20)
                tool_feedback = f"The result of your last command was:\n\n{execution_result}\n\nBased on this, what is your next action?"
                conversation_history.append({"role": "user", "content": tool_feedback})
            else:
                log_and_print("-" * 20)
                log_and_print("[INFO] AI is waiting for your input.")
                prompt_text = "\n👤 You: "
                log_and_print(prompt_text, color=Fore.YELLOW, end='')
                user_response = input()
                if not user_response.strip(): user_response = "[USER_SUBMITTED_EMPTY_PROMPT]"
                log_message(user_response)
                if user_response.lower() in ['exit', 'quit']:
                    log_and_print("\nOperation cancelled. Exiting."); break
                conversation_history.append({"role": "user", "content": user_response})
                log_and_print("-" * 20)
                continue

        except UserInputRequired as e:
            log_and_print("-" * 20)
            log_and_print(f"🤖 AI: {e.message}", color=Fore.CYAN)
            prompt_text = "\n👤 You: "
            log_and_print(prompt_text, color=Fore.YELLOW, end='')
            user_response = input()
            if not user_response.strip(): user_response = "[USER_SUBMITTED_EMPTY_PROMPT]"
            log_message(user_response)
            if user_response.lower() in ['exit', 'quit']:
                log_and_print("\nOperation cancelled. Exiting."); break
            conversation_history.append({"role": "user", "content": user_response})
            log_and_print("-" * 20)
            continue
        except TaskComplete as e:
            log_and_print("-" * 20)
            log_and_print(f"✅ AI: {e.message}", color=Fore.CYAN)            
            if conversation_history:
                process_and_save_memory(conversation_history)
            log_and_print("[INFO] AI has marked the task as complete. Awaiting new user input.")
            log_and_print("-" * 20)
            conversation_history = []
            continue
        except KeyboardInterrupt:
            log_and_print("\nOperation cancelled. Exiting."); break
        except Exception as e:
            log_and_print(f"\n[FATAL] An unexpected error occurred in the main loop: {e}", color=Fore.RED)
            break

if __name__ == "__main__":
    main()
