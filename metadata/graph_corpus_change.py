from metadataObj import metadataObj
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def run_aggregate(metadata_obj, aggregate_type):
    if aggregate_type == "words":
        return metadata_obj.count_words()
    elif aggregate_type == "books":
        return metadata_obj.count_books()
    elif aggregate_type == "authors":
        return metadata_obj.count_authors()
    else:
        raise ValueError("Invalid aggregate_type!")
    

def graph_corpus_change(metadata_paths_dicts, png_out_path, aggregate_stat = "words", comp_pri_sec = True, add_date_filter=1000):
    """Takes a metadata_paths_dicts, which is formatted as a list of dicts, as follows:
    [{"release_code": "2022.2.7", "path": "D:\metadata\metadata_path.csv"}]
    comp_pri_sec - if True, it will produce a graph with two lines, comparing the stat between just
    primary and all versions. If False it will produce one line for just pri
    aggregate stat can either been on 'words', 'books' or 'authors' - this specifies what to count"""

    sns.set_style("darkgrid")

    accepted_aggregates = ["words", "books", "authors"]
    if aggregate_stat not in accepted_aggregates:
        raise ValueError("Invalid aggregate type. Expected on of: %s" % accepted_aggregates)
    
    output_list = []

    for release_path in metadata_paths_dicts:

        # Get the release
        release_code = release_path["release_code"]

        # Create a metadataObj for the specified path and run the chosen aggregation
        metadata_obj = metadataObj(release_path["path"], only_pri=False)

        # If comparing - run an aggregate before filtering to pri_only
        if comp_pri_sec:
            output_row = {"Release Code" : release_code, aggregate_stat: run_aggregate(metadata_obj, aggregate_stat), "corpus": "all"}
            output_list.append(output_row)

        # Evertime - filter to pri only and add to output
        metadata_obj.pri_only()
        
        output_row = {"Release Code" : release_code, aggregate_stat: run_aggregate(metadata_obj, aggregate_stat), "corpus": "primary"}
        output_list.append(output_row)

        if add_date_filter is not None:
            metadata_obj.only_books_before_date(add_date_filter)
            output_row = {"Release Code" : release_code, aggregate_stat: run_aggregate(metadata_obj, aggregate_stat), "corpus": "before {}AH".format(add_date_filter)}
            output_list.append(output_row)
    
    # Transform output_list into df for processing
    df = pd.DataFrame(output_list)
    # print(df)
    # Create a link graph
    g = sns.lineplot(data = df, x="Release Code", y = aggregate_stat, hue="corpus")
    fig = g.get_figure()
    fig.savefig(png_out_path, dpi=300, bbox_inches = "tight")
    
    fig.clear()


if __name__ == "__main__":

    release_dicts_no_wcount = [
        {"release_code": "2019.1.1", "path": "D:/Corpus Stats/2019/OpenITI_metatdata_2019_1_1.csv"}
    ]

    release_dicts_all = [{"release_code": "2020.1.2", "path": "D:/Corpus Stats/2020/OpenITI_metadata_2020_1_2.csv"},
                         {"release_code": "2020.2.3", "path": "D:/Corpus Stats/2020/OpenITI_metadata_2020-2-3_merged.csv"},
                         {"release_code": "2021.1.4", "path": "D:/Corpus Stats/2021/OpenITI_metadata_2021-1-4_merged.csv"},
                         {"release_code": "2021.2.5", "path": "D:/Corpus Stats/2021/OpenITI_metadata_2021-2-5_merged_wNoor.csv"},
                         {"release_code": "2022.1.6", "path": "D:/Corpus Stats/2022/OpenITI_metadata_2022-1-6_merged.csv"},
                         {"release_code": "2022.2.7", "path": "D:/Corpus Stats/2023/OpenITI_metadata_2022-2-7_merged.csv"},
                         {"release_code": "2023.1.8", "path": "D:/Corpus Stats/2023/OpenITI_metadata_2023-1-8.csv"}
                         ]
    
    # Graph for word counts
    graph_corpus_change(release_dicts_all, "corpus_growth_words_pre1000.png")

    # Graph for book and author counts
    agg_types = ["books", "authors"]
    release_dicts_no_wcount.extend(release_dicts_all)
    for agg_type in agg_types:
        graph_corpus_change(release_dicts_no_wcount, "corpus_growth_{}_pre1000.png".format(agg_type), aggregate_stat=agg_type)

    


