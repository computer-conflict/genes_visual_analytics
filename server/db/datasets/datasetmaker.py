# Scrapping document 
import requests, re, time, concurrent
import numpy as np
import pandas as pd

# Returns true if the name looks alike a gen name.
def gen_name_filter(name):
  lower_name = name.lower()
  return not ('Category' in lower_name or 'Wikipedia' in lower_name or 'List' in lower_name or 'human' in lower_name )

# Cleans up a text with dirty content such as <ref>, backslashes, etc... 
def clean_wikitext_plain_paragraph(text):
  cleaned_text = text
  # Trim key texts
  if re.search(re.compile(r'(==+)(.*?)\1'), text) != None:
    cleaned_text = re.sub(re.compile(r'(=+)(.*?)\1'), r'\2', cleaned_text)
  
  # -- Patterns that identifies labels and remove its content -- #
  remove_patterns = np.array([])
  
  # Labels pattern
  remove_patterns = np.append(remove_patterns, re.compile(r'<.*?>.*?</.*?>'))
  # Brackets pattern [[some text]]
  remove_patterns = np.append(remove_patterns, re.compile(r' \[\[.*?\]\]', re.DOTALL))
  remove_patterns = np.append(remove_patterns, re.compile(r'\[\[.*?\]\]', re.DOTALL))
  # Curly brackets {{ some text }} 
  remove_patterns = np.append(remove_patterns, re.compile(r'{{.*?}}', re.DOTALL))

  for pattern in remove_patterns:
    cleaned_text = re.sub(pattern, '', cleaned_text)

  
  # Patterns that only removes labels
  clean_patterns = np.array([])
  # Bold text
  clean_patterns = np.append(clean_patterns, re.compile(r'\'\'\'(.*?)\'\'\'', re.DOTALL))

  for pattern in clean_patterns:
    cleaned_text = re.sub(pattern, r'\1', cleaned_text)
    
  # White spaces
  cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
  
  return cleaned_text
  
def parse_wikitext(wikitext):
  gen_data = {'Summary': ''}
  non_empty_text = list(filter(lambda e: len(e) > 0, wikitext.split("\n")))
  
  key = 'Summary'
  value = ''
  for row in non_empty_text:    
    if row[0] == '{' and non_empty_text[0][1] == '{':
      continue
    
    if re.search(re.compile(r'(==+)(.*?)\1'), row) != None:
      gen_data[key] = clean_wikitext_plain_paragraph(value)
      key = clean_wikitext_plain_paragraph(row)
      value = ''
    else:
      value += ' '+ row
  gen_data[key] = clean_wikitext_plain_paragraph(value)
  
  relevant_key = 'Summary'
  relevant_sections = ['Summary', 'Function', 'Clinical significance', 'Clinical relevance' 'Interactions', 'Role']
  for key in gen_data.keys():
    if (len(gen_data[key]) >= len(gen_data[key])) and any(key.lower() in section.lower() for section in relevant_sections):
      relevant_key = key
  
  return gen_data[relevant_key]

def get_gen_description(gen):
  description = 'KO'
  url = "https://en.wikipedia.org/w/api.php?action=parse&formatversion=2&page={}&prop=wikitext&format=json".format(gen)
  try:
    response = requests.get(url)
    if response.status_code == 200:
      try:
        wikitext = response.json()['parse']['wikitext']
      except Exception:
        return description
      # Check if gen is redirect and if so call again 
      if '#REDIRECT' in wikitext:
        new_gen = wikitext.split('[[')[1].split(']]')[0]
        if new_gen == 'ATPase, Na+/K+ transporting, alpha 1':
          new_gen = 'ATPase,_Na%2B/K%2B_transporting,_alpha_1'
        url = "https://en.wikipedia.org/w/api.php?action=parse&formatversion=2&page={}&prop=wikitext&format=json".format(new_gen)
        try:
          response = requests.get(url)
          if response.status_code != 200:
            return description
          try:
            wikitext = response.json()['parse']['wikitext']
          except Exception:
            return description
        except Exception:
          return description
    description = parse_wikitext(wikitext)      
  except Exception:
    return description
    
  return description

def process_gen(gen):
    gen_info = get_gen_description(gen)
    return [gen, gen_info]

# MAIN function get gene list and search for descriptions
def get_protein_coding_list():
  start = time.time()
  dataset = np.array([["symbol", "summary"]])
  
  protein_codin_genes = list()
  for i in range(4):
    url = "https://en.wikipedia.org/w/api.php?action=parse&format=json&page=List_of_human_protein-coding_genes_{}&formatversion=2".format(i+1)
    response = requests.get(url)
    if response.status_code == 200:
      # Si existe dame el nombre del gen
      # Hay que quitar las palabras vacias
      gen = list(map(lambda e: e['title'], list(filter(lambda e: e['exists'] and gen_name_filter(e['title']), response.json()['parse']['links']))))
      protein_codin_genes += gen
      
  with concurrent.futures.ThreadPoolExecutor(300) as executor:
    dataset = np.vstack((dataset, list(executor.map(process_gen, protein_codin_genes))))

  df = pd.DataFrame(dataset[1:], columns=dataset[0])
  df.to_csv('custom_dataset.csv', index=False)
  end = time.time()
  print(end - start)
  return dataset