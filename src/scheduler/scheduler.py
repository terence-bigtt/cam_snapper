import uuid
import threading
import concurrent.futures
import time


class Scheduler(object):
    def __init__(self, max_workers=None, thread_name_prefix="", running=True):
        self.scheduled = {}
        self.history = {}
        self.results = {}
        self._running = running
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers,
                                                              thread_name_prefix=thread_name_prefix)
        self.thread = threading.Thread(target=self._run)
        self._lock = False
        if running:
            self.start()

    def schedule(self, task):
        taskid = str(uuid.uuid4())
        task.set_executor(self.executor)
        self._lock = True
        while self._loopstart: pass
        self.scheduled.update({taskid: task})
        self._lock = False
        return taskid

    def pause_all(self):
        for tid, task in self.scheduled.items():
            task.pause()

    def pause(self, taskid):
        task = self.scheduled.get(taskid)
        if task:
            task.pause()

    def resume(self, taskid):
        task = self.scheduled.get(taskid)
        if task:
            task.resume()

    def resume_all(self):
        for tid, task in self.scheduled.items():
            task.resume()

    def cancel(self, taskid):
        task = self.scheduled.pop(taskid, None)
        if task:
            task.cancel()
            self.history.update({taskid: task})

    def stop(self):
        self._running = False

    def start(self):
        try:
            if not self.thread.isAlive():
                self.running = True
                self.thread.start()

        except RuntimeError:
            self.thread = threading.Thread(target=self._run)
            self._running = True
            self.thread.start()

    def _run(self):
        while self._running:
            if not self._lock:
                self._loopstart = True
                runningschedule = {k: v for k, v in self.scheduled.items()}
                self._loopstart = False
                for tid, task in runningschedule.items():
                    runningtask = next(task)
                    if runningtask.isexecuting:
                        self.results.update({tid: runningtask})
                    if runningtask.done:
                        self.history.update({tid: self.scheduled.pop(tid)})
