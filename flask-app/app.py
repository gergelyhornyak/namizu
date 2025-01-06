from app_dir import create_app
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from app_dir.utils.askus_utils import daily_routine

app = create_app()

scheduler = BackgroundScheduler()

def job():
    daily_routine()
    print(f"LOG: daily routine: backup, save, reset")

scheduler.add_job(
    func=job,
    trigger=CronTrigger(hour=5),
)

scheduler.start()

if __name__ == '__main__':
    app.run(debug=False,use_reloader=False)


