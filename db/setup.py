# Solves: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb


# Umap
import umap.umap_ as umap
from sentence_transformers import SentenceTransformer

# Clustering
from sklearn.cluster import OPTICS

# Utils imports
import pandas as pd
import time, json, os
import pandas as pd
import numpy as np

# ------------------------------------------- #
#      Initialize enviroment variables        #
# ------------------------------------------- #
client = chromadb.PersistentClient(path="./db/chromadb_client")
umap = umap.UMAP(metric='minkowski', metric_kwds={'p': 3})
clustering = OPTICS()


# -- Functions -- //
def get_umap_dimensions(embeddings):
  print(" - UMAP time:")
  start_time = time.time()
  summaries_2dimensions = umap.fit_transform(embeddings)
  x_list = summaries_2dimensions[:, 0]
  y_list = summaries_2dimensions[:, 1]
  print(f"    {time.time() - start_time} s")
  return [x_list, y_list]

def get_collection_clusters(embeddings):  
  print(f" - Clustering time:")
  start_time = time.time()
  clustering.fit(embeddings)
  print(len(np.unique(clustering.labels_)))
  print(f"    {time.time() - start_time} s")
  return clustering.labels_

def transform_summaries_to_embeddings(summaries):
  transformer = SentenceTransformer("all-MiniLM-L6-v2")
  return transformer.encode(summaries)
  
def create_summary_collection(collection_name):
  dataset_path = f"./db/datasets/raw_datasets/semantic_dataframe.csv"  
  df = pd.read_csv(dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])
  
  # SentenceTransformer
  gene_summaries = df['summary'].tolist()
  embeddings = transform_summaries_to_embeddings(gene_summaries)

  df['x'], df['y'] = get_umap_dimensions(embeddings)  
  df['cluster'] = get_collection_clusters(embeddings)

  print(f"Dump {collection_name} into Chroma.")
  start_time = time.time()
  collection = client.get_or_create_collection(collection_name)
  collection.add(
    ids=list(df["symbol"]),
    documents= list(df["summary"]),
    metadatas= df[['symbol', 'summary', 'x', 'y', 'cluster']].to_dict(orient='records'))
  end_time = time.time()
  print(f"Done insertion: {end_time - start_time} s")

def verify_semantic_info():
  try:
    client.get_collection('gene_summaries')
  except:
    create_summary_collection('gene_summaries')


def create_gene_expressions_collection(dataset):  
  gene_expression_dataset_path = f"./db/datasets/raw_datasets/{dataset.split('_')[0]}"
  df = pd.read_table(gene_expression_dataset_path)
    
  samples = df.columns[1:]
  gene_expressions = df.loc[:, samples]

  df['cluster'] = get_collection_clusters(gene_expressions)
  df['x'], df['y'] = get_umap_dimensions(gene_expressions)  
  
  df.to_csv(f"./db/datasets/modified_datasets/{dataset}.csv", index=False)  

def get_tcga_datasets():
  with open("./db/tcga_datasets_index_test.json") as tcgaFile:
    data = json.load(tcgaFile)
  return data.keys()

def verify_expressions_info():
  expressions_datasets = get_tcga_datasets()
  datasets_count = len(expressions_datasets)
  
  for index,dataset in enumerate(expressions_datasets):
    modified_dataset_path = f"./db/datasets/modified_datasets/{dataset}.csv"
    
    if not os.path.exists(modified_dataset_path):
      print(f"---------------------------------------{index}/{datasets_count}---------------------------------------")
      print(f"Processing: {dataset}")
      start_time = time.time()
      create_gene_expressions_collection(dataset)
      print(f"Done processing {dataset}: {time.time() - start_time} s")
      print("")
    



# Main function
# -------------------------------------------
# Checks if the genes descriptions dataframe is loaded in Chromadb
# and ensures the CSV files containing genes expression csv are
# present in the corresponding folder.
#
# This function can also be launched executing this file. 
def env_setup():
  datasets_folder = "./db/datasets/modified_datasets/"
  os.makedirs(datasets_folder, exist_ok=True)
    
  verify_semantic_info()
  verify_expressions_info()


if __name__ == '__main__':
  env_setup()
  
  