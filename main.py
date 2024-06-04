# Setup imports
from db import env_setup 

# Deploy imports
from flask import Flask, render_template
from tornado.ioloop import IOLoop
from threading import Thread

# Bokeh imports
from bokeh.embed import server_document
from bokeh.layouts import column, row, gridplot
from bokeh.server.server import Server
from bokeh.themes import Theme

# Utils imports
from utils import PlotsHelper, ToolsHelper, WidgetsHelper, DataHelper
app = Flask(__name__)
  

def bokeh_app(doc):
  # Page view variables
  set_1_name = 'KICH'
  set_2_name = 'KIRP'
  
  source = DataHelper.create_datasource(set_1_name, set_2_name)

  sum_btn, brusshing_toggle, select_1, select_2 = WidgetsHelper.get_widgets(source, set_1_name, set_2_name)
  
  summaries_plot, set_1_plot, set_2_plot = PlotsHelper.get_plots(source)
  summaries_plot, set_1_plot, set_2_plot = ToolsHelper.attach_brusshing_to_plots(source, summaries_plot, set_1_plot, set_2_plot, brusshing_toggle)
  
  #summary_div = Div(text="")
  search_bar, h1, result_list = WidgetsHelper.get_search_bar(source)
  
  plots = gridplot([[row(sum_btn, brusshing_toggle), select_1, select_2], [summaries_plot, set_1_plot, set_2_plot]], sizing_mode='scale_width')
  plots.styles = {'padding': '0 25px'}
  
  doc.add_root(column([search_bar, row(plots, sizing_mode='scale_both', min_height=700), h1, result_list], sizing_mode="scale_width"))
  doc.theme = Theme(filename="theme.yaml")

  
@app.route('/', methods=['GET'])
def bkapp_page():
  script = server_document('http://localhost:5006/bkapp')
  return render_template("index.html", script=script, template="Flask")

def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': bokeh_app}, io_loop=IOLoop(), allow_websocket_origin=["localhost:8000"])
    server.start()
    server.io_loop.start()

Thread(target=bk_worker).start()


if __name__ == '__main__':
  env_setup()
  print('Opening single process Flask app with embedded Bokeh application on http://localhost:8000/')
  print()
  print('Multiple connections may block the Bokeh app in this configuration!')
  print('See "flask_gunicorn_embed.py" for one way to run multi-process')
  app.run(port=8000)
