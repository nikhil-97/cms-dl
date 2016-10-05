import datetime
import time
from apscheduler.schedulers import Scheduler

# Start the scheduler
sched = Scheduler()
sched.daemonic = False
sched.start()

def job_function():
    print("Hello World")
    print(datetime.datetime.now())
    time.sleep(20)

# Schedules job_function to be run once each minute
sched.add_cron_job(job_function,  minute='0-59')
