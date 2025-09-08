## Test locally

Follow these steps:

1. Copy the method you want to test to `sensor_test.py`
2. Create you test method
3. Run `python3 -m venv pytmp` to create a temporary python environment
4. Run `source pytmp/bin/activate` to activate the temporary python environment
5. Run `pip install pytest beautifulsoup4` to install pytest
6. Run `pytest -v` to test the parser utility 
