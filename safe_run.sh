#!/bin/bash

source /Users/pravarshaerodula/myenv/bin/activate
cd /Users/pravarshaerodula/Desktop/COSCO

# ✅ Run papermill and force exit code to 0 even if error happens
/Users/pravarshaerodula/myenv/bin/papermill Untitled-2.ipynb output_scraper.ipynb --cwd /Users/pravarshaerodula/Desktop/COSCO || echo "⚠️ Notebook had errors but execution continued"

