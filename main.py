
from pairwise_data.pairwise_mapping import pairwiseMapper

out_dir = "./data/outputs"
corpus_dir = "./data/passim_corpus/"
pairwise_dir = "./data/passim_results/"
main_uris = ["0375AnonymousTranslator.TarikhCalamUrusiyus"]

pairwise_mapper = pairwiseMapper(main_uris, corpus_dir, pairwise_dir, out_dir, load_from_corpus=False)
pairwise_mapper.map_main_uris(sections_levels=2, token_map=True)
pairwise_mapper.map_main_uris(sections_levels=2, out_dir = "./data/char_outputs/")
