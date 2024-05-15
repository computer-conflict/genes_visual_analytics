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
from sentence_transformers import SentenceTransformer
from sklearn.cluster import SpectralClustering, AffinityPropagation, AgglomerativeClustering

def create_summary_collection(client, collection_name, df_path):
  dataset_path = f"./db/datasets/{df_path}"
  df = pd.read_csv(dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])
  
  collection = client.get_or_create_collection(collection_name)
  print(f"Creating {collection_name} embeddings.")
  model = SentenceTransformer("all-MiniLM-L6-v2")
  gene_summaries = df['summary'].tolist()
  
  embeddings = model.encode(gene_summaries)

  fit = umap.UMAP()
  print(f"UMAP + Spectral Clustering for: {collection_name}.")
  start_time = time.time()
  summaries_u = fit.fit_transform(embeddings)
  clustering = SpectralClustering(n_clusters=2, assign_labels='discretize', random_state=0).fit(embeddings)
  end_time = time.time()
  print(f"Umap done in: {end_time - start_time}s. Context: {collection_name}")

  df['x'] = summaries_u[:, 0]
  df['y'] = summaries_u[:, 1]
  df['cluster'] = clustering.labels_

  print(f"Updating {collection_name}.")
  start_time = time.time()
  collection.add(
    ids=list(df["symbol"]),
    documents= list(df["summary"]),
    metadatas= df[['symbol', 'summary', 'x', 'y', 'cluster']].to_dict(orient='records'))
  end_time = time.time()
  print(f"Done: {end_time - start_time} s")



def fit_cluster_by_intervals(cluster_to_fit, df):
  steps_size = int(len(df)/5)
  for i in range(0, len(df), steps_size):
    cluster_to_fit = cluster_to_fit.fit(df.iloc[i:i+steps_size])
    
  return cluster_to_fit

def predict_clusters_for_df(cluster_algorithm, df):
  labels = []
  steps_size = int(len(df)/5)
  for i in range(0, len(df), steps_size):
    labels.append(cluster_algorithm.fit_predict(df.iloc[i:i+steps_size]))  
  return np.concatenate(labels)

def create_set_collection(client, collection_name, save_in_chromadb=False):
  print(f"Creating collection {collection_name}.")
  
  # Create set collections
  collection = client.create_collection(collection_name)
  
  gen_expresion_dataset_path = f"./db/datasets/impressions_sets/{collection_name.split('_')[0]}"
  gen_exp_df = pd.read_table(gen_expresion_dataset_path)
  
  # Calc avg expression 
  gen_exp_df.set_index('sample', inplace=True)
  mean = gen_exp_df.mean(axis=1)
  gen_exp_df = gen_exp_df.reset_index()
  gen_exp_df['avg_gen_impresion'] = list(mean.reset_index()[0])
  
  samples = gen_exp_df.columns[1:]
  gen_expresions = gen_exp_df.loc[:, samples]

  fit = umap.UMAP()
  #gen_expresions_u = fit.fit_transform(gen_expresions)
  #clustering = SpectralClustering(n_clusters=12, assign_labels='discretize', random_state=0).fit(gen_expresions.iloc[0:2000])
  #clustering = AffinityPropagation(random_state=5).fit(dfas)

  # Clustering
  print(f"Clustering for: {collection_name}.")
  clustering_time = time.time()
  cluster_algorithm = AgglomerativeClustering(n_clusters=6)
  cluster_algorithm = fit_cluster_by_intervals(cluster_algorithm, gen_expresions)
  labels = predict_clusters_for_df(cluster_algorithm, gen_expresions)
  print(f"Clustering done in: {time.time() - clustering_time}s. Context: {collection_name}")
  
  # U map
  fit = umap.UMAP()
  print(f"UMAP for: {collection_name}.")
  umap_time = time.time()
  gen_expresions_u = fit.fit_transform(gen_expresions)
  print(f"Umap done in: {time.time() - umap_time}s. Context: {collection_name}")
  
  gen_exp_df['x'] = gen_expresions_u[:, 0]
  gen_exp_df['y'] = gen_expresions_u[:, 1]
  gen_exp_df['cluster'] = labels
  gen_exp_df.to_csv(f"./db/datasets/modified_sets/{collection_name}.csv", index=False)

  if(save_in_chromadb):
    print(f"Adding {collection_name} set to Chroma.")
    chroma_time = time.time()
    for row in gen_exp_df.itertuples(index=False):
      collection.add(
        documents= row[0],
        embeddings=list(row[1:-3]),
        metadatas= {
          'symbol': row[0],
          'cluster':row[-1],
          'x': row[-2],
          'y': row[-3],
          'avg': row[-4]
        },
      ids=[row[0]])
    print(f"Adding time: {time.time() - chroma_time}s. Context: {collection_name}")

def load_sample_set(client, collection_name):
  try:
    client.get_collection(collection_name)
  except:
    create_set_collection(client, collection_name, True)
  
#Db setup
def chroma_setup():
  print("Fetching local client...")
  # Create db and make a new collection
  client = chromadb.PersistentClient(path="./db/local_client")
  collections = client.list_collections()
  for collection in collections:
    print(collection)

  # Load dataset gen summaries
  try:
    client.get_collection('gen_summaries')
  except:
    create_summary_collection(client, 'gen_summaries', 'genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv')
      
      
  #client.delete_collection('KICH')
  #client.delete_collection('KIRP_clustering-spectral')
  #client.delete_collection('KICH_clustering-spectral')
  samples = ['ACC', 'BRCA', 'CHOL', 'COADREAD', 'ESCA', 'HNSC', 'KIRC', 'LAML', 'LIHC',
            'LUSC', 'OV1', 'PCPG', 'READ', 'SKCM', 'TGCT', 'THYM', 'UCS', 'BLCA', 'CESC',
            'COAD', 'DLBC', 'GBM', 'KICH', 'KIRP', 'LGG', 'LUAD', 'MESO', 'PAAD', 'PRAD', 'SARC', 'STAD', 'THCA', 'UCEC', 'UVM']
  samples = ['KIRP_clustering-spectral', 'KICH_clustering-spectral']
    
  print(f"Loading database...")
  start_time = time.time()
  Parallel(n_jobs=1, backend='threading')(delayed(load_sample_set)(client, sample) for sample in samples)
  end_time = time.time()
  print(f"Setup done: {end_time - start_time} s")
  
  