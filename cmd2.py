import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton
import subprocess
import threading

class CommandLineChatApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Command Line Chat Interface")
        self.setGeometry(100, 100, 600, 400)

        # Set the background color for the window (everything except the title bar)
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f7fa;  /* light gray background */
            }
        """)

        # Set up main layout
        self.main_layout = QVBoxLayout(self)

        # Set up the chat display window (text area) to fill the entire screen
        self.chat_window = QTextEdit(self)
        self.chat_window.setReadOnly(True)  # Make the chat window read-only
        self.chat_window.setStyleSheet("""
            background-color: #e0f7fa;  /* Light cyan background for the chat */
            color: #333;  /* Dark text for readability */
            font-size: 14px;
            padding: 10px;
            border-radius: 8px;
            font-family: 'Arial', sans-serif;
            border: 2px solid #b2ebf2;  /* Slightly darker border for emphasis */
        """)
        self.main_layout.addWidget(self.chat_window)

        # Set up the bottom layout (for input box and send button)
        self.bottom_layout = QHBoxLayout()

        # Input box for commands with a simple white background
        self.input_box = QLineEdit(self)
        self.input_box.setStyleSheet("""
            background-color: #ffffff;  /* White background for input box */
            font-size: 14px;
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #ccc;
        """)
        self.bottom_layout.addWidget(self.input_box)

        # Send button with a longer size and vibrant color
        self.send_button = QPushButton("Send", self)
        self.send_button.setStyleSheet("""
            background-color: #ff9800;  /* Vibrant orange color for the button */
            color: white;
            font-size: 16px;  /* Slightly larger font */
            padding: 12px 20px;  /* Increase padding for a longer button */
            border-radius: 8px;
            border: none;
        """)
        self.send_button.clicked.connect(self.execute_command)
        self.bottom_layout.addWidget(self.send_button)

        # Add bottom layout to main layout
        self.main_layout.addLayout(self.bottom_layout)

        # Make the chat window fill the remaining space, and push input box and button to the bottom
        self.main_layout.setStretch(0, 1)  # Stretch the chat window to take up remaining space
        self.main_layout.setStretch(1, 0)  # Don't stretch the bottom layout (input + button)

        # Track the current directory (start from the home directory)
        self.current_directory = os.path.expanduser("~")
        self.previous_directory = None

    def execute_command(self):
        # Get the command input by the user
        command = self.input_box.text().strip()
        if not command:
            return  # Ignore empty inputs

        # Display user command in the chat window
        self.chat_window.append(f"<font color='blue'><b>You:</b></font> {command}")

        # Clear the input box for the next command
        self.input_box.clear()

        # Execute the command in a separate thread to avoid freezing the UI
        threading.Thread(target=self.run_command, args=(command,)).start()

    def run_command(self, command):
        try:
            if command.startswith("cd "):
                # Handle 'cd' command to change directory
                new_directory = command[3:].strip()
                if new_directory == "..":
                    # Go back to the previous directory
                    if self.previous_directory:
                        self.current_directory, self.previous_directory = self.previous_directory, self.current_directory
                        self.update_chat_window(f"<font color='green'><b>System:</b></font> Changed directory to {self.current_directory}")
                    else:
                        self.update_chat_window(f"<font color='red'><b>System (Error):</b></font> No previous directory to go back.")
                else:
                    # Change to the specified directory
                    full_path = os.path.join(self.current_directory, new_directory)
                    if os.path.isdir(full_path):
                        self.previous_directory = self.current_directory
                        self.current_directory = full_path
                        self.update_chat_window(f"<font color='green'><b>System:</b></font> Changed directory to {self.current_directory}")
                    else:
                        self.update_chat_window(f"<font color='red'><b>System (Error):</b></font> Directory '{new_directory}' not found.")
                return

            elif command.startswith("python"):
                # Handle Python expressions by running them with `python -c`
                python_command = command[6:].strip()
                python_command = f"print({python_command})"  # Ensure the result is printed out
                process = subprocess.Popen(
                    ['python3', '-c', python_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                output, _ = process.communicate()
                if output:
                    self.update_chat_window(f"<font color='black'><b>System:</b></font> {output}")
                else:
                    self.update_chat_window(f"<font color='red'><b>System (Error):</b></font> No output returned.")
                
            else:
                # Run the command as a system command
                process = subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=self.current_directory
                )

                # Read the output line by line
                for output in process.stdout:
                    self.update_chat_window(f"<font color='black'><b>System:</b></font> {output}")

                # Capture any error output
                error_output = process.stderr.read()
                if error_output:
                    self.update_chat_window(f"<font color='red'><b>System (Error):</b></font> {error_output}")

        except Exception as e:
            self.update_chat_window(f"<font color='red'><b>Error:</b></font> {str(e)}")

    def update_chat_window(self, output):
        # Update the chat window with the command output
        self.chat_window.append(output)
        self.chat_window.verticalScrollBar().setValue(self.chat_window.verticalScrollBar().maximum())  # Scroll to the bottom

if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)

    # Create the window instance
    window = CommandLineChatApp()
    window.show()

    # Execute the application
    sys.exit(app.exec_())
