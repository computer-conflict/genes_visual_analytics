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
  #gen_expresions = df.loc[:, samples]
  #fit = umap.UMAP()
  #gen_expresions_u = fit.fit_transform(gen_expresions)
  
  
  #model = SentenceTransformer('all-MiniLM-L6-v2')
  #summaries = df.loc[:, "summary"]
  #summaries_embeddings = model.encode(summaries)
  #summaries_u = fit.fit_transform(summaries_embeddings)
  print(df)
  
  #datos = {
  #  'indexes': np.arange(0,len(df)),
  #  'symbol': df.iloc[:, 0],
  #  'summary': df.iloc[:, 1],
  #  'summary_x': summaries_u[:, 0],
  #  'summary_y': summaries_u[:, 1],
  #  'samples_x': gen_expresions_u[:, 0],
  #  'samples_y': gen_expresions_u[:, 1] 
  #}  
  datos = {
    'indexes': np.arange(0,len(df)),
    'symbol': df.iloc[:, 0],
    'summary': df.iloc[:, 1],
    'samples_i': np.arange(0,len(samples)),
  }  
  for sample in samples:
    datos[sample] = df[sample]
  
  source = ColumnDataSource(datos)
  TOOLTIPS = """
    <div style="overflow: none; width: 300px">
      <strong>Nombre</strong>
      <p>@{symbol}</p>
      <strong>Descripción</strong>
      <p>@{summary}</p>
    </div>
  """

  f1 = figure(width=300,height=300
			,tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select"
			,title='Descripciones',tooltips=TOOLTIPS)
  p1 = f1.circle(x='indexes', y='samples_i', source=source,radius=.02,line_width=0,line_alpha=0.5)
  #f1 = figure(width=300,height=300
	#		,tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select"
	#		,title='Descripciones',tooltips=TOOLTIPS)
  #p1 = f1.circle(x='summary_x', y='summary_y', source=source,radius=.02,line_width=0,line_alpha=0.5)
  #
  #f2 = figure(width=300,height=300,
  #    tools="crosshair,box_select,pan,reset,wheel_zoom"
  #    ,title='Expresiones de los genes', tooltips=TOOLTIPS)
  #p2 = f2.circle(x='samples_x', y='samples_y', source=source,radius=.02,line_width=0,line_alpha=0.5)
  
  
  #f3 = figure(width=300,height=300
	#	,tools="crosshair,box_select,pan,reset,wheel_zoom,lasso_select"
	#	,title='Genes y muestras',y_axis_label='Genes' ,x_axis_label='Samples'
  #  ,tooltips=TOOLTIPS)
  #
  #
  #for sample in samples:
  #  f3.circle(x=sample, y='indexes', source=source,radius=.02,line_width=0,line_alpha=0.5)
  #
  #hover = HoverTool()
  #hover.tooltips = [
  #    ('Nombre',"@{symbol}"),
  #    ('Descripción',"@{summary}")]
  #f1.tools.append(hover)
  #f2.tools.append(hover)

  div = Div(text=
      '''
      <h1>Selecciones enlazadas</h1>
      <h4>Manuel Arroyo García, 2023. Universidad de Oviedo</h4>
      <b>Uso de fuentes de datos (source)</b>
      <a href="fuentes/%s">(código fuente)</a>
    '''
  %(__file__.split('.')[0]+'_codigofuente.html'),width=700)

  lay = layout([
    [div],
    [f1]
	])


  show(lay)
  
  
create_data_set()