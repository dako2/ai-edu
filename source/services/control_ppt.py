import os
import platform
import subprocess
import time
from pykeyboard import PyKeyboard
from services.pptx_slides import PptxSlideService

class PowerPointOperator:
    def __init__(self, pptx_path):
        """
        Initializes the PowerPointOperator.

        Args:
            pptx_path: The path to the PowerPoint file.
        """
        if not os.path.exists(pptx_path):
            raise FileNotFoundError(f"File not found: {pptx_path}")

        self.pptx_path = pptx_path
        self.process = None  # Store the subprocess
        self.os_type = platform.system()  # Determine OS
        self.keyboard = PyKeyboard()  # Initialize PyKeyboard

    def open_presentation(self):
        """Opens the PowerPoint presentation."""
        try:
            if self.os_type == "Darwin":  # macOS
                self.process = subprocess.Popen(["open", self.pptx_path])
            elif self.os_type == "Windows":
                self.process = subprocess.Popen([self.pptx_path], shell=True)
            else:
                raise OSError("Unsupported operating system.")

            # Give PowerPoint time to fully open. Adjust as needed.
            time.sleep(5)  # Important pause

        except Exception as e:
            print(f"Error opening presentation: {e}")
            self.process = None

    def start_slideshow(self):
        """Starts the PowerPoint slideshow using the F5 shortcut."""
        try:
            # Simulate pressing the F5 key using PyKeyboard
            self.keyboard.tap_key(self.keyboard.function_keys[5])
        except Exception as e:
            print(f"Error starting slideshow: {e}")

    def _send_keystroke(self, keystroke):
        """Sends a keystroke to control PowerPoint. Private method."""
        try:
            if self.os_type == "Darwin":  # macOS
                import applescript
                script = f"""
                tell application "System Events"
                    tell process "Microsoft PowerPoint"
                        key code {keystroke}
                    end tell
                end tell
                """
                applescript.run(script)
            elif self.os_type == "Windows":
                import pyautogui
                pyautogui.press(keystroke)
            else:
                raise OSError("Unsupported OS for keystrokes.")
        except Exception as e:
            print(f"Error sending keystroke: {e}")

    def next_slide(self):
        """Advances to the next slide."""
        self._send_keystroke(125)  # Down arrow key code on macOS
        self._send_keystroke(49)  # Down arrow key code on macOS
 
    def previous_slide(self):
        """Goes back to the previous slide."""
        self._send_keystroke(126)  # Up arrow key code on macOS

    def close_presentation(self):
        """Closes the PowerPoint presentation."""
        if self.process:
            try:
                if self.os_type == "Darwin":
                    import applescript
                    script = """
                    tell application "Microsoft PowerPoint"
                        quit
                    end tell
                    """
                    applescript.run(script)
                elif self.os_type == "Windows":
                    self.process.terminate()  # or self.process.kill()
                self.process = None
            except Exception as e:
                print(f"Error closing PowerPoint: {e}")

class ControlSlide:
    def __init__(self, pptx_file):
        self.pptx_service = PptxSlideService(pptx_file)
        self.ppt_operator = PowerPointOperator(pptx_file)
        self.ppt_operator.open_presentation()
        
        print("Starting slideshow...")
        self.ppt_operator.start_slideshow()

        self.num_slides_to_rewind = self.pptx_service.total_slides # Example: Rewind 3 slides
        print("Rewinding slides...")
        for _ in range(self.num_slides_to_rewind):
            self.ppt_operator.previous_slide()

        self.ppt_operator._send_keystroke(96)  # F5 key code on macOS
            
    def navigate_slide(self, slide_number):
        """
        Set the current slide by sending a POST request to the server.
        """
        for _ in range(self.num_slides_to_rewind):
            self.ppt_operator.previous_slide()

        for _ in range(slide_number):
            self.ppt_operator.next_slide()

    def next_slide(self):
        self.ppt_operator.next_slide()

    def close(self):
        #input("Press Enter to close the presentation...")
        self.ppt_operator.close_presentation()

# Example usage:
if __name__ == "__main__":

    pptx_file = "/Users/dako22/Downloads/test_full.pptx"  # Replace with your pptx path
    control_slide = ControlSlide(pptx_file)
    