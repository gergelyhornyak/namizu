from app_dir import create_app
from flask_apscheduler import APScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from app_dir.utils.askus_utils import daily_reset

app = create_app()

#scheduler = APScheduler()
scheduler = BackgroundScheduler()

def job():
    daily_reset()
    print(f"LOG: daily question reset")

scheduler.add_job(
    func=job,
    trigger=CronTrigger(hour=5),
)

scheduler.start()

if __name__ == '__main__':
    app.run(debug=False,use_reloader=False)


