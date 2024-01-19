import os
import re
import pandas as pd
from tqdm import tqdm

class metaYmls():
    def __init__ (self, corpus_path):
        yml_dirs = []
        for root, dirs, files in os.walk(corpus_path):
            for name in files:
                if name.split(".")[-1] == "yml":
                    full_path = os.path.join(root, name)
                    yml_dirs.append(full_path)
        
        if len(yml_dirs) > 1:
            print("Created list of yml directories")
            self.yml_dirs = yml_dirs[:]
        else:
            print("No ymls found in directory - try specifying corpus that contains yml files")
            self.yml_dirs = []
        
    def open_as_text(self, yml_dir):            
        with open(yml_dir, encoding='utf-8') as f:
            text = f.read()
        return text

    def parse_field(self, yml_text, field, sep=None):
        """If sep is specified, it uses the specified separator to separate 
        out the strings into a list - otherwise returns a string"""
        regex = field + r"([^\n]+)"        
        values = re.findall(regex, yml_text)        
        if len(values) > 0:            
            values = values[0]
            if sep is not None:
                values = re.split(sep, values)
            if type(values) == list:
                vals_cleaned = [] 
                for val in values:
                    if val == " ":
                        continue
                    else:
                        val_lstrip = val.lstrip()
                        value = val_lstrip.rstrip()
                        vals_cleaned.append(value)
                values = vals_cleaned[:]
            else:
                val_lstrip = value.lstrip()
                value = value.rstrip()

            return values
        else:
            return None
    
    def count_field_distinct(self, field = "90#VERS#ANNOTATOR:", sep=",", csv_path=None):
        field_dict = {}
        for yml_dir in tqdm(self.yml_dirs):
            values = self.parse_field(self.open_as_text(yml_dir), field, sep)
            if values is None:
                continue
            elif type(values) != list:
                values = [values]
            for value in values:
                if value not in field_dict.keys():
                    field_dict[value] = 1
                else:
                    field_dict[value] = field_dict[value] + 1
        df = pd.DataFrame(field_dict.items(), columns = [field, "count"])
        if csv_path is not None:
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        return df


if __name__ == '__main__':
    field = "90#VERS#ANNOTATOR:"
    sep= "[,();+]"
    csv_path = "anotators_count.csv"
    corpus_path = "E:/OpenITI Corpus/corpus_2023_1_8/"

    yml_obj = metaYmls(corpus_path)
    yml_obj.count_field_distinct(field, sep, csv_path=csv_path)


