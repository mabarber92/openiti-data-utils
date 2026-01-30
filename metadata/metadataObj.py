import pandas as pd
import copy

class metadataObj():
    def __init__ (self, meta_csv, only_pri = True):
        self.meta = pd.read_csv(meta_csv, sep="\t")
        if only_pri:
            self.pri_only()
        self.meta["author_uri"] = self.meta["book"].str.split(".", expand=True)[0]
        
        # Make sure we have a language column to allow for comparing different datasets - set it to ara
        self.add_default_col("language", "ara")

        self.author = None
        self.date = None

    def pri_only(self):
        self.meta = self.meta[self.meta["status"] == "pri"]
    
    def add_default_col(self, col, default_val):
        """Function written To allow for language comparison, if the meta input lacks a language col - add one with 'ara' as the code
        Can be customised to add any default value to a set of columns in the metadata obj for comparison between inconsistent data"""
        if col not in self.meta.columns:
            self.meta[col] = default_val


    
    def only_books_before_date(self, date):
        self.meta = self.get_books_dated_between(0, date)

    # Functions for performing aggregate stats on self.meta 
    def count_books(self):
        return len(self.meta)
    def count_authors(self):
        return len(self.meta["author_uri"].drop_duplicates())
    def count_words(self):
        return self.meta["tok_length"].sum()

    def set_author_uri(self, author_uri):
        self.author_uri = author_uri
    
    def set_date(self, date):
        self.date = date
    
    def get_books_dated_between(self, start, end):
        self.date = end
        filtered_df = self.get_books_before_after(on="date")
        self.date = start
        filtered_df = self.get_books_before_after(on="date", after=True, df_in = filtered_df)
        self.date = None
        return filtered_df

    def get_books_before_after(self, on="author_uri", after=False, df_in = None):
        if df_in is not None:
            meta = df_in
        else:
            meta = self.meta
        if on == "author_uri":
            date = int(self.author_uri[:4])
            meta_filtered = meta[meta["author_uri"] != self.author_uri]
        elif on == "date":
            date = self.date
            meta_filtered = meta
        else:
            print("Choose a valid value for on - 'author_uri' or 'date' - you chose: '{}'".format(on))
            return None
        if after:
            return meta_filtered[meta_filtered["date"] >= date]
        else:
            return meta_filtered[meta_filtered["date"] <= date]
    
    def get_largest_books_before_after_author_uri (self, author_uri, top=25, after=False):
        self.author_uri = author_uri
        meta_filtered = self.get_books_before_after(after=after)
        meta_filtered = meta_filtered.sort_values(by=["tok_length"], ascending=False)
        return meta_filtered[["version_uri", "tok_length"]].iloc[:top]

    def get_largest_authors_before_after_author_uri (self, author_uri, top=25, after=False):
        self.author_uri = author_uri
        meta_filtered = self.get_books_before_after(after=after)
        author_list = meta_filtered["author_uri"].drop_duplicates().to_list()
        author_tok_sum = []
        for author in author_list:
            lengths = meta_filtered[meta_filtered["author_uri"] == author]["tok_length"].to_list()
            author_tok_sum.append({"author_uri": author, "total_written_tok": sum(lengths)})
        author_tok_sum_df = pd.DataFrame(author_tok_sum)

        author_tok_sum_df = author_tok_sum_df.sort_values(by=["total_written_tok"], ascending=False)
        return author_tok_sum_df[["author_uri", "total_written_tok"]].iloc[:top]
    
    def get_books_by(self, author):
        self.author_uri = author
        book_list = self.meta[self.meta["author_uri"] == self.author_uri]["book"].to_list()
        return book_list
    
    def fetch_lang_codes(self):
        """Return a list of language codes from the data"""
        codes = self.meta["language"].drop_duplicates().tolist()
        return codes
    
    def filter_language(self, lang_code):
        self.meta = self.meta[self.meta["language"] == lang_code]
    
    def return_lang_filtered(self, lang_code):
        new_obj = copy.copy(self)
        new_obj.filter_language(lang_code)
        return new_obj
    


