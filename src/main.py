from archiver import Archiver
from config.general import GeneralConfig
from scheduler.scheduler import Scheduler
from scheduler.task import ScheduledTask
from snapper import Snapper

scheduler = Scheduler()

general = GeneralConfig('../settings.yml')
storage = general.storage
snap_every = general.snap_every

snapper = Snapper(general)

snap_task = ScheduledTask(snapper.snap, snap_every)
archive_task = ScheduledTask(snapper.archive, snap_every, 1)
tasks = [archive_task, snap_task]
for t in tasks:
    scheduler.schedule(t)

