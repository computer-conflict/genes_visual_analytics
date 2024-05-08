
from threading import Thread

from flask import Flask, render_template
from tornado.ioloop import IOLoop

from bokeh.embed import server_document
from bokeh.layouts import column, row, gridplot
from bokeh.models import ColumnDataSource, Paragraph, Select, Div, TextInput
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.events import SelectionGeometry, MouseMove

# Imports for Chromadb
from db.setup import chroma_setup
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb

import numpy as np
import pandas as pd
import requests
import math

app = Flask(__name__)

def getDataframe(set_name, compare_set_name):
  desc_dataset_path = './db/datasets/genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv'
  desc_df = pd.read_csv(desc_dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])

  gen_expresion_dataset_path = f"./db/datasets/impressions_sets/{set_name}"
  gen_exp_df = pd.read_table(gen_expresion_dataset_path)

  compare_dataset_path = f"./db/datasets/impressions_sets/{compare_set_name}"
  compare_df = pd.read_table(compare_dataset_path)

  # Base df
  df = pd.merge(desc_df, gen_exp_df, how='inner', left_on='symbol', right_on='sample')
  result_df = pd.merge(df, compare_df, how='inner', left_on='symbol', right_on='sample')
  return result_df
  
def bkapp(doc):
  set_name = 'KICH'
  compare_set_name = 'KIRP'
  client = chromadb.PersistentClient(path="./db/local_client")

  # Creamos la source
  df = getDataframe(set_name, compare_set_name)

  summaries_collection = client.get_collection("gen_summaries")
  summaries_metadatas = summaries_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  
  set_collection = client.get_collection(set_name)
  set_metadatas = set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  
  compare_set_collection = client.get_collection(compare_set_name)
  compare_metadatas = compare_set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]

  data = {
    'indexes': np.arange(0,len(df)),
    'symbol': [d['symbol'] for d in summaries_metadatas],
    'summary': [d['summary'] for d in summaries_metadatas],
    'summary_x': [d['x'] for d in summaries_metadatas],
    'summary_y': [d['y'] for d in summaries_metadatas],
    'samples_x': [d['x'] for d in set_metadatas],
    'samples_y': [d['y'] for d in set_metadatas],
    'compare_x': [d['x'] for d in compare_metadatas],
    'compare_y': [d['y'] for d in compare_metadatas]
  }
  source = ColumnDataSource(data) 


  # ----  Datasets Selector ---- #
  def change_set(attr, old, new):
    compare_set_name = compare_select.value
    df = getDataframe(new, compare_set_name)
    set_collection = client.get_collection(new)
    set_metadatas = set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
    source.data['samples_x'] = [d['x'] for d in set_metadatas]
    source.data['samples_y'] = [d['y'] for d in set_metadatas]
  select_options = ['ACC', 'BRCA', 'CHOL', 'COADREAD', 'ESCA', 'HNSC', 'KIRC', 'LAML', 'LIHC',
            'LUSC', 'OV1', 'PCPG', 'READ', 'SKCM', 'TGCT', 'THYM', 'UCS', 'BLCA', 'CESC',
            'COAD', 'DLBC', 'GBM', 'KICH', 'KIRP', 'LGG', 'LUAD', 'MESO', 'PAAD', 'PRAD', 'SARC', 'STAD', 'THCA', 'UCEC', 'UVM']
  select = Select(title="Conjunto de datos a visualizar:", value=set_name,
                  options=select_options,
                  sizing_mode="stretch_width", margin=[10, 0])
  select.on_change('value', change_set)
  select.styles = {'padding': '0 25px'}
  
  def change_compare_set(attr, old, new):
    set_name = select.value
    df = getDataframe(set_name, new)
    
    compare_set_collection = client.get_collection(new)
    compare_metadatas = compare_set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
    source.data['compare_x'] = [d['x'] for d in compare_metadatas]
    source.data['compare_y'] = [d['y'] for d in compare_metadatas]
  compare_select = Select(title="Conjunto de datos a comparar:", value=compare_set_name,
                  options=select_options,
                  sizing_mode="stretch_width", margin=[10, 0])
  compare_select.on_change('value', change_compare_set)
  compare_select.styles = {'padding': '0 25px'}


  # ---- Summary output Bart-cnn ---- #
  led_h2 = Paragraph(text='Resumen de la selección (led-base-book-summary)')
  led_h2.css_classes = ["h2"]
  led_h2.styles = {
    'padding': '5px 0',
    'display': 'block !important',
    'font-size': '1.17em !important',
    'font-weight': 'bold !important',
    'text-transform': 'uppercase !important'
  }
  led_p = Paragraph(text='The gene selection could not be summarize')
  led_p.styles = {
    'color': '#5C5C5C !important',
    'font-size': '1.2rem !important'
  }
  led_group = column(row(led_h2, margin=[20, 0]), led_p)
  led_group.styles = {'padding': '0 25px'}
  
  bart_h2 = Paragraph(text='Resumen de la selección  (Bart-large-cnn)')
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
  
  gpt_header = Div(text="", width=200, height=50)
  gpt_p = Paragraph(text='The gene selection could not be summarize')
  gpt_p.styles = {
    'color': '#5C5C5C !important',
    'font-size': '1.2rem !important'
  }
  gpt_group = column(gpt_header, gpt_p)
  gpt_group.styles = {'padding': '0 25px'}
  
  gene_h2 = Div(text="<h2>Genes seleccionados</h2>", width=200, height=50)
  selected_gene_list = []
  gene_display = column()
  gene_display.styles = {'display': 'flex', 'flex-wrap': 'wrap', 'flex-direction': 'row'}
  gene_group = column(gene_h2, gene_display)
  gene_group.styles = {'padding': '0 25px'}
  

  # ---- Plots ---- #
  TOOLTIPS = """
    <div
      class="figure-tootip"
      style="overflow: none; width: 300px" 
    >
      <p><strong>Nombre:</strong>@{symbol}</p>
      <strong>Descripción</strong>
      <p>@{summary}</p>
    </div>
  """
  
  #  -- Plots figures & callbacks
  #     -- Summaries
  summaries_plot = figure(tooltips=TOOLTIPS, match_aspect=True,
                tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select",
                title='Representación semántica de los genes', sizing_mode='scale_width')
  summaries_plot.scatter(x='summary_x', y='summary_y', source=source, marker="circle", radius=0.02, selection_color="red", nonselection_fill_alpha=0.01)

  #     -- Gene expresions
  expresions_plot = figure(name='expresions_plot', match_aspect=True,
      tools="crosshair,box_select,pan,reset,wheel_zoom",
      title='Representación de las expresiones genéticas', tooltips=TOOLTIPS)
  expresions_plot.scatter(x='samples_x', y='samples_y',
                          source=source, marker="circle", radius=0.02, selection_color="red",  nonselection_fill_alpha=0.01)
  
  compare_plot = figure(name='expresions_plot', match_aspect=True,
      tools="crosshair,box_select,pan,reset,wheel_zoom",
      title='Representación de las expresiones genéticas', tooltips=TOOLTIPS)
  compare_plot.scatter(x='compare_x', y='compare_y',
                          source=source, marker="circle", radius=0.02, selection_color="red",  nonselection_fill_alpha=0.01)
  
  def callback_handler(event):    
    gene_name = event.item.text
    print(f"Se hizo clic en el enlace para el gen {gene_name}")
  

  
  def select_group(event):
    if event.final is True:
      indices = source.selected.indices
      
      gen_descriptions = '.'.join(map(str, np.take(source.data['summary'], indices).tolist()))
            
      gpt_response = requests.post('http://127.0.0.1:5000/summarize',
               data={
                 'gen_descriptions': gen_descriptions
               })
      gpt_header.text = '<h2>Descripciones resumidas (GTP2)</h2>'
      selection_summary = 'The gene selection could not be summarize'
      if (gpt_response.status_code == 200):
        selection_summary = gpt_response.text
      gpt_p.text = selection_summary
          
            ## bart-large-cnn summarization
      #if(True):
      #  bart_response = requests.post('http://127.0.0.1:5000/summarize_bart',
      #                   data={
      #                     'summary_text': list(source.data['summary'][indices])
      #                   })
      #  bart_h2.text = 'Resumen de la selección (Bart-large-cnn)'
      #  selection_summary = 'The gene selection could not be summarize'
      #  if (bart_response.status_code == 200):
      #    selection_summary = bart_response.text
      #  bart_p.text = selection_summary
      #
      ## led-base-book-summary summarization
      #if(True):
      #  led_response = requests.post('http://127.0.0.1:5000/summarize_led',
      #           data={
      #             'summary_text': gen_descriptions
      #           })
      #  led_h2.text = 'Resumen de la selección (led-base-book-summary)'
      #  selection_summary = 'The gene selection could not be summarize'
      #  if (led_response.status_code == 200):
      #    selection_summary = led_response.text
      #  led_p.text = selection_summary
      #        
      selected_gene_list = []
      for gene in np.take(source.data['symbol'], indices).tolist():      
        link_html = f"<a href='#'>{gene}</a>"
        div_enlace = Div(text=link_html)
        div_enlace.on_event('click', callback_handler)
        
        selected_gene_list.append(div_enlace)
      gene_display.children = selected_gene_list
        
  summaries_plot.on_event(SelectionGeometry, select_group)
  expresions_plot.on_event(SelectionGeometry, select_group)
  compare_plot.on_event(SelectionGeometry, select_group)

  #  -- Visualization
  plots = gridplot([[summaries_plot], [gridplot([[expresions_plot, compare_plot]], sizing_mode='scale_both')]], sizing_mode='scale_both')
  plots.styles = {'padding': '0 25px'}

  doc.add_root(column([select, compare_select, row(plots, sizing_mode='scale_both', min_height=700), gpt_group, gene_group], sizing_mode="scale_width"))
  doc.theme = Theme(filename="theme.yaml")

