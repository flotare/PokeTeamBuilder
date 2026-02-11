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

print("Onto chargée")


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

def pokemon_page_bis(pokemon_name = "abomasnow"):
    pokemon_name_clean = pokemon_name.strip()
    prefix = f"PREFIX : <{str(ONTO)}>"

    # --- 1. Infos de base du Pokémon ---
    query_base = f"""
    {prefix}
    SELECT ?img ?pv ?atk ?defense ?spatk ?spdef ?vit
    WHERE {{
        ?p a :Pokemon ;
           :nom "{pokemon_name_clean}" ;
           :url_img ?img .
        OPTIONAL {{ ?p :base_PV ?pv }} .
        OPTIONAL {{ ?p :base_Attaque ?atk }} .
        OPTIONAL {{ ?p :base_Defense ?defense }} .
        OPTIONAL {{ ?p :base_Attaque_Speciale ?spatk }} .
        OPTIONAL {{ ?p :base_Defense_Speciale ?spdef }} .
        OPTIONAL {{ ?p :base_Vitesse ?vit }} .
    }}
    """
    rows_base = list(g.query(query_base))


    row = rows_base[0]
    pokemon = {
        "name": pokemon_name_clean,
        "img": str(row.img),
        "stats": {
            "pv": int(row.pv) if row.pv else 0,
            "atk": int(row.atk) if row.atk else 0,
            "defense": int(row.defense) if row.defense else 0,
            "spatk": int(row.spatk) if row.spatk else 0,
            "spdef": int(row.spdef) if row.spdef else 0,
            "vit": int(row.vit) if row.vit else 0
        }
    }

    # --- 2. Types du Pokémon ---
    query_types = f"""
    {prefix}
    SELECT ?img
    WHERE {{
        ?p a :Pokemon ;
           :nom "{pokemon_name_clean}" ;
           :Pokemon_IsTypeOf ?type .
        ?type :url_img ?img  .
    }}
    """
    rows_types = list(g.query(query_types))
    pokemon["types"] = []
    for r in rows_types:
        pokemon["types"].append({
            "img": str(r.img)
        })

    # --- 3. Groupes d'œufs ---
    query_eggs = f"""
    {prefix}
    SELECT ?egg ?egg_name
    WHERE {{
        ?p a :Pokemon ;
           :nom "{pokemon_name_clean}" ;
           :BelongsToEggGroup ?egg .
        OPTIONAL {{ ?egg :nom ?egg_name }}
    }}
    """
    rows_eggs = list(g.query(query_eggs))
    pokemon["eggs"] = [{"uri": str(r.egg), 
                        "name": str(r.egg_name) if r.egg_name else None} for r in rows_eggs]

    # --- 4. Évolution ---
    query_evo = f"""
    {prefix}
    SELECT ?evo
    WHERE {{
        ?p a :Pokemon ;
           :nom "{pokemon_name_clean}" ;
           :EvolvesTo ?evo .
    }}
    """
    rows_evo = list(g.query(query_evo))
    pokemon["evo"] = [str(r.evo) for r in rows_evo] if rows_evo else []

    # --- 5. Capacités / Moves ---
    query_moves = f"""
    {prefix}
    SELECT ?move ?categorie ?move_name ?type ?puissance ?precision ?pp ?priorite
    WHERE {{
        ?p a :Pokemon ;
           :nom "{pokemon_name_clean}" ;
           :hasForCapaciteLearnable ?move .
        ?move a ?categorie ;
              :nom ?move_name .
        OPTIONAL {{ ?move :Capacite_IsTypeOf ?type }}
        OPTIONAL {{ ?move :puissance_capacite ?puissance }}
        OPTIONAL {{ ?move :precision_capacite ?precision }}
        OPTIONAL {{ ?move :pp_capacite ?pp }}
        OPTIONAL {{ ?move :priorite_capacite ?priorite }}
    }}
    """
    rows_moves = list(g.query(query_moves))
    
    # --- 6. Capacités / Types
    query_moves_types = f"""
    {prefix}
    SELECT ?type_img ?type_uri
    WHERE {{
        ?type_uri a :Type_pokemon ;
            :url_img ?type_img .
    }}
    
    """
    rows_moves_types = list(g.query(query_moves_types))
    types = {}
    for r in rows_moves_types:
        types[str(r.type_uri)] = str(r.type_img)
    
    
    # Filter capacités
    print("filtering")
    rows_moves_2 = []
    for r in rows_moves:
        if str(r.categorie) in ['http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_physique',
                                'http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_speciale',
                                'http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_statut']:
            rows_moves_2.append(r)
    
    pokemon["moves"] = []
    for r in rows_moves_2:
        pokemon["moves"].append({
            "uri": str(r.move),
            "name": str(r.move_name),
            "category": str(r.categorie).split("#")[-1] if r.categorie else None,
            "type_img": types[str(r.type)] if r.type else None,
            "power": int(r.puissance) if r.puissance else None,
            "accuracy": int(r.precision) if r.precision else None,
            "pp": int(r.pp) if r.pp else None,
            "priority": int(r.priorite) if r.priorite else 0,
        })
    
    breakpoint()

pokemon_page_bis()