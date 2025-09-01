# fuelvariationscraping
Scrapes the fuel variation page and extracts the variation value and tendency

## Install in HA

Follow these steps:

1. Go to `File editor` in you HA
2. Navigate to the `homeassistant/custom_components/` folder
3. Create a folder with name `fuelvariationscraping`
4. Copy all the files inside `./custom_compoments/fuel_variation_scraping/` to the recently created folder
5. Add to the `homeassistant/configuration.yaml`:
  ```
  sensor:
    - platform: fuelvariationscraping
  ```
6. Restart HA

## Test locally

Follow these steps:

1. Copy the method you want to test to `sensor_test.py`
2. Create you test method
3. Run `python3 -m venv pytmp` to create a temporary python environment
4. Run `source pytmp/bin/activate` to activate the temporary python environment
5. Run `pip install pytest beautifulsoup4` to install pytest
6. Run `pytest -v` to test the parser utility 
