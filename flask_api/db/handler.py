# db/main.py
# Contains al the functions needed to operate the chromadb, from starting up
# and add collection data, to retrieve data and embeddings.

# Solves: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb

import time
import pandas as pd
from .setup import get_embeddings
from importlib import reload
from bokeh.models import HoverTool, Div
from bokeh.plotting import figure, output_file
from bokeh.layouts import layout
import umap.umap_ as umap


def exec_query(new_query):
  client = chromadb.PersistentClient(path="./db/local_client")
  collection = client.get_collection("chromagens")
  
  results = collection.query(
    query_texts=new_query['query_texts'],
    n_results=new_query['n_results'])
    
  return results

#https://stackoverflow.com/questions/69295551/loading-html-file-content-in-a-vue-component


def exec_plotter():
  print("Loading & trasnform embeddings.")
  fit = umap.UMAP()
  start_time = time.time()
  u = fit.fit_transform(get_embeddings())
  end_time = time.time()
  print(f"Transform time: {end_time - start_time} seconds")
  
  # Creamos la source
  dataset_path = './db/datasets/genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv'
  df = pd.read_csv(dataset_path, usecols=["symbol", "summary"]).dropna()
  source = df
  source['x'] = u[:,0]
  source['y']  = u[:,1]
  
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
  
  div_container = Div()
  plot = figure(width=500,height=500,tooltips=TOOLTIPS,
    tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select")
  plot.scatter(x='x', y='y', color="#74add1",
            source=source, marker="circle", radius=0.02)
  

  # tooltips
  #hover = HoverTool()
  #hover.tooltips = [
  #    ('Nombre',"@{symbol}"),
  #    ('Descripción',"@{summary}")]
  #plot.tools.append(hover)
  def update_size(attrname, old_value, new_value):
    plot.plot_width = div_container.width
    plot.plot_height = div_container.height
    
  div_container.on_change('width', update_size)
  div_container.on_change('height', update_size)
  
  plot_layout = layout([[div_container, plot]])
  
  return plot_layout