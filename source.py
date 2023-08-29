from flask import Flask, render_template, request, jsonify
import threading
from datetime import datetime, timedelta
import time

app = Flask(__name__)

class AlarmClock:

    trigger = 0

    def __init__(self,app):
        self.alarms = []
        self.app = app
        self.lock = threading.Lock()

    def set_alarm(self, alarm_time):
        with self.lock:
            self.alarms.append(alarm_time)

    def check_alarms(self):
        while True:
            current_time = time.time()
            triggered_alarms = []
            with self.lock:
                for alarm_time in self.alarms:
                    if current_time >= alarm_time:
                        triggered_alarms.append(alarm_time)
                for alarm_time in triggered_alarms:
                    AlarmClock.trigger = alarm_time
                    self.alarms.remove(alarm_time)
            time.sleep(1)  # Check alarms every 1 second

alarm_clock = AlarmClock(app)
alarm_thread = threading.Thread(target=alarm_clock.check_alarms)
alarm_thread.daemon = True
alarm_thread.start()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        choice = request.form['choice']
        AlarmClock.trigger = 0
        if choice == "div1":
            try:
                hh = int(request.form['alarm_timehh'])
                mm = int(request.form['alarm_timemm'])
                current_date = datetime.now().date()
                ist_time = datetime.combine(current_date, datetime.min.time().replace(hour=hh, minute=mm))
                utc_time = ist_time - timedelta(hours=5,minutes=30)
                unix_time = (utc_time - datetime(1970,1,1)).total_seconds()
                alarm_clock.set_alarm(unix_time)
                message = "Alarm set successfully."
            except ValueError:
                message = "Invalid input. Please enter a valid time format."
        elif choice == "div2":
            try:
                seconds = int(request.form['countdownss'])
                minutes=int(request.form['countdownmm'])
                alarm_time = time.time() + seconds+(minutes*60)
                alarm_clock.set_alarm(alarm_time)
                message = "Countdown timer set successfully."
            except ValueError:
                message = "Invalid input. Please enter a valid number"
        else:
            message = "Invalid choice. Please select either 1 or 2."

        return render_template('index.html', message=message)


    return render_template('index.html', message=" ")

@app.route('/check',methods=['GET','POST'])
def check():
    return jsonify({'value': AlarmClock.trigger})
    

if __name__ == '__main__':
    app.run(debug=True)
