# fuelvariationscraping
Scrapes the fuel variation page and extracts the variation value and tendency for the current week.

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
