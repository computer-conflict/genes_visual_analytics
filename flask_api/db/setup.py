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

  
def get_embeddings(print_time = False):  
  start_time = time.time()  
  client = chromadb.PersistentClient(path="./db/local_client")
  collection = client.get_collection("chromagens")
  embeddings = collection.get(include=['embeddings'])['embeddings']
  end_time = time.time()
  if(print_time):
    print(f"Embeddings time: {end_time - start_time} seconds")
  return embeddings

#Db setup
def chroma_setup():
  print("Fetching local client...")
  # Create db and make a new collection
  client = chromadb.PersistentClient(path="./db/local_client")
  
  try:
    collection = client.get_collection("chromagens")
  except:
    print("Preparing data...")
    collection = client.create_collection("chromagens")
    
    # Prepare DataFrame
    dataset_path = './db/datasets/genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv'
    df = pd.read_csv(dataset_path, usecols=["symbol", "summary"]).dropna()
    df_numpy = df.to_numpy()
    # Prepare documents
    documents = list(map(lambda x: x[1], df_numpy))
    metadatas = list(map(lambda x: {"source":"summary", "name": x[0]}, df_numpy))
    ids = list(map(lambda x: str(x), range(len(df_numpy)) ))

    print("Adding documents...")
    collection.add(
        documents= documents,
        ids=ids)    
    
  print("Setup done.")
  
  