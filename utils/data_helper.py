# Imports for Chromadb
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb

# Bokeh imports
from bokeh.models import ColumnDataSource

# Utils imports
import numpy as np
import pandas as pd

class DataHelper:
    @staticmethod
    def get_common_genes_list(df_name_1, df_name_2):
        desc_dataset_path = './db/datasets/raw_datasets/semantic_dataframe.csv'
        desc_df = pd.read_csv(desc_dataset_path, usecols=["symbol", "summary"]).dropna().drop_duplicates(subset=['symbol'])

        path = f"./db/datasets/raw_datasets/{df_name_1.split('_')[0]}"
        gene_exp_1_df = pd.read_table(path)

        path = f"./db/datasets/raw_datasets/{df_name_2.split('_')[0]}"
        gene_exp_2_df = pd.read_table(path)

        # Merge dataframes on inner gene name.
        # 'symbol' for descriptions, 'sample' for gene expressions
        df = pd.merge(desc_df, gene_exp_1_df, how='inner', left_on='symbol', right_on='sample')
        result_df = pd.merge(df, gene_exp_2_df, how='inner', left_on='symbol', right_on='sample')

        genes_list = list(result_df["symbol"])
        return genes_list
    
    @staticmethod
    def get_metadata_from_chroma(client, genes_list, collection_name):  
        collection = client.get_collection(collection_name)
        metadatas = collection.get(ids=genes_list, include=["metadatas"])["metadatas"]
        return sorted(metadatas, key=lambda row: row['symbol'])
    
    @staticmethod
    def get_metadata_from_csv(genes_list, df_name):
        file_path = f"./db/datasets/modified_datasets/{df_name.split('_')[0]}.csv"
        df = pd.read_csv(file_path)[['x', 'y', 'cluster', 'sample', 'color']]
        return df[df['sample'].isin(genes_list)].sort_values(by='sample')

  
    @staticmethod
    def create_datasource(set_1_name: str, set_2_name: str) -> ColumnDataSource:
        client = chromadb.PersistentClient(path="./db/chromadb_client")

        common_genes_list = DataHelper.get_common_genes_list(set_1_name, set_2_name) 
        summaries_metadatas = DataHelper.get_metadata_from_chroma(client, common_genes_list, 'gene_summaries')
        expresions_set_1_data = DataHelper.get_metadata_from_csv(common_genes_list, set_1_name)
        expresions_set_2_data = DataHelper.get_metadata_from_csv(common_genes_list, set_2_name)

        data = {
          'indexes': np.arange(0, len(common_genes_list)),
          'symbol': [d['symbol'] for d in summaries_metadatas],
          'summary': [d['summary'] for d in summaries_metadatas],
          'summary_x': [d['x'] for d in summaries_metadatas],
          'summary_y': [d['y'] for d in summaries_metadatas],
          'set_1_x':        list(expresions_set_1_data['x']),
          'set_1_y':        list(expresions_set_1_data['y']),
          'set_1_cluster':  list(expresions_set_1_data['cluster'].astype(str)),
          'set_1_color':    list(expresions_set_1_data['color']),
          'set_2_x':        list(expresions_set_2_data['x']),
          'set_2_y':        list(expresions_set_2_data['y']),
          'set_2_cluster':  list(expresions_set_2_data['cluster'].astype(str)),
          'set_2_color':    list(expresions_set_2_data['color'])          
        }

        return ColumnDataSource(data)

