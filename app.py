from flask import Flask, render_template, request, session, redirect, url_for
import requests


app = Flask(__name__)
app.secret_key = "IDK BRO"


@app.route('/')
def index():
    return render_template('game.html')


if __name__ == '__main__':
    app.run(debug=True)