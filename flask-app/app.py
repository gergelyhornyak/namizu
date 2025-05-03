from app_dir import create_app
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from app_dir.routes.namizu_routes_new import resetDay

app = create_app()

scheduler = BackgroundScheduler()

def job():
    resetDay()

scheduler.add_job(
    func=job,
    trigger=CronTrigger(hour=5),
    misfire_grace_time=40
)

app.logger.info("cronjob added: reset at 5am.")

scheduler.start()

if __name__ == '__main__':
    app.run(debug=False,use_reloader=False)


