import time
import redis
import pandas as pd
from flask import Flask, render_template, url_for
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv() 
cache = redis.Redis(host='redis', port=6379)
app = Flask(__name__)

titanic_df = pd.read_csv("Titanic-Dataset_XGboost.csv")
rows = titanic_df.head()
html_table = rows.to_html(index=False)


# create html file inside templates folder
file_path = os.path.join("templates", "titanic_table.html")

# render html string as a html file
with open(file_path, "w") as file:
    file.write(html_table)

# Group data by gender and survival status, and count the number of survivors
survivors_by_gender = titanic_df.groupby(['Sex', 'Survived']).size().unstack().fillna(0)

# Convert data to JSON format
bar_chart_data = survivors_by_gender.reset_index().to_json(orient='records')

# Write the JavaScript content to a file
with open("bar_chart_data.js", "w") as file:
    file.write(f"var data = {bar_chart_data};")

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

# def show_titanic_rows ():
                

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route('/titanic')
def titanic():
    return render_template('titanic_table.html', table = html_table)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)