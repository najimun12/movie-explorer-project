"""
Najim Uddin Nayeem
ITD104 Assignment 2: Movie Data Explorer
"""
import csv
import re
import os
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk 

DATA_URL  = ("https://gist.githubusercontent.com/tiangechen/b68782efa49a16edaf07dc2cdaa855ea"
             "/raw/0c597858daad80b2de834ec5c26a6e5a438a3db/movies.csv")
DATA_FILE   = "movies.csv"
BANNER_FILE = "banner.png"
COLUMNS     = ("Film", "Genre", "Lead Studio", "Audience score %", "Rotten Tomatoes %", "Year")


# Colours 

BG      = "#f5f0e8"   
BG2     = "#ede8de"   
BG3     = "#e0d9ce"   
TEAL    = "#2a6b6b"   
TEAL2   = "#1d4e4e"   
AMBER   = "#b5813d"  
FG      = "#2a2018" 
FG2     = "#7a6e60"  
SEP     = "#c8c0b0" 
ROW_A   = "#faf7f2"  
ROW_B   = "#f0ebe0"  
ROW_SEL = "#d4ede8" 


# Data Functions

def download_file(path, url):
    """Download CSV only if it does not exist yet."""
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)


def load_movies(path):
    """Read CSV and return a list of movie dictionaries."""
    movies = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            
            clean = {k.strip(): v.strip() for k, v in row.items()}
            if not clean.get("Film"):
                continue   # skip rows with no title
            
            for col in ("Audience score %", "Rotten Tomatoes %", "Year"):
                if not clean.get(col):
                    clean[col] = "0"
            movies.append(clean)
    return movies


def get_genres(movies):
    """Return a sorted list of unique genres with 'All' at the front."""
    genres = sorted({m["Genre"] for m in movies if m.get("Genre")})
    return ["All"] + genres


def validate_search(term):
    """Use regex to check the search term is valid."""
    if not term:
        return True, ""
    if re.fullmatch(r"\d+", term):
        return False, "Search cannot be numbers only."
    if not re.fullmatch(r"[A-Za-z0-9 \-':.]+", term):
        return False, "Search contains invalid characters."
    return True, ""


def search_movies(movies, term):
    """Return movies whose title contains the search term (case-insensitive)."""
    if not term:
        return movies
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    return [m for m in movies if pattern.search(m.get("Film", ""))]


def filter_by_genre(movies, genre):
    """Return only movies matching the chosen genre."""
    if genre == "All":
        return movies
    return [m for m in movies if m.get("Genre") == genre]


def sort_movies(movies, column, ascending):
    """Sort movies by column. Numbers sort as floats, text sorts alphabetically."""
    number_cols = {"Audience score %", "Rotten Tomatoes %", "Year"}

    def get_value(movie):
        val = movie.get(column, "")
        if column in number_cols:
            try:
                return float(val)
            except ValueError:
                return 0.0
        return val.lower()

    return sorted(movies, key=get_value, reverse=not ascending)


# Main App

