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
        page_values["apple"] = float(request.form['apple_new'])
        page_values["banana"] = float(request.form['banana_new'])
        page_values["coconut"] = float(request.form['coconut_new'])
        page_values["dates"] = float(request.form['dates_new'])
        return redirect(url_for('admin'))
    return render_template('admin.html', page_values=page_values)

@app.route("/maze")
def maze():
    return render_template("minigame.html")

@app.route("/loop1")
def loop1():
    return render_template("loop1.html")

@app.route("/loop2")
def loop2():
    return render_template("loop2.html")

if __name__ == '__main__':
    app.run(debug=False)

