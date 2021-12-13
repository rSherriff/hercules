import time


class DeltaTime:
    def __init__(self):
        self.delta_time = 0.16
        self.last_tick = time.time()


    def get_delta_time(self):
        return self.delta_time

    def update_delta_time(self):
        self.delta_time = abs(self.last_tick - time.time())
        self.last_tick = time.time()
