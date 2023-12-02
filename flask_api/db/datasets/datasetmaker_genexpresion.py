# Scrapping document 
import requests, re, time, concurrent
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import umap.umap_ as umap

from bokeh.plotting import figure, output_file
from bokeh.io import show
from bokeh.models import Div, ColumnDataSource, HoverTool
from bokeh.layouts import row, column, layout

def create_data_set():
  filename = __file__.split('.')[0]+'.html'
  output_file(filename)

  
  desc_dataset_path = './db/datasets/genes_human_58347_used_in_sciPlex2_brief_info_by_mygene_package.csv'
  desc_df = pd.read_csv(desc_dataset_path, usecols=["symbol", "summary"]).dropna()
  
  gen_expresion_dataset_path = './db/datasets/HiSeqV2_PANCAN'
  gen_exp_df = pd.read_table(gen_expresion_dataset_path)

  # Base df
  df = pd.merge(desc_df, gen_exp_df, on='symbol')
  


  samples = df.columns[2:]
  gen_expresions = df.loc[:, samples]
  fit = umap.UMAP()
  gen_expresions_u = fit.fit_transform(gen_expresions)
  
  
  model = SentenceTransformer('all-MiniLM-L6-v2')
  summaries = df.loc[:, "summary"]
  summaries_embeddings = model.encode(summaries)
  summaries_u = fit.fit_transform(summaries_embeddings)
  print(df)
  
  datos = {
    'indexes': np.arange(0,len(df)),
    'symbol': df.iloc[:, 0],
    'summary': df.iloc[:, 1],
    'summary_x': summaries_u[:, 0],
    'summary_y': summaries_u[:, 1],
    'samples_x': gen_expresions_u[:, 0],
    'samples_y': gen_expresions_u[:, 1] 
  }  
  for sample in samples:
    datos[sample] = df[sample]
  
  source = ColumnDataSource(datos)
  TOOLTIPS = """
    <div style="overflow: scroll;">
      <strong>Nombre</strong>
      <p>@{symbol}</p>
      <strong>Descripción</strong>
      <p>@{summary}</p>
    </div>
  """

  f1 = figure(width=300,height=300
			,tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select"
			,title='Descripciones',tooltips=TOOLTIPS)
  p1 = f1.circle(x='summary_x', y='summary_y', source=source,radius=.02,line_width=0,line_alpha=0.5)
  
  f2 = figure(width=300,height=300,
      tools="crosshair,box_select,pan,reset,wheel_zoom"
      ,title='Expresiones de los genes', tooltips=TOOLTIPS)
  p2 = f2.circle(x='samples_x', y='samples_y', source=source,radius=.02,line_width=0,line_alpha=0.5)
  
  
  f3 = figure(width=300,height=300
		,tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select"
		,title='Genes y muestras',y_axis_label='Genes' ,x_axis_label='Samples'
    ,tooltips=TOOLTIPS)
  
  
  for sample in samples:
    f3.circle(x=sample, y='indexes', source=source,radius=.02,line_width=0,line_alpha=0.5)
  #
  #hover = HoverTool()
  #hover.tooltips = [
  #    ('Nombre',"@{symbol}"),
  #    ('Descripción',"@{summary}")]
  #f1.tools.append(hover)
  #f2.tools.append(hover)

  div = Div(text='''
  <h1>Ejemplo básico de plot → variante "dataicann"</h1>
  <h4>Ignacio Díaz Blanco, 2021. Universidad de Oviedo</h4>
  <b>Uso de fuentes de datos (source)</b>
  <table>
  <td valign="top">
  <p>En este ejemplo, utilizamos una fuente de datos
  mediante el objeto <i>source</i>. El objeto <i>source</i> puede verse como una tabla 
  en este caso, tiene <i>N</i> muestras y atributos <i>'t', 'ax', 'ay','ir','is'</i>
  </p>
  <p>Este objeto es una "fuente de datos" común
  que "sincroniza" todas las figuras
  cualquier cambio en los datos (modificación, selección)
  es inmediatamente actualizado por Boheh en 
  todas las figuras que tengan esa fuente</p>
  </td>

  <td valign="top">
  <p>Prueba a seleccionar una parte en una de las figuras. 
  Verás que en el resto de las figuras quedan los elementos 
  seleccionados consistentemente. Esto se llama en interacción "linking"</p>	
  </td>
  </table>
  <a href="fuentes/%s">(código fuente)</a>'''%(__file__.split('.')[0]+'_codigofuente.html'),width=700)

  lay = layout([
    [div],
    [f1,f2, f3]
	])


  show(lay)
  
  
create_data_set()