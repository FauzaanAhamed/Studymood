from pynput import keyboard, mouse
import threading
import time

class FocusLogger:
    def __init__(self):
        self.activity_count = 0
        self.lock = threading.Lock()
        self.start_listeners()

    def start_listeners(self):
        def on_press(key): 
            with self.lock: self.activity_count += 1
        def on_click(x, y, button, pressed):
            if pressed:
                with self.lock: self.activity_count += 1

        self.k_listener = keyboard.Listener(on_press=on_press)
        self.m_listener = mouse.Listener(on_click=on_click)
        self.k_listener.start()
        self.m_listener.start()

    def get_focus_score(self):
        with self.lock:
            score = min(self.activity_count / 20, 1.0)
            self.activity_count = 0
        return score
