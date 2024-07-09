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
from sklearn.manifold import TSNE
from bokeh.palettes import Spectral4,Turbo256

# Utils imports
import pandas as pd
import time, json, os
import pandas as pd
import numpy as np

# ------------------------------------------- #
#      Initialize enviroment variables        #
# ------------------------------------------- #
client = chromadb.PersistentClient(path="./db/chromadb_client")
umap_minkowski = umap.UMAP(metric='minkowski', metric_kwds={'p': 3})
umap_cosine = umap.UMAP(metric='cosine')
tsne = TSNE(n_components=2, perplexity=50, learning_rate=200, n_iter=1000, metric='minkowski')
semtanic_clustering = DBSCAN(eps=15.0, min_samples=75)
expressions_clustering = DBSCAN(eps=5.0, min_samples=9)


# -- Functions -- //
def get_umap_dimensions(embeddings, reduction_model):
    print(" - UMAP time:")
    start_time = time.time()
    summaries_2dimensions = reduction_model.fit_transform(embeddings)
    x_list = summaries_2dimensions[:, 0]
    y_list = summaries_2dimensions[:, 1]
    print(f"    {time.time() - start_time} s")
    return [x_list, y_list]


def get_tsne_dimensions(embeddings):
    print(" - t-SNE time:")
    start_time = time.time()
    summaries_2dimensions = tsne.fit_transform(embeddings)
    x_list = summaries_2dimensions[:, 0]
    y_list = summaries_2dimensions[:, 1]
    print(f"    {time.time() - start_time} s")
    return [x_list, y_list]

from sklearn.metrics import silhouette_score
def get_collection_clusters(embeddings, configured_model):
    print(f" - Clustering time:")
    start_time = time.time()
    scaled_embeddings = StandardScaler().fit_transform(embeddings)
    result = configured_model.fit(scaled_embeddings)
    print(f"    {time.time() - start_time} s")
    return result.labels_


def get_collection_colors(labels):
    colors = Spectral4[0:len(labels)] if len(labels) < 11 else Turbo256[0:len(labels)]

    return [colors[label] if label != -1 else 'rgb(102, 194, 165, 0.8)' for label in labels]

def transform_summaries_to_embeddings(summaries):
    transformer = SentenceTransformer("all-MiniLM-L6-v2")
    return transformer.encode(summaries)

def create_summary_collection(dataset):
    dataset_path = f"./db/datasets/raw_datasets/semantic_dataframe.csv"
    df = pd.read_csv(dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])

    # SentenceTransformer
    gene_summaries = df['summary'].tolist()
    embeddings = transform_summaries_to_embeddings(gene_summaries)

    df['x'], df['y'] = get_umap_dimensions(embeddings, umap_cosine)
    labels = get_collection_clusters(embeddings, semtanic_clustering)
    df['cluster'] = labels
    df['color'] = get_collection_colors(labels)

    print(f"Dump {dataset} into Chroma.")
    start_time = time.time()
    collection = client.get_or_create_collection(dataset)
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

    labels = get_collection_clusters(gene_expressions, expressions_clustering)
    df['cluster'] = labels
    df['color'] = get_collection_colors(labels)
    df['x'], df['y'] = get_umap_dimensions(gene_expressions, umap_minkowski)

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

