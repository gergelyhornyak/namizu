from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Initial variables to be displayed on subpages
page_values = {
    "apple": 25,
    "banana": 25,
    "coconut": 25,
    "dates": 25
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/gc')
def gchome():
    return render_template('gchome.html')

@app.route('/readme')
def readme():
    return render_template('readme')

@app.route('/apple')
def apple():
    return render_template('apple.html', value=page_values["apple"])

@app.route('/banana')
def banana():
    return render_template('banana.html', value=page_values["banana"])

@app.route('/coconut')
def coconut():
    return render_template('coconut.html', value=page_values["coconut"])

@app.route('/dates')
def dates():
    return render_template('dates.html', value=page_values["dates"])

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        page_values["apple"] = int(request.form['apple_new'])
        page_values["banana"] = int(request.form['banana_new'])
        page_values["coconut"] = int(request.form['coconut_new'])
        page_values["dates"] = int(request.form['dates_new'])
        return redirect(url_for('admin'))
    return render_template('admin.html', page_values=page_values)

@app.route("/gc/maze")
def maze():
    return render_template("minigame.html")

@app.route("/gc/wof")
def wof():
    return render_template("wheel_of_fortune.html")

@app.route("/gc/wofreal")
def wof_real():
    return render_template("wheel_of_fortune_real.html")

@app.route("/gc/quiz")
def game():
    return render_template("game01.html")

@app.route("/gc/loop1")
def loop1():
    return render_template("loop1.html")

@app.route("/gc/loop2")
def loop2():
    return render_template("loop2.html")

@app.route("/gc/loop3")
def loop3():
    return render_template("loop3.html")

@app.route("/gc/loop4")
def loop4():
    return render_template("loop4.html")

if __name__ == '__main__':
    app.run(debug=False)

