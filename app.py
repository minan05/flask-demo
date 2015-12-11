from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure
from bokeh.embed import components
import requests
import pandas
import datetime as dt
from StringIO import StringIO

ERROR_MESSAGE = "Could not load data for %s."

def load_data(symbol, start_date, end_date):
    url = 'https://www.quandl.com/api/v3/datasets/WIKI/%s.csv' % symbol.upper()
    params = {'start_date': start_date.strftime('%Y-%m-%d'),
              'end_date': end_date.strftime('%Y-%m-%d')}
    response = requests.get(url, params=params)
    print url, response.url, response.status_code
    if response.status_code == requests.codes.ok:
        return pandas.read_csv(StringIO(response.text), parse_dates=['Date'])
    return None

def get_plot(symbol):
    now = dt.datetime.now()
    data = load_data(symbol, now - dt.timedelta(31), now)
    if data is None:
        return '', ERROR_MESSAGE % symbol
    
    plot = figure(x_axis_type='datetime')
    datelist = data.Date.tolist()
    plot.patch(datelist + datelist[::-1], data.Low.tolist() + data.High.tolist()[::-1],
               alpha=0.5, line_width=1, legend='High/Low')
    plot.line(data.Date, data.Open, line_color='green', line_width=3, legend='Open', line_join='bevel')
    plot.line(data.Date, data.Close, line_color='orange', line_width=3, legend='Close', line_join='bevel')
    plot.yaxis.axis_label = 'Price'
    
    return components(plot)

app = Flask(__name__)

@app.route('/')
def index():
    symbol = request.args.get('symbol', '')
    script, div = get_plot(symbol) if symbol else ('', '')
    return render_template('index.html', symbol=symbol, plot_script=script, plot_div=div)

if __name__ == '__main__':
    app.run(port=33507, debug=True)
