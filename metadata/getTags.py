import pandas as pd
import re

class getTags():
    def __init__ (self, meta_csv, col = "tags"):
        self.meta_df = pd.read_csv(meta_csv, sep="\t")
        self.fetch_col(col)
    def fetch_col(self, col="tags"):
        self.col_series = self.meta_df[col]
    def list_all_unique(self):
        return self.get_unique_sort().tolist()
    def df_all_unique(self, col_name = "unique_tags"):
        return self.get_unique_sort(col_name)
    def get_unique_sort(self, col_name = "unique_tags"):
        df = pd.DataFrame()
        df[col_name] = list(dict.fromkeys(self.list_of_all_tags()))
        return df.sort_values(by = col_name)
    def list_of_all_tags(self):
        final_list = []
        list_of_rows = self.col_series.dropna().tolist()
        for row in list_of_rows:            
            tag_list = re.split("\s*::\s+", row)
            final_list.extend(tag_list)
        if "" in final_list:
            print("Space found")
            final_list = [i for i in final_list if i != " "]
        return final_list
    # For future - set up class so obj can be filtered like it is a dataframe