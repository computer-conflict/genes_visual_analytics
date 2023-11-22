# db/main.py
# Contains al the functions needed to operate the chromadb, from starting up
# and add collection data, to retrieve data and embeddings.
#import pandas as pd
import pandas as pd

# Solves: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb


def exec_query(new_query):
  client = chromadb.PersistentClient(path="./db/local_client")
  collection = client.get_collection("chromagens")
  
  results = collection.query(
    query_texts=new_query['query_texts'],
    n_results=new_query['n_results'])
    
  return results

#https://stackoverflow.com/questions/69295551/loading-html-file-content-in-a-vue-component
from bokeh.models import HoverTool
from bokeh.plotting import figure, output_file
import umap.umap_ as umap

def exec_plotter():
  client = chromadb.PersistentClient(path="./db/local_client")
  collection = client.get_collection("chromagens")

  
  print("Loading & trasnform embeddings.")
  embeddings = collection.get(include=['embeddings'])['embeddings']  
  fit = umap.UMAP()
  u = fit.fit_transform(embeddings)
  print("Done.")
  

  

  
  #Fake embeddings for dev
  #u = np.empty((len(df), 2))
  #for i in range(0, len(df)):
  #  np.random.seed(i)
  #  
  #  u[i] = [np.random.randint(1, 11), np.random.randint(1, 11)]
  
  filename = __file__.split('.')[0]+'.html'
  output_file(filename)
  # Creamos la source
  dataset_path = './db/datasets/genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv'
  df = pd.read_csv(dataset_path, usecols=["symbol", "summary"]).dropna()
  source = df
  source['x'] = u[:,0]
  source['y']  = u[:,1]
  
  # crear figura y plot
  # en el campo color se usa color_map para mapear "categoría --> color" en cada muestra
  plot = figure()
  plot.scatter(x='x', y='y', color="#74add1",
            source=source, marker="circle", radius=0.02)
  
  # tooltips
  hover = HoverTool()
  hover.tooltips = [
      ('Nombre',"@{symbol}"),
      ('Descripción',"@{summary}")]
  plot.tools.append(hover)
  
  return plot