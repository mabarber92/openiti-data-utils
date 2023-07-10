import re
import pandas as pd


def openiti_path_list_from_uri (uri, meta_csv, corpus_base_path, uri_type = "book", only_pri = True, meta_field="local_path"):
    meta = pd.read_csv(meta_csv)
    if only_pri:
        meta = meta[meta["status"] == "pri"]
    if type(uri) is not list:
        uri = [uri]
    meta = meta[meta[uri_type].isin(uri)]
    meta["abs_path"]= corpus_base_path + "/" + metadata[meta_field]
    meta_list = meta["abs_path"].to_list()
    return meta_list



class openitiTextGroup():
    def __init__ (self, uri, meta_csv, corpus_base_path, uri_type = "book", only_pri=True, meta_field="local_path"):
        meta = pd.read_csv(meta_csv, sep="\t")
        if only_pri:
            meta = meta[meta["status"] == "pri"]
        if type(uri) is not list:
            uri = [uri]
        self.meta = meta[meta[uri_type].isin(uri)]        
        self.meta["abs_path"] = corpus_base_path + self.meta[meta_field].str.split("/master/", expand = True)[1]
        self.path_list = self.meta["abs_path"].to_list()

    # Functions for performing action on an individual text   
    def _count_vols(self, text):
        
        return max([int(x) for x in re.findall(r"V(\d+)", text)])
    
    def _count_pages(self, text):
        # print(re.findall(r"V\d+P\d+", text))
        # print(text[0:500])
        return len(re.findall(r"PageV\d+P\d+", text))
    
    # Function for looping through the text path list and performing action
    def _loop_and_count(self, func):
        count = 0              
        for uri in self.path_list:
            with open(uri, encoding="utf-8") as f:
                text = f.read()            
            text_count = func(text)
            print(uri, text_count) 
            count = count + text_count
        return count
    
    # Functions for performing the actions
    def count_tokens(self):
        return self.meta["tok_length"].sum()
    
    def count_vols(self):
        return self._loop_and_count(self._count_vols)
    
    def count_pages(self):
        return self._loop_and_count(self._count_pages)

if __name__ == "__main__":
    corpus_base_path = "E:/OpenITI Corpus/corpus_2022_1_6/" 
    meta_csv = "E:/Corpus Stats/2021/OpenITI_metadata_2021-2-5.csv"
    tabariTexts = openitiTextGroup("Tabari", meta_csv, corpus_base_path, uri_type="author_from_uri")
    print("Total Tabari vol count: {}".format(tabariTexts.count_vols()))
    print("Total Tabari page count: {}".format(tabariTexts.count_pages()))
    print("Total Tabari token count: {}".format(tabariTexts.count_tokens()))
    