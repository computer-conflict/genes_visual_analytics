# Imports for Chromadb
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb

# Bokeh imports
from bokeh.layouts import column
from bokeh.models import Button, ColumnDataSource, Div, Select, TextInput, Toggle

# Utils imports
import numpy as np
from typing import List
from .data_helper import DataHelper

from gpt4all import GPT4All

class WidgetsHelper:
    @staticmethod
    def summarize_selection(source) -> str:
        indices = source.selected.indices
        genes_descriptions = ('. ').join(map(str, np.take(source.data['summary'], indices).tolist()))

        def chunk_text(text, max_tokens):
            # Esta función divide el texto en fragmentos de tamaño máximo max_tokens
            words = text.split()
            chunks = []
            current_chunk = []
            current_length = 0

            for word in words:
                if current_length + len(word) + 1 > max_tokens:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word) + 1
                else:
                    current_chunk.append(word)
                    current_length += len(word) + 1

            if current_chunk:
                chunks.append(" ".join(current_chunk))
            return chunks

        model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
        max_tokens_per_chunk = 2048  # Ajusta esto según sea necesario

        genes_descriptions_chunks = chunk_text(genes_descriptions, max_tokens_per_chunk)
        responses = []

        with model.chat_session():
            for chunk in genes_descriptions_chunks:
                response = model.generate(prompt=f"Can you say what functions share these gene summaries: {chunk}", temp=0)
                responses.append(response)

        # Combina las respuestas
        combined_response = " ".join(responses)
        return f'\
            <h2>Descripciones resumidas</h2> \
            <p>{combined_response}</p>'
        #summary_div.text = f'\
        #    <h2>Descripciones resumidas</h2> \
        #    <p>{combined_response}</p>'

    @staticmethod
    def get_widgets(source: ColumnDataSource, set_1_name:str, set_2_name:str) -> List:
        select_options = ["ACC", "BLCA", "BRCA", "CESC", "CHOL", "COAD", "COADREAD", "DLBC",
                          "ESCA", "GBM", "HNSC", "KICH", "KIRC", "KIRP", "LAML", "LGG", "LIHC",
                          "LUAD", "LUNG", "LUSC", "MESO", "OV", "PAAD", "PCPG", "PRAD", "READ",
                          "SARC", "SKCM", "STAD", "TGCT", "THCA", "THYM", "UCEC", "UCS", "UVM"]


        def change_set_1(attr, old, new):
          set_2_name = select_2.value
          common_genes_list = DataHelper.get_common_genes_list(new, set_2_name)
          expresions_set_1_data = DataHelper.get_metadata_from_csv(common_genes_list, new)
          source.data['set_1_x'] = expresions_set_1_data['x']
          source.data['set_1_y'] = expresions_set_1_data['y']
          source.data['set_1_cluster'] = expresions_set_1_data['cluster'].astype(str).values
        select_1 = Select(title="Conjunto de datos a visualizar:",
                        value=set_1_name,
                        options=sorted(select_options),
                        sizing_mode="stretch_width", margin=[10, 0])
        select_1.on_change('value', change_set_1)
        select_1.styles = {'padding': '0 20px'}

        def change_set_2(attr, old, new):
          set_1_name = select_1.value
          common_genes_list = DataHelper.get_common_genes_list(new, set_1_name)
          expresions_set_2_data = DataHelper.get_metadata_from_csv(common_genes_list, new)
          source.data['set_2_x'] = expresions_set_2_data['x'].values
          source.data['set_2_y'] = expresions_set_2_data['y'].values
          source.data['set_2_cluster'] = expresions_set_2_data['cluster'].astype(str).values
        select_2 = Select(title="Conjunto de datos a visualizar:",
                        value=set_2_name,
                        options=sorted(select_options),
                        sizing_mode="stretch_width", margin=[10, 0])
        select_2.on_change('value', change_set_2)
        select_2.styles = {'padding': '0 20px'}


        sum_btn = Button(label="Resumir selección", sizing_mode="stretch_width", margin=[10, 0])
        sum_btn.disabled=True
        #sum_btn.on_click(summarize_selection)
        sum_btn.styles = {'margin-top': '20px'}

        brusshing_toggle = Toggle(label="Brushing", sizing_mode="stretch_width", margin=[10, 50])
        brusshing_toggle.styles = {'margin-top': '20px'}

        return [sum_btn, brusshing_toggle, select_1, select_2]

    @staticmethod
    def get_search_bar(source: ColumnDataSource) -> TextInput:
        def search_query(attr, old, new):
          client = chromadb.PersistentClient(path="./db/chromadb_client")
          collection = client.get_collection("gene_summaries")
          results = collection.query(
            query_texts=new,
            n_results=200)

          results['metadatas'][0][0]

          h1.text = '<h2>Genes seleccionados</h2>'
          results_widgets = []
          result_list.children = []
          for result in results['metadatas'][0]:
            result_group = column(sizing_mode="stretch_width")

            # Add results to Div (gene list view)
            header = Div(text=f"<h2>{result['symbol']}</h2>")
            header.styles = {'padding': '0 25px'}
            result_group.children.append(header)

            text = Div(text=f"<p>{result['summary']}</p>")
            text.styles = {'padding': '0 25px'}
            result_group.children.append(text)

            results_widgets.append(result_group)

          result_list.children = list(results_widgets)

          symbols = list(map(lambda r: r['symbol'], results['metadatas'][0]))
          indices = []
          for sym in symbols:
            try:
                indice = source.data['symbol'].index(sym)
                indices.append(indice)
            except ValueError:
                pass  # Ignorar símbolos que no están en source.data['symbol']
          source.selected.indices = indices

        search_bar = TextInput(title="Conjunto de datos a visualizar:",
                              placeholder='Introduce la descripción del gen...',
                              sizing_mode="stretch_width", margin=[10, 0])
        search_bar.on_change('value', search_query)
        search_bar.styles = {'padding': '0 25px'}

        # Search results display
        h1 = Div(text="<h1></h1>")
        h1.styles = {'padding': '0 25px'}
        result_list = column(sizing_mode="stretch_width")

        return [search_bar, h1, result_list]

