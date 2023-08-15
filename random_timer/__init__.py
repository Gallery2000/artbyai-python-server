import random
import threading


class RandomTimer:
    def __init__(self, callback_function):
        self.timer = None
        self.lock = threading.Lock()
        self.callback_function = callback_function

    def random_wait(self):
        return random.uniform(5, 10)

    def timer_callback(self):
        with self.lock:
            print("Timer expired!")
            if self.callback_function:
                self.callback_function()

    def start_timer(self):
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()

            wait_time = self.random_wait()
            print(f"Waiting for {wait_time:.2f} seconds...")
            self.timer = threading.Timer(wait_time, self.timer_callback)
            self.timer.start()
