# TEM-Dash
A Dash application to visualize time-domain electromagnetic (TEM) soudings modeled with UBC-GIF forward modeling software em1dtmfwd.

## Installation

1. Install Dash

```
pip install dash==0.27.0  # The core dash backend
pip install dash-html-components==0.12.0  # HTML components
pip install dash-core-components==0.28.0  # Supercharged components
```
2. Install Pandas, Numpy

```
pip install pandas
pip install numpy
```

3. Unzipped the data. Make sure the folder name is "MdlemAll".

## Running the application

1. Running the following command will start a local web server

```
python tem_dash_app.py
```
2. Go to your favorite browser and visit http://localhost:8050 to acces the application