class MovieApp:
    def __init__(self, root, movies):
        self.root      = root
        self.all       = movies      
        self.shown     = movies[:]  
        self.ascending = True      
        self.banner_img = None       

        root.title("Movie Explorer App")
        root.geometry("1060x680")
        root.configure(bg=BG)
        root.minsize(800, 480)

        self.setup_style()
        self.build_header()
        self.build_controls()
        self.build_table()
        self.build_footer()
        self.show_movies(self.all)


    def setup_style(self):
        """Apply colours to the ttk Treeview table."""
        s = ttk.Style()
        s.theme_use("default")
        s.configure("App.Treeview",
            background=ROW_A, foreground=FG, fieldbackground=ROW_A,
            rowheight=26, font=("Helvetica", 10), borderwidth=0)
        s.configure("App.Treeview.Heading",
            background=BG2, foreground=TEAL,
            font=("Helvetica", 10, "bold"), relief="flat")
        s.map("App.Treeview",
            background=[("selected", ROW_SEL)],
            foreground=[("selected", TEAL2)])
        s.map("App.Treeview.Heading",
            background=[("active", BG3)])
        for direction in ("Vertical", "Horizontal"):
            s.configure(f"App.{direction}.TScrollbar",
                background=BG3, troughcolor=BG2,
                arrowcolor=TEAL, borderwidth=0)


    def build_header(self):
        """Top section: amber line + banner image + centred title."""
        header = tk.Frame(self.root, bg=BG2)
        header.pack(fill=tk.X)
        tk.Frame(header, bg=AMBER, height=3).pack(fill=tk.X)
        if os.path.exists(BANNER_FILE):
            try:
                img = Image.open(BANNER_FILE).resize((1060, 72), Image.LANCZOS)
                self.banner_img = ImageTk.PhotoImage(img)
                tk.Label(header, image=self.banner_img, bg=BG2, bd=0).pack(fill=tk.X)
            except Exception:
                pass

        # Centred title below the banner
        tk.Label(header,
                 text="Movie Explorer",
                 font=("Georgia", 18, "bold"),
                 bg=BG2, fg=TEAL).pack(pady=(8, 0))

        tk.Frame(header, bg=SEP, height=1).pack(fill=tk.X)


    def build_controls(self):
        """Controls bar: search, genre filter, sort options, reset button."""
        bar = tk.Frame(self.root, bg=BG3, pady=9, padx=16)
        bar.pack(fill=tk.X)

        lbl = {"bg": BG3, "fg": FG2, "font": ("Helvetica", 10)}

        # Search box
        tk.Label(bar, text="Search:", **lbl).grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        entry = tk.Entry(bar, textvariable=self.search_var, width=22,
                         font=("Helvetica", 10), bg="#ffffff", fg=FG,
                         insertbackground=AMBER, relief=tk.SOLID, bd=1)
        entry.grid(row=0, column=1, padx=(0, 5), ipady=3)
        entry.bind("<Return>", lambda e: self.on_search())

        self.make_button(bar, "Search", self.on_search, TEAL, "#fff").grid(
            row=0, column=2, padx=(0, 22), ipady=2)

        # Genre dropdown
        tk.Label(bar, text="Genre:", **lbl).grid(row=0, column=3, padx=(0, 5))
        self.genre_var = tk.StringVar(value="All")
        genre_box = ttk.Combobox(bar, textvariable=self.genre_var,
                                 values=get_genres(self.all),
                                 width=13, state="readonly",
                                 font=("Helvetica", 10))
        genre_box.grid(row=0, column=4, padx=(0, 22))
        genre_box.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        tk.Label(bar, text="Sort by:", **lbl).grid(row=0, column=5, padx=(0, 5))
        self.sort_col = tk.StringVar(value="Film")
        sort_box = ttk.Combobox(bar, textvariable=self.sort_col,
                                values=list(COLUMNS), width=17,
                                state="readonly", font=("Helvetica", 10))
        sort_box.grid(row=0, column=6, padx=(0, 5))
        sort_box.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Ascending / Descending toggle
        self.dir_label = tk.StringVar(value="↑ Asc")
        self.make_button(bar, None, self.toggle_sort, BG2, TEAL,
                         tv=self.dir_label).grid(row=0, column=7, padx=(0, 22), ipady=2)

        # Reset button
        self.make_button(bar, "✕ Reset", self.reset_all, BG2, FG2).grid(
            row=0, column=8, ipady=2)

        tk.Frame(self.root, bg=SEP, height=1).pack(fill=tk.X)


    def make_button(self, parent, text, command, bg, fg, tv=None):
        """Create a flat styled button."""
        return tk.Button(parent,
                         text=text, textvariable=tv, command=command,
                         bg=bg, fg=fg,
                         activebackground=TEAL2, activeforeground="#fff",
                         relief=tk.FLAT, font=("Helvetica", 10, "bold"),
                         padx=10, cursor="hand2")


    def build_table(self):
        """Scrollable results table with clickable column headers."""
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True)

        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL,
                                  style="App.Vertical.TScrollbar")
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL,
                                  style="App.Horizontal.TScrollbar")

        self.tree = ttk.Treeview(frame, columns=COLUMNS, show="headings",
                                  yscrollcommand=v_scroll.set,
                                  xscrollcommand=h_scroll.set,
                                  selectmode="browse", style="App.Treeview")
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        # Make the table fill all available space
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Set column widths and attach sort-on-click
        widths = (255, 105, 165, 125, 140, 60)
        for col, w in zip(COLUMNS, widths):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=w, anchor=tk.CENTER, minwidth=45)

        self.tree.tag_configure("even", background=ROW_A)
        self.tree.tag_configure("odd",  background=ROW_B)
        self.tree.bind("<Double-1>", self.show_detail)


    def build_footer(self):
        """Footer bar showing only the student name — centred and bold."""
        tk.Frame(self.root, bg=AMBER, height=2).pack(fill=tk.X)

        footer = tk.Frame(self.root, bg=BG2, pady=8)
        footer.pack(fill=tk.X)

        tk.Label(footer,
                 text="© Najim Uddin Nayeem ID: n12574031",
                 font=("Helvetica", 11, "bold"),
                 bg=BG2, fg=TEAL).pack()


    # Event handlers 
    def on_search(self):
        ok, msg = validate_search(self.search_var.get().strip())
        if not ok:
            messagebox.showwarning("Invalid Search", msg)
            return
        self.refresh()

    def toggle_sort(self):
        self.ascending = not self.ascending
        self.dir_label.set("↑ Asc" if self.ascending else "↓ Desc")
        self.refresh()

    def sort_by_column(self, col):
        """Click column header to sort; click again to reverse."""
        if self.sort_col.get() == col:
            self.toggle_sort()
        else:
            self.sort_col.set(col)
            self.ascending = True
            self.dir_label.set("↑ Asc")
            self.refresh()

    def reset_all(self):
        self.search_var.set("")
        self.genre_var.set("All")
        self.sort_col.set("Film")
        self.ascending = True
        self.dir_label.set("↑ Asc")
        self.refresh()

    def refresh(self):
        """Apply search → filter → sort, then display results."""
        results = search_movies(self.all, self.search_var.get().strip())
        results = filter_by_genre(results, self.genre_var.get())
        results = sort_movies(results, self.sort_col.get(), self.ascending)
        self.shown = results
        self.show_movies(results)

    def show_movies(self, movies):
        """Clear the table and insert the given list of movies."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, movie in enumerate(movies):
            tag = "even" if i % 2 == 0 else "odd"
            values = tuple(movie.get(col, "") for col in COLUMNS)
            self.tree.insert("", tk.END, values=values, tags=(tag,))

    def show_detail(self, event):
        """Double-click a row to open a popup with full movie details."""
        selected = self.tree.selection()
        if not selected:
            return
        title = self.tree.item(selected[0], "values")[0]
        movie = next((m for m in self.shown if m.get("Film") == title), None)
        if not movie:
            return

        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("400x330")
        popup.resizable(False, False)
        popup.configure(bg=BG)
        popup.grab_set() 

        tk.Frame(popup, bg=AMBER, height=2).pack(fill=tk.X)
        tk.Label(popup, text=title,
                 font=("Georgia", 14, "bold"),
                 bg=BG, fg=TEAL, wraplength=370).pack(pady=(14, 4), padx=16)
        tk.Frame(popup, bg=SEP, height=1).pack(fill=tk.X, padx=20, pady=(0, 10))

        detail_frame = tk.Frame(popup, bg=BG)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=24)

        fields = [
            ("Genre",          "Genre"),
            ("Lead Studio",    "Lead Studio"),
            ("Audience Score", "Audience score %"),
            ("Rotten Tomatoes","Rotten Tomatoes %"),
            ("Worldwide Gross","Worldwide Gross"),
            ("Profitability",  "Profitability"),
            ("Year",           "Year"),
        ]
        for label, key in fields:
            value = movie.get(key, "")
            if not value or value == "0":
                continue
            row = tk.Frame(detail_frame, bg=BG)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=f"{label}:", width=16, anchor=tk.W,
                     font=("Helvetica", 10, "bold"), bg=BG, fg=FG2).pack(side=tk.LEFT)
            tk.Label(row, text=value, anchor=tk.W,
                     font=("Helvetica", 10), bg=BG, fg=FG).pack(side=tk.LEFT)

        tk.Button(popup, text="Close", command=popup.destroy,
                  bg=TEAL, fg="#fff", activebackground=TEAL2,
                  relief=tk.FLAT, font=("Helvetica", 10, "bold"),
                  padx=18, cursor="hand2").pack(pady=14)


# Run the app

def main():
    download_file(DATA_FILE, DATA_URL)
    movies = load_movies(DATA_FILE)
    if not movies:
        print("No movies loaded — check movies.csv")
        return
    root = tk.Tk()
    MovieApp(root, movies)
    root.mainloop()


if __name__ == "__main__":
    main()
