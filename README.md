[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Purpose
Simulating how the Elo ranking system works in a simple Python interface 

## Install
pip install -r requirements.txt

## Usage
``` 
elo.py [-h] [--sleeptime SLEEPTIME] [--static] [-v] nb_players nb_games nb_placements min_skill delta_skill
```
Static example:
``` 
python elo.py 5 100 15 10 10 --sleeptime=5 --static
``` 
Dynamic example:
``` 
python elo.py 5 10000 15 10 10 --sleeptime=0.01
``` 
