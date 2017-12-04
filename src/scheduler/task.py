
import time

class RunningTask(object):
    def __init__(self, future=None, will_run_in=None, paused=False, cancelled=False, done=False):
        self.future = future
        self.will_run_in = will_run_in
        self.ispaused = paused
        self.iscancelled = cancelled
        self.done = done

    @property
    def isexecuting(self):
        return self.future is not None

    @property
    def iswaiting(self):
        return self.will_run_in is not None


class TaskException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class Task(object):
    def __init__(self, cmd, *args, **kwargs):
        kw = {k: v for k, v in kwargs.items()}
        every = kw.pop("every", None)
        timeout = kw.pop("timeout", None)
        max_error_tol = kw.pop("max_error_tol", 10)
        self._last_ran = None
        self._started_at = None
        self.timeout = timeout
        self.max_error_tol = max_error_tol
        self.cmd = cmd
        self.args = args
        self.kwargs = kw
        self.errors = []
        self.last_result = None
        self._next_run = timeout or 0
        self.every = every
        self.cancelled = False
        self.paused = False
        self._paused_at = None
        self._generator = self.run()
        self.executor = None

    def set_executor(self, executor):
        self.executor = executor

    def __next__(self):
        return next(self._generator)

    def pause(self):
        self.paused = True
        self._paused_at = time.time()

    def resume(self):
        self.paused = False
        if self._paused_at:
            timesincepause = time.time() - self._paused_at
            self._next_run += timesincepause
            self._paused_at = None

    def cancel(self):
        self.cancelled = True

    def _initialize(self):
        self._started_at = time.time()

    def _should_run_in(self):
        if self.cancelled:
            return
        now = time.time()
        time_since_last_run = now - (self._last_ran or self._started_at)
        if self._next_run is None:
            return
        return self._next_run - (time_since_last_run or 0)

    def run(self):
        self._initialize()
        yield RunningTask()
        while True:
            if self.executor is None:
                raise TaskException("Executor not defined. Use set_executor(executor).")

            if self.cancelled:
                result = RunningTask(cancelled=True)

            elif self.paused:
                result = RunningTask(paused=True)
            else:
                willrunin = self._should_run_in()
                if not willrunin:
                    self.cancel()
                    result = RunningTask(done=True, cancelled=True)
                else:
                    shouldrun = willrunin < 0
                    if shouldrun:
                        future = self.executor.submit(self._executecmd)
                        next_run = self.setup_next_run()
                        result = RunningTask(future=future, will_run_in=next_run)
                    else:
                        result = RunningTask(will_run_in=willrunin, paused=self.paused, cancelled=self.cancelled)
            yield result

    def setup_next_run(self):
        self._last_ran = time.time()
        self._next_run = None
        if self.every is not None:
            self._next_run = self.every
        return self._next_run

    def _executecmd(self):
        try:
            return self.cmd(*self.args, **self.kwargs)

        except Exception as e:
            print(e)
            print("exception in run", len(self.errors), self.max_error_tol)
            self.errors.append(e)
            if len(self.errors) >= self.max_error_tol:
                self.cancel()


