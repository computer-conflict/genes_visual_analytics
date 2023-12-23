# db/main.py
# Contains al the functions needed to operate the chromadb, from starting up
# and add collection data, to retrieve data and embeddings.
#import pandas as pd
import pandas as pd

# Solves: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb, time

import umap.umap_ as umap


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
  print(f"Done: {end_time - start_time} seconds")
  embeddings = collection.get(ids=list(df["symbol"]), include=['embeddings'])['embeddings']
  

  fit = umap.UMAP()
  print(f"Preparing {collection_name} dataframe.")
  start_time = time.time()
  summaries_u = fit.fit_transform(embeddings)
  end_time = time.time()
  print(f"Done in: {end_time - start_time} seconds")

  df['x'] = summaries_u[:, 0]
  df['y'] = summaries_u[:, 1]

  print(f"Updating {collection_name}.")
  start_time = time.time()
  collection.update(
    ids=list(df["symbol"]),
    metadatas= df[['symbol', 'summary', 'x', 'y']].to_dict(orient='records'))
  end_time = time.time()
  print(f"Done: {end_time - start_time} seconds")

def create_set_collection(client, collection_name, df_path):
  gen_expresion_dataset_path = f"./db/datasets/{df_path}"
  gen_exp_df = pd.read_table(gen_expresion_dataset_path).drop_duplicates()
  # Calc avg expression 
  gen_exp_df.set_index('symbol', inplace=True)
  mean = gen_exp_df.mean(axis=1)
  gen_exp_df = gen_exp_df.reset_index()
  gen_exp_df['avg_gen_impresion'] = list(mean.reset_index()[0])

  fit = umap.UMAP()
  samples = gen_exp_df.columns[1:]
  gen_expresions = gen_exp_df.loc[:, samples]
  print(f"Preparing {collection_name} dataframe.")
  start_time = time.time()
  gen_expresions_u = fit.fit_transform(gen_expresions)
  end_time = time.time()
  print(f"Done: {end_time - start_time} seconds")

  gen_exp_df['x'] = gen_expresions_u[:, 0]
  gen_exp_df['y'] = gen_expresions_u[:, 1]
  docs = list(map(lambda sym: f"{collection_name}-{sym}", list(gen_exp_df["symbol"])))

  print(f"Creating collection {collection_name}.")
  collection = client.create_collection(collection_name)
  collection.add(
      documents= docs,
      metadatas= gen_exp_df[['symbol', 'x', 'y', 'avg_gen_impresion']].to_dict(orient='records'),
      ids=list(gen_exp_df["symbol"]))
  end_time = time.time()
  print(f"Done: {end_time - start_time} seconds")
  
#Db setup
def chroma_setup():
  print("Fetching local client...")
  # Create db and make a new collection
  client = chromadb.PersistentClient(path="./db/local_client")
  
  datasets = {
    'gen_summaries': 'genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv',
    'SET-HiSeqV2_PANCAN': 'HiSeqV2_PANCAN',
  }

  for key, value in datasets.items():
    try:
      client.get_collection(key)
    except:
      if key == 'gen_summaries':
        create_summary_collection(client, key, value)
      else:
        create_set_collection(client, key, value)  
    
  print("Setup done.")
  
  