def brushing(doc):
  set_name = 'KICH'
  compare_set_name = 'KIRP'
  client = chromadb.PersistentClient(path="./db/local_client")

  # Creamos la source
  df = getDataframe(set_name, compare_set_name)

  summaries_collection = client.get_collection("gen_summaries")
  summaries_metadatas = summaries_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  
  set_collection = client.get_collection(set_name)
  set_metadatas = set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  
  compare_set_collection = client.get_collection(compare_set_name)
  compare_metadatas = compare_set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]

  data = {
    'indexes': np.arange(0,len(df)),
    'symbol': [d['symbol'] for d in summaries_metadatas],
    'summary': [d['summary'] for d in summaries_metadatas],
    'summary_x': [d['x'] for d in summaries_metadatas],
    'summary_y': [d['y'] for d in summaries_metadatas],
    'samples_x': [d['x'] for d in set_metadatas],
    'samples_y': [d['y'] for d in set_metadatas],
    'compare_x': [d['x'] for d in compare_metadatas],
    'compare_y': [d['y'] for d in compare_metadatas]
  }
  source = ColumnDataSource(data) 


  # ----  Datasets Selector ---- #
  def change_set(attr, old, new):
    compare_set_name = compare_select.value
    df = getDataframe(new, compare_set_name)
    set_collection = client.get_collection(new)
    set_metadatas = set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
    source.data['samples_x'] = [d['x'] for d in set_metadatas]
    source.data['samples_y'] = [d['y'] for d in set_metadatas]
  select_options = ['ACC', 'BRCA', 'CHOL', 'COADREAD', 'ESCA', 'HNSC', 'KIRC', 'LAML', 'LIHC',
            'LUSC', 'OV1', 'PCPG', 'READ', 'SKCM', 'TGCT', 'THYM', 'UCS', 'BLCA', 'CESC',
            'COAD', 'DLBC', 'GBM', 'KICH', 'KIRP', 'LGG', 'LUAD', 'MESO', 'PAAD', 'PRAD', 'SARC', 'STAD', 'THCA', 'UCEC', 'UVM']
  select = Select(title="Conjunto de datos a visualizar:", value=set_name,
                  options=select_options,
                  sizing_mode="stretch_width", margin=[10, 0])
  select.on_change('value', change_set)
  select.styles = {'padding': '0 25px'}
  
  def change_compare_set(attr, old, new):
    set_name = select.value
    df = getDataframe(set_name, new)
    
    compare_set_collection = client.get_collection(new)
    compare_metadatas = compare_set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
    source.data['compare_x'] = [d['x'] for d in compare_metadatas]
    source.data['compare_y'] = [d['y'] for d in compare_metadatas]
  compare_select = Select(title="Conjunto de datos a comparar:", value=compare_set_name,
                  options=select_options,
                  sizing_mode="stretch_width", margin=[10, 0])
  compare_select.on_change('value', change_compare_set)
  compare_select.styles = {'padding': '0 25px'}
  

  # ---- Plots ---- #
  #  -- Plots figures & callbacks
  #     -- Summaries
  summaries_plot = figure(match_aspect=True, tools="crosshair,wheel_zoom",
      title='Representación semántica de los genes', sizing_mode='scale_width')
  source_sel = ColumnDataSource({'x':[],'y':[]})
  
  summaries_plot.scatter(x='summary_x', y='summary_y', source=source, marker="circle", radius=0.02, selection_color="red", nonselection_fill_alpha=0.01)
  
  #     -- Gene expresions
  expresions_plot = figure(name='expresions_plot', match_aspect=True, tools="crosshair,wheel_zoom",
      title='Representación de las expresiones genéticas')
  expresions_plot.scatter(x='samples_x', y='samples_y',
                          source=source, marker="circle", radius=0.02, selection_color="red",  nonselection_fill_alpha=0.01)
  
  compare_plot = figure(name='expresions_plot', match_aspect=True, tools="crosshair,wheel_zoom",
      title='Representación de las expresiones genéticas')
  compare_plot.scatter(x='compare_x', y='compare_y',
                          source=source, marker="circle", radius=0.02, selection_color="red",  nonselection_fill_alpha=0.01)
  
  
  def on_mouse_move(e):
    # OBTENER PUNTOS EN UN ENTORNO DEL RATÓN d(mousex,mousey) < dmax
    x = e.x
    xs= e.sx
    y = e.y
    ys= e.sy
    
    # DISTANCIAS d(mousex,mousey)
    #dist = xs.map(lambda d,i: math.pow(xs[i]-x,2)+math.pow(ys[i]-y,2))
    #
    ## INDICES SELECCIONADOS d(mousex,mousey) < dmax
    #idx = dist.map(lambda d,i: i if d<3 else -1).filter(lambda d: d > 0)
    #
    ## ÍNDICE DEL PUNTO MÁS CERCANO AL RATÓN
    #bmu = dist.index(min(dist));
    print(f"x: {x}, y: {y}")
    #source_sel.data['x'] = [x]
    #source_sel.data['y'] = [y]
        
  summaries_plot.on_event(MouseMove, on_mouse_move)
  expresions_plot.on_event(MouseMove, on_mouse_move)
  compare_plot.on_event(MouseMove, on_mouse_move)

  #  -- Visualization
  plots = gridplot([[summaries_plot], [gridplot([[expresions_plot, compare_plot]], sizing_mode='scale_both')]], sizing_mode='scale_both')
  plots.styles = {'padding': '0 25px'}

  doc.add_root(column([select, compare_select, row(plots, sizing_mode='scale_both', min_height=700)], sizing_mode="scale_width"))
  doc.theme = Theme(filename="theme.yaml")


