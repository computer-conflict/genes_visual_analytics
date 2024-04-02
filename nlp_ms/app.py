from flask import Flask, request

import torch
from transformers import pipeline

app = Flask(__name__)

#https://huggingface.co/allenai/led-base-16384
#https://huggingface.co/pszemraj/led-base-book-summary?text=large+earthquakes+along+a+given+fault+segment+do+not+occur+at+random+intervals+because+it+takes+time+to+accumulate+the+strain+energy+for+the+rupture.+The+rates+at+which+tectonic+plates+move+and+accumulate+strain+at+their+boundaries+are+approximately+uniform.+Therefore%2C+in+first+approximation%2C+one+may+expect+that+large+ruptures+of+the+same+fault+segment+will+occur+at+approximately+constant+time+intervals.+If+subsequent+main+shocks+have+different+amounts+of+slip+across+the+fault%2C+then+the+recurrence+time+may+vary%2C+and+the+basic+idea+of+periodic+mainshocks+must+be+modified.+For+great+plate+boundary+ruptures+the+length+and+slip+often+vary+by+a+factor+of+2.+Along+the+southern+segment+of+the+San+Andreas+fault+the+recurrence+interval+is+145+years+with+variations+of+several+decades.+The+smaller+the+standard+deviation+of+the+average+recurrence+interval%2C+the+more+specific+could+be+the+long+term+prediction+of+a+future+mainshock.

@app.route("/summarize_large", methods=['POST', 'GET'])
def summarize():
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

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
  
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
