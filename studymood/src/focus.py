try:
    from pynput import keyboard, mouse
    import threading
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    import threading

class FocusLogger:
    def __init__(self):
        self.activity_count = 0
        self.lock = threading.Lock()
        if PYNPUT_AVAILABLE:
            self.start_listeners()
        else:
            print("pynput not available - using simulated focus tracking")

    def start_listeners(self):
        if not PYNPUT_AVAILABLE:
            return
            
        def on_press(key): 
            with self.lock: 
                self.activity_count += 1
        def on_click(x, y, button, pressed):
            if pressed:
                with self.lock: 
                    self.activity_count += 1

        self.k_listener = keyboard.Listener(on_press=on_press)
        self.m_listener = mouse.Listener(on_click=on_click)
        self.k_listener.start()
        self.m_listener.start()

    def get_focus_score(self):
        with self.lock:
            if PYNPUT_AVAILABLE:
                score = min(self.activity_count / 20, 1.0)
                self.activity_count = 0
            else:
                # Simulate activity for cloud deployment
                import random
                score = random.uniform(0.4, 0.8)
            return score
