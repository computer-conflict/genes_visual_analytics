import requests
import gzip
import shutil
        
def download_and_unzip_dataset(name, url):  
  response = requests.get(url, stream=True)
  
  if response.status_code == 200:
    with open(f"{name}.gz", 'wb') as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)
    
    # Descomprimir el archivo gz
    with gzip.open(f"{name}.gz", 'rb') as f_in:
      with open(f"./zipped_impressions_sets/{name}", 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    
    print(f"Dataset {name} añadido correctamente.")
  else:
    print("[ERROR] No se ha podido descargar el dataset {name}.")
    
def download_datasets():
  tcga_datatasets = {
    "LAML": 'https://tcga-xena-hub.s3.us-east-1.amazonaws.com/download/TCGA.LAML.sampleMap%2FHiSeqV2_PANCAN.gz'
  }
  
  for name, url in tcga_datatasets.items():
    download_and_unzip_dataset(name, url)

if __name__ == "__main__":
  download_datasets()