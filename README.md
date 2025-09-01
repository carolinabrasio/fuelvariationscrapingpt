# fuel-variation-scraping
Scrapes the fuel variation page and extracts the variation value and tendency

## Install in HA

Follow these steps:

1. Go to `File editor` in you HA
2. Navigate to the `custom_components/` folder
3. Create a folder with name `fuel-variation-scraping`
4. Copy all the files inside `./custom_compoments/fuel_variation_scraping/` to the recently created folder
5. Restart HA

## Test locally

Follow these steps:

1. Run `python3 -m venv pytmp` to create a temporary python environment
2. Run `source pytmp/bin/activate` to activate the temporary python environment
3. Run `pip install pytest` to install pytest
4. Run `pytest -v` to test the parser utility 
