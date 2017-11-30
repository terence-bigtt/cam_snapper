import uuid


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
