"""
ITD104 Assignment 2 - Movie Data Explorer
Najim Uddin Nayeem | n12574031
"""

import tkinter as tk
from tkinter import ttk, messagebox

DATA_URL  = ("https://gist.githubusercontent.com/tiangechen/b68782efa49a16edaf07dc2cdaa855ea"
             "/raw/0c597858daad80b2de834ec5c26a6e5a438a3db/movies.csv")
DATA_FILE   = "movies.csv"
BANNER_FILE = "banner.png"
COLUMNS     = ("Film", "Genre", "Lead Studio", "Audience score %", "Rotten Tomatoes %", "Year")



def load_movies(path):
    """Read CSV and return a list of movie dictionaries."""
    movies = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
   
            clean = {k.strip(): v.strip() for k, v in row.items()}
            if not clean.get("Film"):
                continue  
          
            for col in ("Audience score %", "Rotten Tomatoes %", "Year"):
                if not clean.get(col):
                    clean[col] = "0"
            movies.append(clean)
    return movies
