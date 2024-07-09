import requests, gzip, shutil, os, json, time
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

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
  with open("./db/tcga_datasets_index_test.json") as tcgaFile:
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

def get_gen_summary(gene_name):
    try:
        search_url = f"https://www.ncbi.nlm.nih.gov/gene/?term={gene_name}"
        response = requests.get(search_url)

        soup = BeautifulSoup(response.text, 'html.parser')

        gene_link = None
        for a_tag in soup.find_all('a', href=True, ref=True):
            ref = a_tag['ref']
            if 'ordinalpos=1' in ref and 'link_uid=' in ref:
                gene_link = a_tag
                break

        if not gene_link:
            return gene_name, ""

        gene_page_url = 'https://www.ncbi.nlm.nih.gov' + gene_link['href']

        response = requests.get(gene_page_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        summary_text = None
        for dt in soup.find_all('dt'):
            if dt.get_text(strip=True) == "Summary":
                dd = dt.find_next('dd')
                if dd:
                    summary_text = dd.get_text(strip=True)
                break

        if not summary_text:
            return gene_name, ""

        return gene_name, summary_text
    except requests.exceptions.RequestException:
        return gene_name, ""

def load_genes_summaries_dataset():
    file_path = 'db/datasets/raw_datasets/UCS'
    output_path = 'db/datasets/raw_datasets/genes_summary_script.csv'

    df = pd.read_table(file_path)
    results = []
    total_genes = len(df)
    genes_without_summary = 0

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=70) as executor:
        future_to_gene = {executor.submit(get_gen_summary, gene_name): gene_name for gene_name in df['sample']}

        for idx, future in enumerate(as_completed(future_to_gene), 1):
            gene_name, summary = future.result()
            if len(summary) == 0:
                genes_without_summary += 1
            results.append({'symbol': gene_name, 'summary': summary})
            print(f"{idx}/{total_genes} (Sin resumen: {genes_without_summary}) Procesando gen: {gene_name}")

    end_time = time.time()
    total_time = end_time - start_time

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    print("\n--- Resumen del conjunto de datos semantico ---")
    print(f"Genes procesados: {total_genes}")
    print(f"Genes sin resumen: {genes_without_summary}")
    print(f"Tiempo total: {total_time:.2f} segundos")

if __name__ == "__main__":
    #load_genes_expressions_datasets()

    file_path = 'db/datasets/raw_datasets/semantic_dataframe.csv'
    if not os.path.exists(file_path):
        load_genes_summaries_dataset()