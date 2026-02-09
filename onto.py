from rdflib import Graph, URIRef

g = Graph()
g.parse("./turtle/OntoPokemon.ttl", format="turtle")

print(len(g))  # nombre de triplets


for s, p, o in g: # Sujet prédicat objet
    print(s, p, o)



# pred = URIRef("http://www.semanticweb.org/arthu/ontologies/2026/0/untitled-ontology-4/EvolvesTo")

# for s, p, o in g.triples((None, pred, None)):
#     print(s, o)