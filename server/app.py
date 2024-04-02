from db.setup import chroma_setup

from api import app

if __name__ == '__main__':
  chroma_setup()
  # Escuchar en el puerto 8000
  app.run(debug=True, port=8000)