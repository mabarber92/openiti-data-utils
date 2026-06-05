from openiti_texts.openitiTexts import openitiTextms, openitiCorpus
import os
# Codes to create raw offset mappings from pairwise data

# Need to use openitiTexts full_ms_offsets_df and section_offset_df
# Should have ability to export a section map for annotation and then
# reload on that - so on init check if the section map already exists

class pairwise_mapper():
    """Take a directory of pairwise tsvs and produce a series of mapping files
    that map offsets into the text as a whole and corresponding section maps
    exports a csv section map reuse map and uri meta mapper that together can be
    used to product graphs of pairwise at the token or char level"""

    def __init__(self, main_text_uris: type(list), corpus_dir: type(str), pairwise_dir: type(str), out_dir: type(str) meta_path=None, load_from_corpus=True):
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
        self.out_dir = out_dir

        self.pairwise_path_dict = self._id_pairwise_for_main(pairwise_dir)


    def _initialise_texts(self, main_text_uris, corpus_dir, meta_path, load_from_corpus):
        """Check that all main_text_uris have corresponding texts in the corpus dir, or build a path list of loading from corpus"""
        # If loading from corpus - we use the corpus object to create relevant text paths for the main texts
        if load_from_corpus:
            corpus_object = openitiCorpus(meta_path, corpus_dir)
            path_dict = corpus_object.fetch_path_for_books(main_text_uris, return_dict=True)
            return path_dict
        
        # Otherwise we check that all supplied main_text_uris have a corresponding path in corpus_dir and return paths
        else:
            return self._check_and_return_paths()

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
    
    def _initialise_output_dirs(self):
        """When processing data mapping we use this func to check and create relevant output files"""
        
        for text in self.main_text_uris:            
            out_path = os.path.join(self.out_dir, text)
            if not os.path.exists(out_path):
                os.mkdir()

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


                




