# db/main.py
# Contains al the functions needed to operate the chromadb, from starting up
# and add collection data, to retrieve data and embeddings.

# Solves: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb

import numpy as np
import pandas as pd
from bokeh.models import LinearColorMapper, Div, ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import layout, column, row
from matplotlib.cm import plasma
from matplotlib.colors import rgb2hex


def exec_query(new_query):
  client = chromadb.PersistentClient(path="./db/local_client")
  collection = client.get_collection("gen_summaries")
  
  results = collection.query(
    query_texts=new_query['query_texts'],
    n_results=new_query['n_results'])
    
  return results

#https://stackoverflow.com/questions/69295551/loading-html-file-content-in-a-vue-component

def exec_plotter():
  client = chromadb.PersistentClient(path="./db/local_client")

  # Creamos la source
  desc_dataset_path = './db/datasets/genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv'
  desc_df = pd.read_csv(desc_dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])

  gen_expresion_dataset_path = './db/datasets/HiSeqV2_PANCAN'
  gen_exp_df = pd.read_table(gen_expresion_dataset_path)

  # Base df
  df = pd.merge(desc_df, gen_exp_df, on='symbol')
  
  samples = df.columns[2:]
  gen_expresions = df.loc[:, samples]

  summaries_collection = client.get_collection("gen_summaries")
  summaries_metadatas = summaries_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  set_collection = client.get_collection("SET-HiSeqV2_PANCAN")
  set_metadatas = set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]

  data = {
    'indexes': np.arange(0,len(df)),
    'symbol': df["symbol"],
    'summary': df["summary"],
    'summary_x': [d['x'] for d in summaries_metadatas],
    'summary_y':[d['y'] for d in summaries_metadatas],
    'samples_x': [d['x'] for d in set_metadatas],
    'samples_y': [d['y'] for d in set_metadatas],
    'sample_avg': [d['avg_gen_impresion'] for d in set_metadatas]
  }
  source = ColumnDataSource(data)

  paleta = [rgb2hex(plasma(x)) for x in np.linspace(0,1,7)]
  color_map = LinearColorMapper(palette=paleta,
                  low = min(data['sample_avg']),
                  high= max(data['sample_avg']))
  
  # Plot creation
  TOOLTIPS = """
    <div
      class="figure-tootip"
      style="overflow: none; width: 300px" 
    >
      <strong>Nombre</strong>
      <p>@{symbol}</p>
      <strong>Descripción</strong>
      <p>@{summary}</p>
    </div>
  """
  
  plot = figure(height=500, width=int(1439.2*0.66), margin=(0, 20, 0, 0), tooltips=TOOLTIPS,
                tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select")
  plot.scatter(x='summary_x', y='summary_y', source=source, marker="circle", radius=0.02,
                color={'field': 'sample_avg', 'transform': color_map})
  gen_plot = figure(height=500, width=int(1439.2*0.33),
      tools="crosshair,box_select,pan,reset,wheel_zoom",
      title='Vista de los genes', tooltips=TOOLTIPS)
  gen_plot.hbar(y='indexes', right='sample_avg', width=0.9, source=source,
                color={'field': 'sample_avg', 'transform': color_map})
  impresions_plot = figure(height=400, width=int(1439.2*0.33), 
      tools="crosshair,box_select,pan,reset,wheel_zoom",
      title='Expresiones de los genes', tooltips=TOOLTIPS)
  impresions_plot.scatter(x='samples_x', y='samples_y', source=source, marker="circle", radius=0.02,
                color={'field': 'sample_avg', 'transform': color_map})
  

  div_container = Div()
  impresions_container = Div()

  def callback(attr, old, new):
    print("LassoTool callback executed on Patch {}".format(old))

  source.selected.on_change('indices',callback)

  div = layout(plot, height=500)
  sumary_container = row(div, gen_plot, margin=(0, 0, 20, 0))  
  #plot_layout = layout([[div_container, plot, impresions_plot]])
  plot_layout = layout(
    sumary_container,
    row(
        column(impresions_plot)
    )
  )
  plot_layout.css_classes = ['flex','gap-2']
  
  return plot_layout