import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import matplotlib as mpl

# Ensure robust enough to work with just a reuse map and nothing else - also need to allow for section selection - via another filter csv? - or a keep col in the section csv

class multireuseGraph():


    def __init__(self, mapper_dir):
        """Initiate the graphing object using a directory to the mapping directory"""

        # Set the cols and filenames that the data needs for the graphing to work effectively - other cols are optional
        self.data_cols = {"section_map": {"path": "section_map.csv", "cols": ["heading", "offset", "level", "bio"]},
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

    def _create_rectangle(self, start, end, current_height, height, color='grey', annotation_box=False):
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
            

        rect = Rectangle(xy, width, height, facecolor=color, linestyle=linestyle, edgecolor='black', linewidth=linewidth)
        return rect

    def _write_patch_row(self, row_data, v_bottom, row_height):
        """Write a row of patches for one book
        row_data: all data by one book to be populated to the row"""
        row_patches = []
        row_dicts = row_data.to_dict('records')

        for row in row_dicts:
            rect = self._create_rectangle(row["start_offset"], row["end_offset"], v_bottom, row_height)
            row_patches.append(rect)
        
        return row_patches

    

    def _add_book_labels(self, label_list, y_pos_list):
        """Use a list of books and their positions on the y axis to add the labels"""

        meta_mapper = self.data_store["meta_mapper"]

        if meta_mapper is not None:
            updated_labels = []
            for label in label_list:
                meta_map = meta_mapper[meta_mapper["variable_name"] == label]["label"].dropna().values.tolist()
                
                if len(meta_map) > 0:
                    updated_labels.append(meta_map[0])
                    
                else:
                    label = label.replace(".", "\n")
                    
                    updated_labels.append(label)
        else:
            updated_labels = label_list.copy()
        
        self.ax.set_yticks(y_pos_list, updated_labels)
        




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


    def _write_graph_patches(self, sort_strategy="chron", row_gap=0.1):
        """Write all patches for the graph
        sort_strategy: chron == sort y-axis rows by author death date | reuse == sort yaxis rows by quantity of reuse
        row_gap: percentage of the row height that will be used as a gap between each row - 0 === no gap between rows """
        reuse_data = self.data_store["reuse_map"]
        
        # Sort the data first - so we process the rows in the order desired order
        books = self._sort_reuse_rows(reuse_data, sort_strategy)
        
        # Initialise starting parameters
        self.height_increase = 100/len(books)
        v_bottom = 0
        label_pos = []
        patch_list = []

        # Loop through each book - pass the data to the row writer to write the rows - log y-pos as we go
        for book in books:
            # Get data
            data = reuse_data[reuse_data["book2"] == book]
            # Fetch row height
            row_height = self.height_increase * (1-row_gap)
            
            # Write patches and add to patch_list
            patches = self._write_patch_row(data, v_bottom, row_height)
            patch_list.extend(patches)

            # Add label pos
            label_y = v_bottom + (row_height/2)
            label_pos.append(label_y)

            # Augment v_bottom
            v_bottom += self.height_increase

        
        # Transform the patch list into a patch collection, add to axis
        
        patch_collection = PatchCollection(patch_list, color="black")
        self.ax.add_collection(patch_collection)
        self.ax_height=v_bottom
        self.ax.set_ylim(0, self.ax_height)
        # Add labels to axis
        self._add_book_labels(books, label_pos)

        # Return patch_collection in case we need to make edits later
        return patch_collection

    def _get_level_heights(self, data, bottom, top):
        level_count = len(data["level"].drop_duplicates())
        section_patch_height = (top-bottom) / level_count
        return section_patch_height, level_count

    def _add_overlay_annotations(self, annotation_list, font_size=8):

        for annotation in annotation_list:
            self.ax.text(annotation["x"], annotation["y"], annotation["label_text"], size = font_size, va=annotation["va"]
                     )

    def _calculate_shading(self, level_count, cmap_name="binary", alternate_shades=False, low_margin=0.15, high_margin=0.4):
        """Create the shader that can be passed to the patch_collection for shading of sections
        and alternating the shades of each section if desired
        level_count: total number of levels in the text
        cmap_name: cmap to initialise - best cmaps = sequential (e.g. 'binary', 'Greys')
        alternate_shades: output a list of list of integers to allow for alternating of shading between each section
        low_margin: fraction of the colormap to exclude at the light end
        high_margin: fraction of the colormap to exclude at the dark end - increase to avoid overly dark shades
        returns
        mapping_index: per-level integer(s) to pass as the patch value for colormap lookup
        cmap: initialised cmap to pass to the patch_collection
        norm: Normalize instance that maps [0, total_shades-1] to [low_margin, 1-high_margin] in colormap space"""

        mapping_index = []
        current_index = 0
        for i in range(level_count):
            if alternate_shades:
                mapping_index.append([current_index, current_index+1])
                current_index += 2
            else:
                mapping_index.append(current_index)
                current_index += 1

        total_shades = current_index
        cmap = mpl.colormaps[cmap_name]

        # Derive vmin/vmax so that integer values [0, total_shades-1] map to [margin, 1-margin]
        # in colormap space, keeping away from the harsh ends of sequential maps
        if total_shades > 1:
            shade_range = (total_shades - 1) / (1 - low_margin - high_margin)
            vmin = -low_margin * shade_range
            vmax = vmin + shade_range
        else:
            vmin, vmax = -low_margin, 1 + high_margin

        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        return mapping_index, cmap, norm

    def _add_heirarchical_shading(self, data, bottom, top, pos, overlay_annotation=[1], alternate_shades=False, extend_shades=1):
        """"overlay_annotation: add the metadata or original section heading text as an overlay to that level - unlikely to work
                                for large texts above level 1
            extend_shades: level to extend the shading across the graph - only applied with alternate_shades, if 0 shades are not extended"""

        # Use bottom and top and number of levels to get patch height
        section_patch_height, level_count = self._get_level_heights(data, bottom, top)

        # # Initialise cmap as a list for heirarchical tiers
        # colors = mpl.colormaps['Dark2'].colors
        # # Loop through levels and create patches
        y_pos = top
        print(y_pos)

        shading_index, cmap, norm = self._calculate_shading(level_count, alternate_shades=alternate_shades)

        # Determine whether to use metadata col or heading col
        if "label" in data.columns:
            if len(data["label"].dropna()) > 0:
                annotation_col = "label"
            else:
                annotation_col = "heading"
        
        for i in range(1, level_count+1):
            color_pos = 0
            patch_list = []
            patch_values = []
            vlines = []
            annotations_list =[]
            filtered_data = (data[data["level"] <= i]
                             .sort_values(by=["offset", "level"])
                             .drop_duplicates(subset=["offset"])
                             .to_dict("records"))
            for idx, row in enumerate(filtered_data[:-1]):
                if alternate_shades:
                    selected_color = shading_index[i-1][color_pos]
                    color_pos = 1 - color_pos
                else:
                    selected_color = shading_index[i-1]
                
                height = section_patch_height
                start = y_pos-section_patch_height
                if alternate_shades and extend_shades != 0:
                    if i == extend_shades:
                        height = (level_count - i + 1) * section_patch_height + self.ax_height
                        if pos == 'top':
                            start = y_pos-height
                        

                patch = self._create_rectangle(row["offset"], filtered_data[idx+1]["offset"], start, height)
                patch_list.append(patch)
                patch_values.append(selected_color)
                if row["level"] <= i:
                    vlines.append(row["offset"])
                if i in overlay_annotation:
                    annotation = row[annotation_col]                      
                    if str(annotation) == "nan":
                        annotation = ""
                    
                    annot_y = y_pos - section_patch_height/2                             
                    annotations_list.append({"label_text": annotation,
                    "y" : annot_y,
                    "x" : row["offset"] + (filtered_data[idx+1]["offset"]- row["offset"])*0.05,
                    "va": "center"
                    })
                if len(annotations_list) > 0:
                    self._add_overlay_annotations(annotations_list)
                         
                # add condition for overlay annotation


            # Line below - added vlines, but this made small sections unreadable 
            if not alternate_shades:
                self.ax.vlines(vlines, y_pos-section_patch_height, y_pos, color='black', linewidth=0.5)
            if pos == 'top':
                h_pos = y_pos-section_patch_height
            else:
                h_pos = y_pos
            self.ax.axhline(h_pos, color='black', linewidth=0.75)
            
            patch_collection = PatchCollection(patch_list, cmap=cmap, norm=norm)
            patch_collection.set_array(patch_values)
            self.ax.add_collection(patch_collection)
            y_pos -= section_patch_height
        
        




    def _add_section_lines(self, data, outside_axis, inside_axis, pos, keep_offset_scale=True, heirarchical_shading=True, dotted_vlines_level=0,
        overlay_annotation = [1], alternate_shades=False, extend_shades=0):
        """Use a list of x positions, and floats for proportion of data outside axis and inside axis to add vlines,
        and a horizonal line to add the section annotation.
        x_pos: list of values along x axis for position of vlines
        outside_axis: how far outside of the axis should the line be (as a decimal representation of the data 0.1 == lines 10% length of total data)
        inside_axis: how far into the graph should the lines be (as a decimal representation of the data 0.1 == lines 10% length of total data inside graph)
        pos: position of section lines - 'top' == above graph, 'bottom' == below graph
        keep_offset_scale: if True, retain a measure of the number of tokens/chars into text on the axis. If True and pos == 'bottom' - token scale is moved
                            to the top of the graph
        heirarchical_shading: if True add boxes that reflect the heirarchy of the text
        TODO: Add option for hierachical section shading

        Use a decimal (a percentage) to produce new height data that represents the data within the graph itself
        pos: top - move to top of the graph, bottom - move to bottom of graph
        TODO: Test this logic with top and bottom config - to check it draws as expected - ISSUES HERE NEED RESOLUTION
        Need to return to this and reappraise logic as confounding two factors"""

        # Calculate line top and bottom depending on pos
        if pos == 'bottom':
            bottom = 1 - (outside_axis*self.ax_height)
            top = inside_axis*self.ax_height
            h_line_pos = 0
        if pos == 'top':
            bottom = self.ax_height - (inside_axis*self.ax_height)
            top = self.ax_height + (outside_axis*self.ax_height)
            h_line_pos = self.ax_height
        
        # If keep_offset_scale and 'bottom' - move the scale to the top - otherwise remove axis
        if keep_offset_scale:
            if pos == 'bottom':
                self.ax.xaxis.tick_top()
        else:
            self.ax.xaxis.set_visible(False)
        
        
        

        # If heirarchical_shading - add boxes for the heirarchical shading
        if heirarchical_shading:
            self._add_heirarchical_shading(data, bottom, top, pos, overlay_annotation=overlay_annotation, alternate_shades=alternate_shades, extend_shades=extend_shades)
        
        # Get x_pos from the data
        x_pos = data["offset"].values.tolist()
        # Add the vlines
        if not heirarchical_shading:
            # Draw a horizontal line for the start of the section labelling
            self.ax.axhline(h_line_pos, color='black')
            self.ax.vlines(x_pos, bottom, top, color='black', linewidth=0.5)

        
        if dotted_vlines_level > 0:
            x_pos = data[data["level"] <= dotted_vlines_level]["offset"].values.tolist()

            self.ax.vlines(x_pos, 0, self.ax_height, linewidth=0.5, linestyle='--', color='black')

        # If extend_shades is not 0 - we need to redraw patches
        if extend_shades != 0:
            patch_collection = self._write_graph_patches(row_gap=self.row_gap, sort_strategy=self.sort_strategy)

        # TO DO: Add labels to left of the section markers for each section (using annotation)

        # Reset plot ylims to make the data visible - taking maximum top and bottom of the data
        self.ax.set_ylim(min([0, bottom]), max([self.ax_height, top]))

        


    def _write_section_maps(self, add_vlines=True, vline_start=0.4, vline_height=0, heading_levels=None, exclude_bios=False, 
                            add_labels=True, pos='top', keep_offset_scale=True, heirarchical_shading=True, dotted_vlines_level=0,
                            overlay_annotation=[1], alternate_shades=False, extend_shades=0):
        """Add the section labels to the graph
        add_vlines: add vlines as well as the labels to the x-axis
        vline_start: position on graph (as percentage of data to start the vline) - -0.1 = start below the xaxis, 10% of total height of graph
                    below the xaxis
        vline_height: percentage of total data used by vline - if 1 then vline will use the whole graph
                    if 0, will draw from vline_start to xaxis
        heading_levels: which heading levels to use as list [1,2] - use levels 1 and 2 - if None, use all in the data
        add_labels: add labels to the xaxis based on labels in the data
        pos: 'top' - labels and section markers at the top of the graph, 'bottom' labels and sections markers at the bottom of the graph
        keep_offset_scale: keep the scale in chars or tokens, position will be altered based on the pos of the section labels
        heirarchical_shading: add shading to the bottom section bar that highlights sections
        dotted_vlines_level: up to which level in the hierarchy to add dotted lines across the graph - 0 == do not use
        """
        section_map = self.data_store["section_map"]
        if section_map is None:
            print("Cannot add vlines for sections without sections")
        else:
            # Filter the data based on level and bio
            if heading_levels is not None:
                section_map = section_map[section_map["level"].isin(heading_levels)]
            if exclude_bios:
                section_map = section_map[section_map["bio"] != True]
            
            # Add vlines using remaining data
            if add_vlines:
                self._add_section_lines(section_map, vline_start, vline_height, pos=pos, keep_offset_scale=keep_offset_scale,
                heirarchical_shading=heirarchical_shading, dotted_vlines_level=dotted_vlines_level, overlay_annotation=overlay_annotation,
                alternate_shades=alternate_shades, extend_shades=extend_shades)

    def _calculate_set_xlim(self, end_marker="text_end"):
        """From data infer xlims"""
        section_map=self.data_store["section_map"]
        if section_map is not None:
            end_pos = section_map[section_map["heading"] == end_marker]["offset"].tolist()[0]
        else:
            # If we lack a section map - take last offset in the reuse data
            end_pos = self.data_store["reuse_map"]["offset_end"].max()
        
        # To do : Add ability to use this as a way to filter based on section header range

        self.ax.set_xlim(0, end_pos)

    def create_reuse_graph(self, sort_strategy='chron', row_gap=0.1, figsize=None):
        """Full func for handling graph writing
        row_gaps: gaps between rows of data as percentage of the total graph 0 puts each row adjacent
        sort_strategy: strategy used to sort books on the yaxis - 'chron' : chronological sorting, oldest book at
        bottom to newest book at top, 'reuse' : sort by quantity of reuse for each book based on the offsets"""

        # Run graph initiation
        if figsize is None:
            px = 1/plt.rcParams['figure.dpi']
            figsize = (1200*px, 800*px)
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax_height=0
        self.ax_bottom=0
        self.row_gap = 0.1
        self.sort_strategy = sort_strategy

        patch_collection = self._write_graph_patches(row_gap=self.row_gap, sort_strategy=self.sort_strategy)
        self._calculate_set_xlim()

    def write_figure(self, image_path):
        """Allows us to write the figure after tweaking things - like adding annotation"""
