# automated-BEMTOOL-configurator
A Streamlit + Docker application for generating configuration files used in the BEMTOOL bio-economic fisheries model.  
The app simplifies the creation of complex `.csv` input files by guiding users through parameter selection, species–fleet relationships, and biological inputs.

---

## Features
- Interactive Streamlit interface for parameter entry  
- Automated validation of uploaded species & fleet files  
- Dynamic creation of configuration matrix (`pandas`-based)  
- Containerized for portable deployment via **Docker**

---

## Usage

### Run locally
pip install -r requirements.txt

streamlit run config_file.py

### Run with Docker
docker build -t docker-bmt .

docker run -p 8501:8501 docker-bmt

Then open http://localhost:8501 in your browser.
