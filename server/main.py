
from threading import Thread

from flask import Flask, render_template
from tornado.ioloop import IOLoop

from bokeh.embed import server_document
from bokeh.layouts import column, row, gridplot
from bokeh.models import ColumnDataSource, Paragraph, Select, CustomJS
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.events import SelectionGeometry

# Imports for Chromadb
from db.setup import chroma_setup
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb

import numpy as np
import pandas as pd
import requests

app = Flask(__name__)


def bkapp(doc):
  set_name = 'ACC'
  client = chromadb.PersistentClient(path="./db/local_client")

  # Creamos la source
  desc_dataset_path = './db/datasets/genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv'
  desc_df = pd.read_csv(desc_dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])

  gen_expresion_dataset_path = f"./datasets/impressions_sets/{set_name}"
  gen_exp_df = pd.read_table(gen_expresion_dataset_path)

  # Base df
  df = pd.merge(desc_df, gen_exp_df, how='inner', left_on='symbol', right_on='sample')

  summaries_collection = client.get_collection("gen_summaries")
  summaries_metadatas = summaries_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  set_collection = client.get_collection(set_name)
  set_metadatas = set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  #samples_avg = df['avg_gen_impresion']

  data = {
    'indexes': np.arange(0,len(df)),
    'symbol': df["symbol"],
    'summary': df["summary"],
    'summary_x': [d['x'] for d in summaries_metadatas],
    'summary_y':[d['y'] for d in summaries_metadatas],
    'samples_x': [d['x'] for d in set_metadatas],
    'samples_y': [d['y'] for d in set_metadatas]
  }
  source = ColumnDataSource(data) 


  # ----  Datasets Selector ---- #
  def change_set(attr, old, new):
    set_path = f"./datasets/impressions_sets/{new}"
    gen_exp_df = pd.read_table(set_path)
    # Base df
    df = pd.merge(desc_df, gen_exp_df, how='inner', left_on='symbol', right_on='sample')
    set_collection = client.get_collection(new)
    set_metadatas = set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
    #samples_avg = df['avg_gen_impresion']

    new_data = {
      'indexes':   np.arange(0,len(df)),
      'symbol':    df["symbol"],
      'summary':   df["summary"],
      'summary_x': [d['x'] for d in summaries_metadatas],
      'summary_y': [d['y'] for d in summaries_metadatas],
      'samples_x': [d['x'] for d in set_metadatas],
      'samples_y': [d['y'] for d in set_metadatas]
    }
    source.data = new_data
  select_options = ['ACC', 'BRCA', 'CHOL', 'COADREAD', 'ESCA', 'HNSC', 'KIRC', 'LAML', 'LIHC']
  select = Select(title="Conjunto de datos a visualizar:", value="ACC",
                  options=select_options,
                  sizing_mode="stretch_width", margin=[10, 0])
  select.on_change('value', change_set)
  select.styles = {'padding': '0 25px'}
  select.css_classes = ["form-control", "my-custom-class"]


  # ---- Selection output ---- #
  selection_h2 = Paragraph(text='Resumen de la selección')
  selection_h2.css_classes = ["h2"]
  selection_h2.styles = {
    'padding': '5px 0',
    'display': 'block !important',
    'font-size': '1.17em !important',
    'font-weight': 'bold !important',
    'text-transform': 'uppercase !important'
  }
  selection_p = Paragraph(text='The gene selection could not be summarize')
  selection_p.styles = {
    'color': '#5C5C5C !important',
    'font-size': '1.2rem !important'
  }
  summary_group = column(row(selection_h2, margin=[20, 0]), selection_p)
  summary_group.styles = {'padding': '0 25px'}
  
  # ---- Summary output Bart-cnn ---- #
  bart_h2 = Paragraph(text='Resumen de la selección')
  bart_h2.css_classes = ["h2"]
  bart_h2.styles = {
    'padding': '5px 0',
    'display': 'block !important',
    'font-size': '1.17em !important',
    'font-weight': 'bold !important',
    'text-transform': 'uppercase !important'
  }
  bart_p = Paragraph(text='The gene selection could not be summarize')
  bart_p.styles = {
    'color': '#5C5C5C !important',
    'font-size': '1.2rem !important'
  }
  bart_group = column(row(bart_h2, margin=[20, 0]), bart_p)
  bart_group.styles = {'padding': '0 25px'}
  

  # ---- Plots ---- #
  TOOLTIPS = """
    <div
      class="figure-tootip"
      style="overflow: none; width: 300px" 
    >
      <p><strong>Nombre:</strong>@{symbol}</p>
      <p><strong>Gen avg expression:</strong>@{sample_avg}</p>
      <strong>Descripción</strong>
      <p>@{summary}</p>
    </div>
  """
  
  #  -- Plots figures & callbacks
  #     -- Summaries
  summaries_plot = figure(tooltips=TOOLTIPS,
                tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select",
                title='Representación semántica de los genes')
  summaries_plot.scatter(x='summary_x', y='summary_y', source=source, marker="circle", radius=0.02, selection_color="red", nonselection_fill_alpha=0.01)

  #     -- Gene expresions
  expresions_plot = figure(name='expresions_plot', 
      tools="crosshair,box_select,pan,reset,wheel_zoom",
      title='Representación de las expresiones genéticas', tooltips=TOOLTIPS)
  expresions_plot.scatter(x='samples_x', y='samples_y',
                          source=source, marker="circle", radius=0.02, selection_color="red",  nonselection_fill_alpha=0.01)
  
  def select_group(event):
    if event.final is True:
      indices = source.selected.indices
      gen_descriptions = '.'.join(map(str, source.data['summary'][indices]))
      
      # led-base-book-summary summarization
      led_response = requests.post('http://127.0.0.1:5000/summarize',
                       data={
                         'summary_text': gen_descriptions
                       })
      selection_h2.text = 'Resumen de la selección (led-base-book-summary)'
      selection_summary = 'The gene selection could not be summarize'
      if (led_response.status_code == 200):
        selection_summary = led_response.text
        selection_p.text = selection_summary
        
      # bart-large-cnn summarization
      bart_response = requests.post('http://127.0.0.1:5000/summarize',
                       data={
                         'summary_text': gen_descriptions
                       })
      bart_h2.text = 'Resumen de la selección (led-base-book-summary)'
      selection_summary = 'The gene selection could not be summarize'
      if (bart_response.status_code == 200):
        selection_summary = bart_response.text
        bart_p.text = selection_summary
        
  summaries_plot.on_event(SelectionGeometry, select_group)
  expresions_plot.on_event(SelectionGeometry, select_group)

  #  -- Visualization
  plots = gridplot([summaries_plot, expresions_plot], ncols=2, sizing_mode='scale_both')
  plots.styles = {'padding': '0 25px'}


  doc.add_root(column(select, plots, summary_group, sizing_mode="stretch_both", min_height=700))

  doc.theme = Theme(filename="theme.yaml")


@app.route('/searcher', methods=['GET'])
def searcher_page():
  script = server_document('http://localhost:5006/bkapp')
  return render_template("index.html", script=script, template="Flask")

@app.route('/', methods=['GET'])
def bkapp_page():
  script = server_document('http://localhost:5006/bkapp')
  return render_template("index.html", script=script, template="Flask")

def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': bkapp}, io_loop=IOLoop(), allow_websocket_origin=["localhost:8000"])
    server.start()
    server.io_loop.start()

Thread(target=bk_worker).start()


if __name__ == '__main__':    
  chroma_setup()
  print('Opening single process Flask app with embedded Bokeh application on http://localhost:8000/')
  print()
  print('Multiple connections may block the Bokeh app in this configuration!')
  print('See "flask_gunicorn_embed.py" for one way to run multi-process')
  app.run(port=8000)
