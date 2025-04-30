from app_dir import create_app
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from app_dir.utils.namizu_utils import daily_routine

app = create_app()

scheduler = BackgroundScheduler()

def job():
    daily_routine()

scheduler.add_job(
    func=job,
    trigger=CronTrigger(hour=5),
    misfire_grace_time=40
)

scheduler.start()

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)


