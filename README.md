# Visual Analytics for Gene Information
This project is a Proof of Concept (POC) aimed at demonstrating that clusters in the semantic space are related to clusters in the genes expressions space.

## Configuration
### Basic requierements
In order to prepare the environment and launch the prototype, you need to fulfill the following requirements:

- Venv
- Python3.11
- Pip~=24.0
- ~4GB Free disk space (for datasets)

### Enviroment setup

First, we need to create the environment and install all Pip requirements. The following commands must be executed in the root of the project.

```
python3.11 -m venv .venv

source .venv/bin/activate
```
Once the Python environment is created and activated, it is time to install the necessary libraries to run the application.

`pip install -r requirements.txt`

> **_NOTE:_** Macos users should run
 `pip install -r requirements_macos.txt`


Once all the packages are installed, it's time to download the datasets.

`python ./db/datasets/datasets_downloader.py`

"This command will download all the gene expression datasets from [xenabrowser](https://xenabrowser.net), unzip them, and save them into ./db/datasets/raw_datasets.

## Deployment

To deploy the app just run:

`python main.py`

The application will check the integrity of the data and serve the application at [localhost:8000](http://127.0.0.1:8000) 


