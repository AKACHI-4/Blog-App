from flask import Flask, render_template 

# Define app
app = Flask(__name__)

@app.route("/")
def hello() :
    return render_template('index.html')

@app.route("/about")
def adarsh() :
    name = "Adarsh"
    return render_template('about.html', name = name)

app.run(debug=True)
