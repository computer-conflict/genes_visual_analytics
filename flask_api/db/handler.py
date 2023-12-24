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

def exec_plotter(samples_index, set_name):
  client = chromadb.PersistentClient(path="./db/local_client")

  # Creamos la source
  desc_dataset_path = './db/datasets/genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv'
  desc_df = pd.read_csv(desc_dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])

  gen_expresion_dataset_path = f"./db/datasets/{set_name}"
  gen_exp_df = pd.read_table(gen_expresion_dataset_path)
  if samples_index != '-1':
    samples_index.append(0)
    gen_exp_df = gen_exp_df.iloc[:, samples_index]
    gen_exp_df.set_index('symbol', inplace=True)
    mean = gen_exp_df.mean(axis=1)
    gen_exp_df = gen_exp_df.reset_index()
    gen_exp_df['avg_gen_impresion'] = list(mean.reset_index()[0])

  # Base df
  df = pd.merge(desc_df, gen_exp_df, on='symbol')

  summaries_collection = client.get_collection("gen_summaries")
  summaries_metadatas = summaries_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  set_collection = client.get_collection("SET-HiSeqV2_PANCAN")
  set_metadatas = set_collection.get(ids=list(df["symbol"]), include=["metadatas"])["metadatas"]
  samples_avg = df['avg_gen_impresion'] if samples_index != '-1' else [d['avg_gen_impresion'] for d in set_metadatas]

  data = {
    'indexes': np.arange(0,len(df)),
    'symbol': df["symbol"],
    'summary': df["summary"],
    'summary_x': [d['x'] for d in summaries_metadatas],
    'summary_y':[d['y'] for d in summaries_metadatas],
    'samples_x': [d['x'] for d in set_metadatas],
    'samples_y': [d['y'] for d in set_metadatas],
    'sample_avg': samples_avg
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
      <p><strong>Nombre:</strong>@{symbol}</p>
      <p><strong>Gen avg expression:</strong>@{sample_avg}</p>
      <strong>Descripción</strong>
      <p>@{summary}</p>
    </div>
  """
  
  plot = figure(height=500, width=int(1439.2*0.66), margin=(0, 20, 0, 0), tooltips=TOOLTIPS,
                tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select",
                title='Gen summaries view')
  plot.scatter(x='summary_x', y='summary_y', source=source, marker="circle", radius=0.02,
                color={'field': 'sample_avg', 'transform': color_map})
  gen_plot = figure(height=500, width=int(1439.2*0.33),
      tools="crosshair,box_select,pan,reset,wheel_zoom",
      title='Gen view', tooltips=TOOLTIPS)
  gen_plot.hbar(y='indexes', right='sample_avg', width=0.9, source=source,
                color={'field': 'sample_avg', 'transform': color_map})
  expresions_plot = figure(height=400, width=int(1439.2*0.60), margin=(0 ,int(1439.2*0.20), 30, int(1439.2*0.20)), 
      tools="crosshair,box_select,pan,reset,wheel_zoom",
      title='Gen expression', tooltips=TOOLTIPS)
  expresions_plot.scatter(x='samples_x', y='samples_y', source=source, marker="circle", radius=0.02,
                color={'field': 'sample_avg', 'transform': color_map})

  div = layout(plot, height=500)
  sumary_container = row(div, gen_plot, margin=(0, 0, 20, 0))
  sample_selector = layout()
  sample_selector.css_classes = ['sample_selector']

  plot_layout = layout(
    sumary_container,
    row(
        column(expresions_plot)
    )
  )
  plot_layout.css_classes = ['flex','gap-2']
  
  return plot_layout

def get_set_samples(set_name):
  dataset_path = f"./db/datasets/{set_name}"
  df = pd.read_table(dataset_path).drop_duplicates()

  samples = df.columns[1:]

  return list(map(lambda sample: {'name': sample[1], 'value': sample[0]+1},enumerate(samples)))

def get_sets_list():
  return ['HiSeqV2_PANCAN', 'HiSeqV2_DLBC', 'HiSeqV2_KICH']