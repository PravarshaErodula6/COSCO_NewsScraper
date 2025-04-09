#!/bin/bash

source /Users/pravarshaerodula/myenv/bin/activate
cd /Users/pravarshaerodula/Desktop/COSCO
/Users/pravarshaerodula/myenv/bin/papermill Untitled-2.ipynb output_scraper.ipynb --cwd /Users/pravarshaerodula/Desktop/COSCO --log-output --request-save-on-cell-execute || true
