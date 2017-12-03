import uuid
import threading
import concurrent.futures

class Scheduler:
    def __init__(self, run=True):
        self.scheduled = {}
        self.history = {}
        self.running = run
        self.paused = {}
        self.stopped = {}

    def schedule(self, task):
        task_id = str(uuid.uuid4())
        self.scheduled.update({task_id: task})
        if self.running:
            task.start()
        return task_id

    def get_tasks(self, task_id=None):
        tasks = self.scheduled.values()
        if task_id:
            tasks = [t for t in [self.scheduled.get(task_id)] if t is not None]
        return tasks

    def _get_bool_dict(self, taskid, bval):
        if taskid:
            return {taskid: True}
        else:
            return {tid: True for tid in self.scheduled.keys()}

    def pause(self, taskid=None):
        self.paused.update(self._get_bool_dict(taskid, True))
        for t in self.get_tasks(taskid):
            t.pause()

    def resume(self, taskid=None):
        self.paused.update(self._get_bool_dict(taskid, False))
        for t in self.get_tasks(taskid):
            t.resume()

    def stop(self, taskid=None):
        self.stopped.update(self._get_bool_dict(taskid, True))
        for t in self.get_tasks(taskid):
            t.cancel()
        for t in self.get_tasks(taskid):
            t.join()
        self._clean_schedule()

    def _clean_schedule(self):
        self.history.update({tid: t for tid, t in self.scheduled.items() if not t.is_alive()})
        self.scheduled = {tid: t for tid, t in self.scheduled.items() if tid not in self.history.keys()}

    def run(self, taskid=None):
        self.running = True
        for t in self.get_tasks(taskid):
            try:
                t.start()
            except Exception as e:
                print(e.args)
                pass


class ScheduleLoop(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):


class SchedulerAsync(threading.Thread):
    def __init__(self, run=True):
        self.scheduled = {}
        self.history = {}
        self.running = run
        self.paused = {}
        self.stopped = {}


    def schedule(self, task):
        task_id = str(uuid.uuid4())
        self.scheduled.update({task_id: task})
        if self.running:
            task.start()
        return task_id


import time


class ScheduledTaskAsync():
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

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def cancel(self):
        self.cancelled = True

    def _initialize(self):
        self.started_at = time.time()

    def _should_run_in(self):
        if self.cancelled:
            return
        now = time.time()
        initialized_since = now - (self.last_ran or self.started_at)
        if self.next_run is None:
            return
        return self.next_run - (initialized_since or 0)

    def run(self):
        starting = yield
        self._initialize()
        while True:
            request = yield self._should_run_in() >0
            if request:
                if request == 'status' :
                    yield {'paused': self.paused, 'cancelled': self.cancelled}

        self._initialize()
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
            should_run_in = self._should_run_in()
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