def searcher(doc):
  # ---- Plots ---- #
  client = chromadb.PersistentClient(path="./db/local_client")
  summaries_collection = client.get_collection("gen_summaries")
  summaries_metadatas = summaries_collection.get(include=["metadatas"])["metadatas"]
  data = {
    'symbol': [d['symbol'] for d in summaries_metadatas],
    'summary': [d['summary'] for d in summaries_metadatas],
    'summary_x': [d['x'] for d in summaries_metadatas],
    'summary_y': [d['y'] for d in summaries_metadatas],
  }
  source = ColumnDataSource(data) 
  TOOLTIPS = """
    <div
      class="figure-tootip"
      style="overflow: none; width: 300px" 
    >
      <p><strong>Nombre:</strong>@{symbol}</p>
      <strong>Descripción</strong>
      <p>@{summary}</p>
    </div>
  """
  summaries_plot = figure(tooltips=TOOLTIPS, match_aspect=True, sizing_mode='scale_both',
                tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select",
                title='Representación semántica de los genes')
  summaries_plot.scatter(x='summary_x', y='summary_y', source=source, marker="circle", radius=0.02, selection_color="red", nonselection_fill_alpha=0.01)
  summaries_plot.styles = {'padding': '0 25px'}

  def search_query(attr, old, new):
    client = chromadb.PersistentClient(path="./db/local_client")
    collection = client.get_collection("gen_summaries")
    results = collection.query(
      query_texts=new,
      n_results=50)
    
    results['metadatas'][0][0]
    
    h1.text = '<h2>Genes seleccionados</h2>'
    results_widgets = []
    result_list.children = []
    for result in results['metadatas'][0]:
      result_group = column(sizing_mode="stretch_width")
      
      header = Div(text=f"<h2>{result['symbol']}</h2>")
      header.styles = {'padding': '0 25px'}
      result_group.children.append(header)   
      text = Div(text=f"<p>{result['summary']}</p>")
      text.styles = {'padding': '0 25px'}
      result_group.children.append(text)  
      
      results_widgets.append(result_group)
    result_list.children = list(results_widgets)
    
    symbols = list(map(lambda r: r['symbol'],results['metadatas'][0]))
    indices = list(map(lambda sym: source.data['symbol'].index(sym), symbols))
    source.selected.indices = indices    
  search_bar = TextInput(title="Conjunto de datos a visualizar:", placeholder='Introduce la descripción del gen...',
                sizing_mode="stretch_width", margin=[10, 0])
  search_bar.on_change('value', search_query)
  search_bar.styles = {'padding': '0 25px'}
  
  #  -- Results display
  h1 = Div(text="<h1></h1>")
  h1.styles = {'padding': '0 25px'}
  result_list = column(sizing_mode="stretch_width")


  doc.add_root(column([search_bar, row(summaries_plot, sizing_mode='stretch_both', min_height=500), h1, result_list], sizing_mode="scale_width"))
  doc.theme = Theme(filename="theme.yaml")

@app.route('/searcher', methods=['GET'])
def searcher_page():
  script = server_document('http://localhost:5006/searcher')
  return render_template("searcher.html", script=script, template="Flask")

@app.route('/', methods=['GET'])
def bkapp_page():
  script = server_document('http://localhost:5006/bkapp')
  return render_template("index.html", script=script, template="Flask")

@app.route('/brushing', methods=['GET'])
def brushing_page():
  script = server_document('http://localhost:5006/brushing')
  return render_template("brushing.html", script=script, template="Flask")

def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': bkapp, '/searcher': searcher, '/brushing': brushing}, io_loop=IOLoop(), allow_websocket_origin=["localhost:8000"])
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
