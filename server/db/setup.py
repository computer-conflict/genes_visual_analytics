# db/main.py
# Contains al the functions needed to operate the chromadb, from starting up
# and add collection data, to retrieve data and embeddings.
import numpy as np
import pandas as pd

# Solves: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb, time

import umap.umap_ as umap
from joblib import Parallel, delayed

def create_summary_collection(client, collection_name, df_path):
  dataset_path = f"./db/datasets/{df_path}"
  df = pd.read_csv(dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])
  
  collection = client.get_or_create_collection(collection_name)
  print(f"Creating {collection_name} embeddings.")
  start_time = time.time()
  collection.add(
      documents= list(df["summary"]),
      metadatas= df[['symbol', 'summary']].to_dict(orient='records'),
      ids=list(df["symbol"]))
  end_time = time.time()
  print(f"Done: {end_time - start_time} s")
  embeddings = collection.get(ids=list(df["symbol"]), include=['embeddings'])['embeddings']
  

  fit = umap.UMAP()
  print(f"Preparing {collection_name} dataframe.")
  start_time = time.time()
  summaries_u = fit.fit_transform(embeddings)
  end_time = time.time()
  print(f"Done in: {end_time - start_time} s")

  df['x'] = summaries_u[:, 0]
  df['y'] = summaries_u[:, 1]

  print(f"Updating {collection_name}.")
  start_time = time.time()
  collection.update(
    ids=list(df["symbol"]),
    metadatas= df[['symbol', 'summary', 'x', 'y']].to_dict(orient='records'))
  end_time = time.time()
  print(f"Done: {end_time - start_time} s")


def add_doc_to_collection(collection, row):
  collection.add(
    documents= row[0],
    embeddings=list(row[1:-3]),
    metadatas= {
      'symbol': row[0],
      'x': row[-1],
      'y': row[-2],
      'avg': row[-3]
    },
    ids=[row[0]])
  return True
  

def create_set_collection(client, collection_name):
  print(f"Creating collection {collection_name}.")
  
  # Create set collections
  collection = client.create_collection(collection_name)
  
  gen_expresion_dataset_path = f"./db/sets/{collection_name}"
  gen_exp_df = pd.read_table(gen_expresion_dataset_path).drop_duplicates()
  
  # Calc avg expression 
  gen_exp_df.set_index('sample', inplace=True)
  mean = gen_exp_df.mean(axis=1)
  gen_exp_df = gen_exp_df.reset_index()
  gen_exp_df['avg_gen_impresion'] = list(mean.reset_index()[0])
  
  
  samples = gen_exp_df.columns[1:]
  gen_expresions = gen_exp_df.loc[:, samples]

  fit = umap.UMAP()
  print(f"Applying umap to {collection_name} gene impresions.")
  start_time = time.time()
  gen_expresions_u = fit.fit_transform(gen_expresions)
  end_time = time.time()
  print(f"Done: {end_time - start_time} s")

  gen_exp_df['x'] = gen_expresions_u[:, 0]
  gen_exp_df['y'] = gen_expresions_u[:, 1]

  print(f"Adding {collection_name} set to Chroma.")
  start_time = time.time()
  Parallel(n_jobs=8, backend='threading')(delayed(add_doc_to_collection)(collection, row) for row in gen_exp_df.itertuples(index=False))
  #for row in gen_exp_df.itertuples(index=False):
  #  collection.add(
  #    documents= row[0],
  #    metadatas= {
  #      'symbol': row[0],
  #      'x': row[-1],
  #      'y': row[-2],
  #      'avg': row[-3]
  #    },
  #    ids=[row[0]])
  #collection.add(
  #  documents= list(gen_exp_df["symbol"]),
  #  metadatas= gen_exp_df[['symbol', 'x', 'y', 'avg_gen_impresion']].to_dict(orient='records'),
  #  ids=list(gen_exp_df["symbol"]))
  #end_time = time.time()
  print(f"Collection created: {end_time - start_time} s")

def load_sample_set(client, collection_name):
  try:
    client.get_collection(collection_name)
  except:
    create_set_collection(client, collection_name)
     

  
#Db setup
def chroma_setup():
  print("Fetching local client...")
  # Create db and make a new collection
  client = chromadb.PersistentClient(path="./db/local_client")
  
  # Load dataset gen summaries
  try:
    client.get_collection('gen_summaries')
  except:
    create_summary_collection(client, 'gen_summaries', 'genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv')
        
  samples = ['ACC', 'BRCA', 'CHOL', 'COADREAD', 'ESCA', 'HNSC', 'KIRC', 'LAML', 'LIHC',
            'LUSC', 'OV1', 'PCPG', 'READ', 'SKCM', 'TGCT', 'THYM', 'UCS', 'BLCA', 'CESC',
            'COAD', 'DLBC', 'GBM', 'KICH', 'KIRP', 'LGG', 'LUAD', 'MESO', 'PAAD', 'PRAD', 'SARC', 'STAD', 'THCA', 'UCEC', 'UVM']
  
  samples = ['ACC', 'BRCA', 'CHOL', 'COADREAD', 'ESCA', 'HNSC', 'KIRC', 'LAML', 'LIHC']

  print(f"Loading database...")
  start_time = time.time()
  Parallel(n_jobs=4, backend='threading')(delayed(load_sample_set)(client, sample) for sample in samples)
  end_time = time.time()
  print(f"Setup done: {end_time - start_time} s")
  
  