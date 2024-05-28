import requests, gzip, shutil, os, json

class bcolors:
    OK = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def download_and_unzip_dataset(dataset_name, url):
    zips_folder = "./db/datasets/zipped_expressions_sets/"
    os.makedirs(zips_folder, exist_ok=True)
    dest_folder = "./db/datasets/raw_datasets/"
    os.makedirs(dest_folder, exist_ok=True)
    
    try:        
        r = requests.get(url, stream=True)
    
        if r.ok:
            compressed_file_path = f"{zips_folder}{dataset_name}.gz"
            with open(compressed_file_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            decompressed_file_path = f"{dest_folder}{dataset_name}"
            with gzip.open(compressed_file_path, 'rb') as f_in:
                with open(decompressed_file_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            os.remove(compressed_file_path)

            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        False

        
    
def get_tcga_datasets():
  with open("./db/tcga_datasets_index.json") as tcgaFile:
    data = json.load(tcgaFile)
  return data

def load_genes_expressions_datasets():
    tcga_datatasets = get_tcga_datasets()
    datasets_count = len(tcga_datatasets)

    print("Downloading datasets...")
    for index, (name, url) in enumerate(tcga_datatasets.items()):
        if download_and_unzip_dataset(name, url):
            print(f"{index+1}/{datasets_count}:{bcolors.OK} {name} - OK{bcolors.ENDC}")
        else:            
            print(f"{index+1}/{datasets_count}:{bcolors.FAIL} ERROR downloading: {name}{bcolors.ENDC}")
    
    if os.path.exists("./db/datasets/zipped_expressions_sets"):
        os.rmdir("./db/datasets/zipped_expressions_sets")
    
if __name__ == "__main__":
    load_genes_expressions_datasets()