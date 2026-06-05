import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd

# Ensure robust enough to work with just a reuse map and nothing else - also need to allow for section selection - via another filter csv? - or a keep col in the section csv

class multireuseGraph():


    def __init__(self, mapper_dir):
        """Initiate the graphing object using a directory to the mapping directory"""

        # Set the cols and filenames that the data needs for the graphing to work effectively - other cols are optional
        self.data_cols = {"section_map": {"path": "section_map.csv", "cols": ["heading", "offset"]},
                      "reuse_map": {"path" : "reuse_map.csv", "cols": ["start_offset", "end_offset", "book2"]},
                      "meta_mapper": {"path": "meta_mapper.csv", "cols": ["variable_name", "label"]}}
        # Check and load the incoming data
        self._check_and_load_data(mapper_dir)
    
    def _report_data_error(self, file_list, data_type, cols=None):
        """Func to handle the logic of populating files - if we have no reuse map we cannot proceed,
        otherwise we just report the issue to the user and skip the data type"""
        if cols is None:
            print(f"Valid {data_type} needed to produce graphs")
        else:
            print(f"Valid cols: {cols} needed for {data_type}")
        print(f"Files in directory: {file_list}")
        if data_type == "reuse_map":
            print("Cannot initiate graph without valid data")
            exit()
        else:
            print("Skipping this data type")
            

    def _check_and_load_data(self, mapping_dir):

        self.data_store = {}
        data_files = os.listdir(mapping_dir)
        for data_type, value in self.data_cols.items():
            if value["path"] in data_files:
                path = os.path.join(mapping_dir, value["path"])
                data = pd.read_csv(path)
                for col in value["cols"]:
                    if not col in data.columns:
                        self._report_data_error(file_list, data_type, cols=col)
                        # If invalid - set data to None so we don't use it later on
                        data = None

            else:
                self._report_data_error(data_files, data_type)
                # If the data type does not exist - we set it to none (handling reuse_map full failure type in the function)
                data = None
            
            self.data_store[data_type] = data
        print("Data store populated!")



        

    def _map_metadata(self):
        """Once we have a graph object, we rewrite any labels for which we have metadata"""

    def _create_rectangle(self, start, end, current_height, height_increase, annotation_box=False):
        """Use data about start, end position and height to create a rectangle using that data
        annotation_box: allows us to use the same func to draw an annotation box around interesting data"""
        
        xy = (start, current_height)
        width = end-start
        
        if annotation_box:
            linestyle = "-"
            linewidth = 0.5
            
        else:
            linestyle = None
            linewidth = None
            

        rect = Rectangle(xy, width, height_increase, facecolor='none', linestyle=linestyle, edgecolor='black', linewidth=linewidth)
        return rect

    def _write_patch_row(self, row_data, y_pos, row_height):
        """Write a row of patches for one book
        row_data: all data by one book to be populated to the row"""
    

    def _add_book_labels(self, label_list, y_pos_list):
        """Use a list of books and their positions on the y axis to add the labels"""

    def _sort_reuse_rows(self, reuse_data, sort_strategy):
        """Use reuse data to sort the data to appear on the y-axis according to specified sort strategy"""
        books = reuse_data.sort_values(by=["book2"])["book2"].drop_duplicates().to_list()
        if sort_strategy == "reuse":
            book_reuse_quan = {}
            for book in books:
                book_reuse = reuse_data[reuse_data["book2"] == book].to_dict("records")
                total_reuse = 0
                for reuse in book_reuse:
                    reuse_len = reuse["end_offset"] - reuse["start_offset"]
                    total_reuse += reuse_len
                book_reuse_quan[book] = total_reuse
            reordered = [k for k, v in sorted(book_reuse_quan.items(), key=lambda item: item[1], reverse=True)]
        if sort_strategy == "chron":
            reordered = books
        
        return reordered


    def _write_graph_patches(self, sort_strategy="chron"):
        """Write all patches for the graph
        sort_strategy: chron == sort y-axis rows by author death date | reuse == sort yaxis rows by quantity of reuse """
        reuse_data = self.data_store["reuse_map"]
        
        # Sort the data first - so we process the rows in the order desired order
        books = self._sort_reuse_rows(reuse_data, sort_strategy)
        print(books)

        # TODO: Loop through each book - pass the data to the row writer to write the rows - log y-pos as we go

        # After rows have been written write the ylabels using the function - from the book list and ypos

    def _write_section_maps(self, add_vlines=True, vline_height="-0.1"):
        """Add the section labels to the graph
        add_vlines: add vlines as well as the labels to the x-axis
        vline_height: percentage of total data used by vline - if 1 then vline will use the whole graph
                    negative numbers will draw the lines below the graph"""
    
    def create_reuse_graph(self, row_gaps=0.1, figsize=None):
        """Full func for handling graph writing
        row_gaps: gaps between rows of data as percentage of the total graph 0 puts each row adjacent"""

        # Run graph initiation
        if figsize is None:
            px = 1/plt.rcParams['figure.dpi']
            figsize = (800*px, 1200*px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)

        patch_collection = self._write_graph_patches()

    def write_figure(self, image_path):
        """Allows us to write the figure after tweaking things - like adding annotation"""
