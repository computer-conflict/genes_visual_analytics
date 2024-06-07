# Solves: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb


# Umap
import umap.umap_ as umap
from sentence_transformers import SentenceTransformer

# Clustering
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from bokeh.palettes import Spectral11,Turbo256

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
clustering = DBSCAN(eps=5.0, min_samples=9)


# -- Functions -- //
def get_umap_dimensions(embeddings):
    print(" - UMAP time:")
    start_time = time.time()
    summaries_2dimensions = umap.fit_transform(embeddings)
    x_list = summaries_2dimensions[:, 0]
    y_list = summaries_2dimensions[:, 1]
    print(f"    {time.time() - start_time} s")
    return [x_list, y_list]

from sklearn.metrics import silhouette_score
def get_collection_clusters(embeddings):  
    print(f" - Clustering time:")
    start_time = time.time()
    scaled_embeddings = StandardScaler().fit_transform(embeddings)
    result = clustering.fit(scaled_embeddings)
    print(f"    {time.time() - start_time} s")
    
    #eps_values = np.linspace(0.5, 5.0, 20)  # Puedes ajustar este rango según sea necesario
    #min_samples_values = range(5, 20)  # Puedes ajustar este rango según sea necesario
#
    #best_score = -1
    #best_params = None
    #best_labels = None
#
    #for eps in eps_values:
    #    for min_samples in min_samples_values:
    #        db = DBSCAN(eps=eps, min_samples=min_samples).fit(embeddings)
    #        labels = db.labels_
    #        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    #        if 1 < n_clusters <= 10:  # Buscamos entre 2 y 10 clusters
    #            score = silhouette_score(embeddings, labels)
    #            if score > best_score:
    #                best_score = score
    #                best_params = (eps, min_samples)
    #                best_labels = labels
#
    #if best_params is not None:
    #    print(f'Mejor puntaje de silhouette: {best_score}')
    #    print(f'Mejores parámetros: eps={best_params[0]}, min_samples={best_params[1]}')
    #else:
    #    print('No se encontraron parámetros que produzcan menos de 10 clusters.')

    return result.labels_






def get_collection_colors(labels):
    colors = Spectral11[0:len(labels)] if len(labels) < 11 else Turbo256[0:len(labels)]
    
    return [colors[label] if label != -1 else 'rgba(128, 128, 128, 0.8)' for label in labels]

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
    labels = get_collection_clusters(embeddings)
    df['cluster'] = labels
    df['color'] = get_collection_colors(labels)

    print(f"Dump {collection_name} into Chroma.")
    start_time = time.time()
    collection = client.get_or_create_collection(collection_name)
    collection.add(
      ids=list(df["symbol"]),
      documents= list(df["summary"]),
      metadatas= df[['symbol', 'summary', 'x', 'y', 'cluster', 'color']].to_dict(orient='records'))
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
    
    labels = get_collection_clusters(gene_expressions)
    df['cluster'] = labels
    df['color'] = get_collection_colors(labels)
    df['x'], df['y'] = get_umap_dimensions(gene_expressions)  
    
    df.to_csv(f"./db/datasets/modified_datasets/{dataset}.csv", index=False)  

def get_tcga_datasets():
    with open("./db/tcga_datasets_index.json") as tcgaFile:
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
  
  