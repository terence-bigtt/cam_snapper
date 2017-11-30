from archiver import Archiver
from config.general import GeneralConfig
from scheduler.scheduler import Scheduler
from scheduler.task import ScheduledTask
from snapper import Snapper

scheduler = Scheduler()

general = GeneralConfig('../settings.yml')
storage = general.storage
snap_every = general.snap_every

snappers = [Snapper(cam_conf, general.storage) for cam_conf in general.cams]

snap_tasks = [ScheduledTask(snapper.snap, snap_every) for snapper in snappers]
archive_tasks = [ScheduledTask(snapper.archive, snap_every, 1) for snapper in snappers]
tasks = archive_tasks + snap_tasks

for t in tasks:
    scheduler.schedule(t)

