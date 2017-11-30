import time, threading


class ScheduledTask(threading.Thread):
    def __init__(self, cmd, every=None, timeout=None, max_error_tol=10):
        self.last_ran = None
        self.started_at = None
        self.timeout = timeout
        self.max_error_tol = max_error_tol
        self.cmd = cmd
        self.errors = []
        self.last_result = None
        self.next_run = timeout or 0
        self.every = every
        self.cancelled = False
        self.paused = False
        threading.Thread.__init__(self)

    def reset(self):
        return ScheduledTask(self.cmd, self.every, self.timeout, self.max_error_tol)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def cancel(self):
        self.cancelled = True

    def initialize(self):
        self.started_at = time.time()

    def should_run_in(self):
        if self.cancelled:
            return
        now = time.time()
        initialized_since = now - (self.last_ran or self.started_at)
        if self.next_run is None:
            return
        return self.next_run - (initialized_since or 0)

    def run(self):
        self.initialize()
        goon = True
        runner = self._runner()
        while goon:
            goon = next(runner)

    def _runner(self):
        goon = True
        received = None
        while True:
            if received is not None:
                goon = received
            should_run_in = self.should_run_in()
            if should_run_in is None or not goon or self.cancelled:
                yield False
                break

            if self.paused or should_run_in > 0:
                dorun = False
            else:
                dorun = True

            if dorun:
                try:
                    self.last_result = self.cmd()
                    self.last_ran = time.time()
                    self.next_run = None
                    if self.every is not None:
                        self.next_run = self.every

                except Exception as e:
                    print(e)
                    print("exception in run", len(self.errors), self.max_error_tol)
                    self.errors.append(e)
                    if len(self.errors) >= self.max_error_tol:
                        self.cancel()
                        yield False
                        break

            received = yield goon
