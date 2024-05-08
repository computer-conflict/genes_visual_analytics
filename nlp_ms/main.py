from flask import Flask, request

import torch
from transformers import pipeline
from nlpcloud import Client

app = Flask(__name__)

#https://huggingface.co/allenai/led-base-16384
#https://huggingface.co/pszemraj/led-base-book-summary?text=large+earthquakes+along+a+given+fault+segment+do+not+occur+at+random+intervals+because+it+takes+time+to+accumulate+the+strain+energy+for+the+rupture.+The+rates+at+which+tectonic+plates+move+and+accumulate+strain+at+their+boundaries+are+approximately+uniform.+Therefore%2C+in+first+approximation%2C+one+may+expect+that+large+ruptures+of+the+same+fault+segment+will+occur+at+approximately+constant+time+intervals.+If+subsequent+main+shocks+have+different+amounts+of+slip+across+the+fault%2C+then+the+recurrence+time+may+vary%2C+and+the+basic+idea+of+periodic+mainshocks+must+be+modified.+For+great+plate+boundary+ruptures+the+length+and+slip+often+vary+by+a+factor+of+2.+Along+the+southern+segment+of+the+San+Andreas+fault+the+recurrence+interval+is+145+years+with+variations+of+several+decades.+The+smaller+the+standard+deviation+of+the+average+recurrence+interval%2C+the+more+specific+could+be+the+long+term+prediction+of+a+future+mainshock.

@app.route("/summarize_led", methods=['POST', 'GET'])
def summarize_large():
  #summarizer = pipeline("summarization", model="philschmid/bart-large-cnn-samsum")

  summarizer = pipeline(
      "summarization",
      "pszemraj/led-base-book-summary",
      device=0 if torch.cuda.is_available() else -1,
  )

  response = 'Descriptions cannot be summarized'
  if request.method == 'POST':
    gene_summaries = request.form['summary_text']
    result = summarizer(
      gene_summaries,
      min_length=8,
      max_length=256,
      no_repeat_ngram_size=3,
      encoder_no_repeat_ngram_size=3,
      repetition_penalty=3.5,
      num_beams=4,
      do_sample=False,
      early_stopping=True,
    )
    response = result[0]["summary_text"]
    #response = summarizer(ARTICLE, max_length=130, min_length=30, do_sample=False)
    
  print(response)
  return response

@app.route("/summarize_bart", methods=['POST', 'GET'])
def summarize_batch():
  response = 'Descriptions cannot be summarized'
  
  try:
    summarizer = pipeline("summarization", "facebook/bart-large-cnn")
    
    if request.method == 'POST':
      resumenes = request.form['summary_text']
      
      def summarize_article(articles):
        full_article = ''.join(articles)
        if(len(full_article) < 1024):
          return summarizer(full_article, max_length=130, min_length=30, do_sample=False)
        
        mid_list_len = len(articles)
        left_summarization = summarize_article(articles[:mid_list_len])[0]["summary_text"]
        right_summarization = summarize_article(articles[mid_list_len:])[0]["summary_text"]
        return summarize_article([left_summarization, right_summarization])
        
      result = summarize_article(gene_summaries)
      response = result[0]["summary_text"]
      
  finally:    
    return response

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]
        
def summarize_text(text, summarizer):
    summary = summarizer(f"{text}", max_new_tokens=700, num_return_sequences=1)
    print("Chunk resumido\n")
    print(summary)
    print("           '    ")
    print("         o      ")
    print("       0        ")
    print("        o       ")
    print("        .       ")
    print("_-_-_----_---_--")

    return summary


@app.route("/summarize_gpt", methods=['POST', 'GET'])
def summarize_gpt():
  # Cargar el tokenizador y el modelo GPT-2
  summarizer = pipeline("summarization")

  request_summary = ''
  if request.method == 'POST':
    gene_summaries = request.form['summary_text'].split('. ')
    max_tokens_per_chunk = 500
    
    # Dividir los resumenes en trozos procesables
    chunks = list(chunk_list(gene_summaries, max_tokens_per_chunk))
    
    summarized_chunks = []
    for chunk in chunks:
      # Procesamiento de cada trozo
      summarized_chunk = summarize_text(chunk, summarizer)
      summarized_chunks.append(summarized_chunk)
      
    # Concatenar los resúmenes en más conjuntos de tamaño máximo
    if len(summarized_chunks) > 1:
      combined_summary = ". ".join(summarized_chunks)
      combined_chunks = list(chunk_list(combined_summary, max_tokens_per_chunk))
      request_summary = summarize_text(combined_chunks)
    else:
      request_summary = ". ".join(summarized_chunks)
      
  return request_summary

@app.route("/ask_gpt", methods=['POST'])
def ask_gpt():
  # Cargar el tokenizador y el modelo GPT-2
  model = pipeline('text-generation', model='gpt2')
  
  question = request.form['question']
  
  answer = model(f"{question}", num_return_sequences=5)
      
  return answer


@app.route("/summarize", methods=['POST'])
def summarize():
  descriptions = request.form['gen_descriptions']
  print(descriptions)
  
  client = Client("bart-large-cnn ", "578651d6ebe92ce54c5e611856fd409a920d27cc", gpu=True, asynchronous=True)
  summary = client.summarization(descriptions)
      
  return summary['summary_text']


@app.route("/ping")
def hello_world():
    return "pong"
  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
