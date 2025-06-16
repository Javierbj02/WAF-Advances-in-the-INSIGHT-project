import json
from scenario_builder import ScenarioBuilder
from ontology_utils import load_ontology, initialize_ontology, relate_term_to_ontology, search_lov, search_ols, search_wikidata
from sentence_transformers import SentenceTransformer, util

def main():
    owl_path = "data/SOMA_and_OCRA.owl"
    
    initialize_ontology(owl_path)
#    return
    
#    ontology = load_ontology(rdf_path)
    ontology = load_ontology(owl_path)    
    builder = ScenarioBuilder()

    input_terms = ['achieve', 'collaborate', 'deliver', 'destination', 'follow', 'goal', 'hospital', 'human', 'location', 'medicine', 'nurse', 'place', 'robot', 'supervisor', 'take', 'object']

    model = SentenceTransformer('all-MiniLM-L6-v2')
    for term in input_terms:
        builder.add_term(term)
        matches = relate_term_to_ontology(term, ontology, False)

        if matches:
            for match in matches:
                builder.add_relation(term, match)
        else:
            suggestionsA = search_lov(term)
            suggestionsB = search_ols(term)
            suggestionsC = search_wikidata(term)            
            
            suggestions = suggestionsA + suggestionsB + suggestionsC
            
            for suggest in suggestions:
                builder.add_relation(term, suggest)
                
    res = json.loads(json.dumps(builder.export(), indent=2))
    #print(res["relations"]["achieve"])

    for term in input_terms:
        print(f'\n\n Term: {term} \n\n')
        for relation in res["relations"][term]:
            embeddings_T_L_D = model.encode([term, relation["label"], relation["description"]], convert_to_tensor=True)
            term_label_sim = util.pytorch_cos_sim(embeddings_T_L_D[0], embeddings_T_L_D[1])
            term_desc_sim = util.pytorch_cos_sim(embeddings_T_L_D[0], embeddings_T_L_D[2])
            relation["similarity_embedding"]= max(term_label_sim, term_desc_sim) 
            print(relation)
            print(f'\n')
        print(f'\n\n ----------- \n\n')
            
    print(res)            

#    for build in builder.export():
#        embeddings_T_L_D = model.encode([build["term"], build["label"], build["description"]], convert_to_tensor=True)
#        term_label_description = util.pytorch_cos_sim(embeddings[0], embeddings[1])
#        ontology_match["similarity"] = max(similarity_description.item(), ontology_match["similarity"])           

#    print(json.dumps(builder.export(), indent=2))
    

if __name__ == "__main__":
    main()
