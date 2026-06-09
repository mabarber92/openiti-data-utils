
from pairwise_data.pairwise_mapping import pairwiseMapper
from pairwise_data.graph_pairwise import multireuseGraph

out_dir = "./data/outputs"
corpus_dir = "./data/passim_corpus/"
pairwise_dir = "./data/passim_results/"
main_uris = ["0375AnonymousTranslator.TarikhCalamUrusiyus"]
data_dir = "./data/outputs/0375AnonymousTranslator.TarikhCalamUrusiyus"

# pairwise_mapper = pairwiseMapper(main_uris, corpus_dir, pairwise_dir, out_dir, load_from_corpus=False)
# pairwise_mapper.map_main_uris(sections_levels=2, token_map=True)
# pairwise_mapper.map_main_uris(sections_levels=2, out_dir = "./data/char_outputs/")

multireuse_graph = multireuseGraph(data_dir)
multireuse_graph.create_reuse_graph(sort_strategy="chron")
multireuse_graph._write_section_maps(vline_height=0, vline_start=0.1, pos='top', dotted_vlines_level=1, alternate_shades=True, extend_shades=1)
multireuse_graph.fig.savefig("chron_test.png", bbox_inches="tight", dpi=300)

multireuse_graph.create_reuse_graph(sort_strategy="reuse")
multireuse_graph._write_section_maps(vline_height=0, vline_start=0.1, pos='top', dotted_vlines_level=1, alternate_shades=True, extend_shades=1)
multireuse_graph.fig.savefig("reuse_test.png", bbox_inches="tight", dpi=300)
