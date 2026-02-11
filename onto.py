from rdflib import Graph, URIRef
from rdflib import Namespace
from owlrl import RDFS_Semantics

# charger ontologie
g = Graph()
g.parse("./turtle/Onto_web.ttl", format="turtle")
ONTO = Namespace("http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/")

# Appliquer le raisonnement RDFS / OWL-RL
rdfs = RDFS_Semantics(g, axioms=True, daxioms=True)
rdfs.closure()  # enrichit le graphe avec l'inférence



def search_pokemon(q: str = ""):

    q = q.replace('"', '').strip()

    query = f"""
    PREFIX : <{str(ONTO)}>

    SELECT ?pokemon ?nom ?url_img ?type ?type_img
    WHERE {{
        ?pokemon a :Pokemon ;
                 :nom ?nom .
        OPTIONAL {{ ?pokemon :url_img ?url_img . }}

        OPTIONAL {{
            ?pokemon :Pokemon_IsTypeOf ?type .
            OPTIONAL {{ ?type :url_img ?type_img . }}
        }}

        FILTER(CONTAINS(LCASE(STR(?nom)), LCASE("{q}")))
    }}
    """

    # dictionnaire pour fusionner les lignes d'un même Pokémon
    results = {}
    for row in g.query(query):
        key = str(row.nom)
        if key not in results:
            results[key] = {
                "name": key,
                "img": str(row.url_img) if row.url_img else "https://picsum.photos/80",
                "types": []
            }

        # ajoute le type et son image
        if row.type:
            results[key]["types"].append({
                "type_name": str(row.type).split("#")[-1],
                "type_img": str(row.type_img) if row.type_img else "https://picsum.photos/40"
            })

    res = list(results.values())
    if len(res) > 10:    
        res = res[:10]

    return res


def pokemon_page(pokemon_name = "alcremie-gmax"):

    pokemon_name_clean = pokemon_name.strip()
    prefix = f"PREFIX : <{str(ONTO)}>"

    query = f"""
    {prefix}

    SELECT ?p ?img ?type ?type_img ?egg ?evo
           ?pv ?atk ?defense ?spatk ?spdef ?vit
    WHERE {{

        ?p a :Pokemon ;
           :nom "{pokemon_name_clean}" ;
           :url_img ?img .

        OPTIONAL {{ ?p :Pokemon_IsTypeOf ?type .
                   ?type :url_img ?type_img . }}

        OPTIONAL {{ ?p :BelongsToEggGroup ?egg . }}
        OPTIONAL {{ ?p :IsEvolutionOf ?evo . }}

        OPTIONAL {{ ?p :base_PV ?pv . }}
        OPTIONAL {{ ?p :base_Attaque ?atk . }}
        OPTIONAL {{ ?p :base_Defense ?defense . }}
        OPTIONAL {{ ?p :base_Attaque_Speciale ?spatk . }}
        OPTIONAL {{ ?p :base_Defense_Speciale ?spdef . }}
        OPTIONAL {{ ?p :base_Vitesse ?vit . }}
    }}
    """

    rows = list(g.query(query))

    pokemon = {
        "name": pokemon_name_clean,
        "img": str(rows[0].img),
        "types": [],
        "eggs": [],
        "evo": None,
        "stats": {
            "pv": int(rows[0].pv) if rows[0].pv else 0,
            "atk": int(rows[0].atk) if rows[0].atk else 0,
            "defense": int(rows[0].defense) if rows[0].defense else 0,
            "spatk": int(rows[0].spatk) if rows[0].spatk else 0,
            "spdef": int(rows[0].spdef) if rows[0].spdef else 0,
            "vit": int(rows[0].vit) if rows[0].vit else 0
        }
    }

    for r in rows:
        if r.type_img:
            pokemon["types"].append(str(r.type_img))
        if r.egg:
            pokemon["eggs"].append(str(r.egg))
        if r.evo:
            pokemon["evo"] = str(r.evo)

    breakpoint()

pokemon_page()