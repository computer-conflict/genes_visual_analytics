from flask import request, jsonify, abort
from db.handler import exec_query, exec_plotter
from api import app


from bokeh.embed import json_item
import json

# Definir rutas
@app.route('/')
def home():
  return '¡Bienvenido a mi API sin modelos!'

@app.route('/search')
def search():
  query_text = request.args.get('query_text','')
  #n_results = request.args.get('n_results',5)
  
  query = {
    "query_texts": query_text,
    "n_results": 5
  }
  
  return jsonify(exec_query(query))

@app.route('/plot')
def plotter():
  try:
    plot = exec_plotter()
    return jsonify(json.dumps(json_item(plot, "plot")))
  except Exception as e:
    print(f"Error: {str(e)}")
    abort(500)