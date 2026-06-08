from openiti_texts.openitiTexts import openitiTextMs, openitiCorpus
import os
import pandas as pd
# Codes to create raw offset mappings from pairwise data

# Need to use openitiTexts full_ms_offsets_df and section_offset_df
# Should have ability to export a section map for annotation and then
# reload on that - so on init check if the section map already exists

class pairwiseMapper():
    """Take a directory of pairwise tsvs and produce a series of mapping files
    that map offsets into the text as a whole and corresponding section maps
    exports a csv section map reuse map and uri meta mapper that together can be
    used to product graphs of pairwise at the token or char level"""

    def __init__(self, main_text_uris: type(list), corpus_dir: type(str), pairwise_dir: type(str), out_dir: type(str), meta_path=None, load_from_corpus=True):
        """Initialise with core data
        main_text_uris: book uris - used to fetch data from a corpus folder - for each main text, a map against all relevant pairwise files
                        will be created - if None - then the pairwise_dir will be used to fetch a list of all possible texts
        corpus_dir: directory containing the texts or path to full openiti corpus
        pairwise_dir: a directory of pairwise files to be used for creating the mappings
        our_dir: directory for storing maps - will produce nested structure: out_dir/book_uri/*mapping_file
        meta_path: needed if loading from full corpus - to produce the correct paths to the supplied uris
        load_from_corpus: if True, corpus_dir = full openiti corpus path and meta will be used to build the corpus paths
        
        NOTE: Currently assume a single level structure for the pairwise files - if we want to use nesting structures a func will be needed to convert
        the next into a list of paths to pairwise files"""

        if main_text_uris is None:
            main_text_uris = self._fetch_uris_from_pairwise(os.listdir(pairwise_dir))

        self.main_text_path_dict = self._initialise_texts(main_text_uris, corpus_dir, meta_path, load_from_corpus)
        self.main_text_uris = list(self.main_text_path_dict.keys())
        print(f"Initialised pairwiseMapper with {len(self.main_text_uris)} main texts for mapping")
        self.out_dir = out_dir

        self.pairwise_path_dict = self._id_pairwise_for_main(pairwise_dir)


    def _initialise_texts(self, main_text_uris, corpus_dir, meta_path, load_from_corpus):
        """Check that all main_text_uris have corresponding texts in the corpus dir, or build a path list of loading from corpus"""
        # If loading from corpus - we use the corpus object to create relevant text paths for the main texts
        if load_from_corpus:
            if meta_path is None:
                print("ERROR: meta_path is set to None. To load from corpus provide a path to metadata")
                exit()
            corpus_object = openitiCorpus(meta_path, corpus_dir)
            path_dict = corpus_object.fetch_path_for_books(main_text_uris, return_dict=True)
            return path_dict
        
        # Otherwise we check that all supplied main_text_uris have a corresponding path in corpus_dir and return paths
        else:
            return self._check_and_return_paths(main_text_uris, corpus_dir)

    def _check_and_return_paths(self, book_uris, corpus_dir):
        """Go through book URIs, check that every URI has a corresponding path, check with user if match isn't found and return matching paths"""
        text_paths = os.listdir(corpus_dir)
        selected_paths = {}
        for book_uri in book_uris:
            matching_paths = [p for p in text_paths if book_uri in p]
            matching_count = len(matching_paths)
            if matching_count == 0:
                print(f"WARNING: No matching path found for {book_uri}. Proceed without this main URI?")
                input()
            else:
                if matching_count > 1:
                    print(f"Multiple matching paths found in directory. Choose the number for the correct path:")
                    for idx, path in matching_paths:
                        print(f"{idx} : {path}")
                    selected_idx = int(input())
                else:
                    selected_idx = 0
                
                matching_path = os.path.join(corpus_dir, matching_paths[selected_idx])
                selected_paths[book_uri] = matching_path

        return selected_paths
    
    def _initialise_output_dirs(self, out_dir=None):
        """When processing data mapping we use this func to check and create relevant output files"""
        if out_dir is None:
            out_dir = self.out_dir
        for text in self.main_text_uris:            
            out_path = os.path.join(out_dir, text)
            if not os.path.exists(out_path):
                os.mkdir(out_path)
        return out_dir

    def _pairwise_file_to_uris(self, pairwise_filename, splitter = "_"):
        """Split a pairwise_filename on _ and reduce to a book_uri return as list
        returns: list of len 2"""
        
        full_uris = pairwise_filename.split(splitter)
        book_uris = [".".join(parts.split(".")[:2]) for parts in full_uris]
        
        if len(book_uris) != 2:
            print(f"Invalid pairwise filename found {pairwise_filename}")
            exit()
        
        return book_uris

    def _fetch_uris_from_pairwise(self, pairwise_files):
        """Take a list of paths and fetch the book_URIs from within them"""
        
        book_uris = [self_pairwise_file_to_uris(file) for file in pairwise_files]

        # Remove duplicates and return
        unique_books = list(set(book_uris))
        return unique_books


    def _id_pairwise_for_main(self, pairwise_dir):
        """Using dir of pairwise files - check for matches to main_text_uris and create a dict mapping uris to lists of
        pairwise files
        returns: dict {"book_uri": [{"path": pairwise_path, "uri_pos": 1 or 2}]}
                where uri_pos documents whether the uri is in the first or second position in the file"""
        
        pairwise_dict = {}
        pairwise_files = os.listdir(pairwise_dir)

        for book_uri in self.main_text_uris:
            matching_pairwise_files = [pairwise_file for pairwise_file in pairwise_files if book_uri in pairwise_file]
            pairwise_list = []
            for matching_pairwise in matching_pairwise_files:
                uris = self._pairwise_file_to_uris(matching_pairwise)
                # func always returns uris in order hey appear in filename - so we can use the pos to infer whether relevant data is text1 or text2
                pos = uris.index(book_uri) + 1
                
                # Add data to the list for this book
                pairwise_list.append(
                    {"pairwise_file": os.path.join(pairwise_dir, matching_pairwise),
                    "pos": pos}
                )
            pairwise_dict[book_uri] = pairwise_list
        
        return pairwise_dict

    def _concat_pairwise_data(self, main_uri):
        """Take a main_uri fetch the pairwise data from the dict and use it to load and concatenate the
        relevant data. Rename cols so that they will work with the openitiTextMs funcs
        main_uri: book_uri
        returns: list of dicts {"ms": main_ms, "start_offset": start, "end_offset": end, "book2": aligned_book, "ms2": aligned_ms}"""

        pairwise_paths = self.pairwise_path_dict[main_uri]
        concat_df = pd.DataFrame()
        for path in pairwise_paths:
            df = pd.read_csv(path["pairwise_file"], sep="\t")
            
            # Select and rename relevant cols
            pos = path["pos"]
            if pos == 2:
                book_cols = ["seq2", "begin2", "end2", "series_b1", "seq"]
                df = df[book_cols]
                df = df.rename(columns={"seq2": "ms", "begin2": "start_offset", "end2": "end_offset", "series_b1": "book2", "seq": "ms2"})
            if pos == 1:
                book_cols = ["seq", "begin", "end", "series_b2", "seq2"]
                df = df[book_cols]
                df = df.rename(columns={"seq": "ms", "begin": "start_offset", "end": "end_offset", "series_b2": "book2", "seq2": "ms2"})
            
            concat_df = pd.concat([concat_df, df])
            
        # Return list of dicts
        return concat_df.to_dict("records")

    def _write_meta_mapper(self, main_uri, reuse_map, token_map, out_dir, col_1="variable_name", col_2="label"):
        
        meta_mapper = []
        # Append the units to the meta_mapper
        if token_map:
            unit_label = "tokens"
        else:
            unit_label = "characters"
        units_map = {col_1: "offset_units", col_2: unit_label}
        meta_mapper.append(units_map)

        # Use the mapping_df to fetch all book ids
        book_ids = reuse_map["book2"].drop_duplicates().to_list()
        book_ids += [main_uri]
        for book_id in book_ids:
            meta_mapper.append({
                col_1: book_id,
                col_2: ""
            })
        
        meta_map_df = pd.DataFrame(meta_mapper)
        csv_path = os.path.join(out_dir, "meta_mapper.csv")
        meta_map_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        return meta_map_df


    def write_maps_for_uri(self, main_uri, out_dir, sections_levels=None, use_bio_sections=True, 
                            section_meta_mapper=True, general_meta_mapper=True, token_map=False):
        """Write a map for a specific URI
        main_uri: book uri to be mapped - used to access text path and pairwise paths stored in pairwiseMapper
        out_dir: directory into which the csv maps are written
        section_levels: if None use all levels in the text, otherwise use up to level - e.g. 2 = [### |, ### ||]
        use_bio_sections: if True, use biographical headers as sections, otherwise exclude them from the section map
        section_meta_mapper: ensure the section mapper csv contains a column for manual mapping of metadata to be used by
                            graphs
        general_meta_mapper: a separate csv used for mapping metadata to be used by a graph (book uris, offset units)
                            Columns: [variable_name, label_mapping]
        token_map: if True the char offsets in the pairwise are converted to tokens, and section offsets are calculated
                    as tokens. Useful for more understable graphs"""
        
        # Initialise the OpenITI text object
        text_path = self.main_text_path_dict[main_uri]
        openiti_obj = openitiTextMs(text_path, report=True)

        # Write the section map
        section_map_path = os.path.join(out_dir, "section_map.csv")
        if section_meta_mapper:
            meta_cols = ["label"]
        openiti_obj.section_offset_df(levels_count=sections_levels, include_bios=use_bio_sections, 
                                        csv_path=section_map_path, meta_cols=meta_cols, token_offset=token_map,
                                         end_marker="text_end")

        # Concat the relevant pairwise data and produce and write offsets
        reuse_map_path = os.path.join(out_dir, "reuse_map.csv")
        concat_data = self._concat_pairwise_data(main_uri)
        
        mapping_df = openiti_obj.full_ms_offset_df(concat_data, csv_path=reuse_map_path, token_offset=token_map)
        
        # Use the map to write a general_meta_mapper
        if general_meta_mapper:
            self._write_meta_mapper(main_uri, mapping_df, token_map, out_dir)
        

    def map_main_uris(self, sections_levels=None, use_bio_sections=True, 
                    section_meta_mapper=True, general_meta_mapper=True, token_map=False, out_dir=None):
        """Write maps for all the main uris. For all main_uris stored in object
                section_levels: if None use all levels in the text, otherwise use up to level - e.g. 2 = [### |, ### ||]
        use_bio_sections: if True, use biographical headers as sections, otherwise exclude them from the section map
        section_meta_mapper: ensure the section mapper csv contains a column for manual mapping of metadata to be used by
                            graphs
        general_meta_mapper: a separate csv used for mapping metadata to be used by a graph (book uris, offset units)
                            Columns: [variable_name, label_mapping]
        token_map: if True the char offsets in the pairwise are converted to tokens, and section offsets are calculated
                    as tokens. Useful for more understable graphs"""
        
        # Check all paths have been created - using out_dir or default out_dir if it is set to none
        out_dir = self._initialise_output_dirs(out_dir)

        for main_uri in self.main_text_uris:
            print(f"Writing maps for {main_uri}")
            maps_path = os.path.join(out_dir, main_uri)
            self.write_maps_for_uri(main_uri, maps_path, sections_levels=sections_levels, use_bio_sections=use_bio_sections,
                                    section_meta_mapper=section_meta_mapper, general_meta_mapper=general_meta_mapper,
                                    token_map=token_map)

                




