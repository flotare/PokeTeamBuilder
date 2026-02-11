from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rdflib import Graph
from rdflib.namespace import RDFS
from rdflib import Namespace

from owlrl import RDFS_Semantics

from fastapi.middleware.cors import CORSMiddleware

import time as t

app = FastAPI()

# autorise JS local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# charger ontologie
g = Graph()
g.parse("./turtle/Onto_web.ttl", format="turtle")
ONTO = Namespace("http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/")

# Appliquer le raisonnement RDFS / OWL-RL
rdfs = RDFS_Semantics(g, axioms=True, daxioms=True)
rdfs.closure()  # enrichit le graphe avec l'inférence


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# print("=== TEST NOM ===")
# for s, p, o in g:
#     if "nom" in str(p):
#         print(s, p, o)




@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search/pokemon")
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
                "img": str(row.url_img) if row.url_img else None,
                "types": []
            }

        # ajoute le type et son image
        results[key]["types"].append({
            "type_name": str(row.type).split("#")[-1],
            "type_img": str(row.type_img) if row.type_img else None
        })

    res = list(results.values())
    res = sorted(res, 
        key=lambda poke_dict: 
            (not poke_dict["name"].startswith(q.lower()) , poke_dict["name"])
    )

    return res[:10]


@app.get("/search/objet")
def search_objet(q: str = ""):

    prefix = f"PREFIX : <{str(ONTO)}>"

    q = q.replace('"', '').strip()

    query = f"""
    {prefix}

    SELECT ?entity ?nom ?url_img
    WHERE {{
        ?entity a :Objet ;
                :nom ?nom ;
                :url_img ?url_img.
        FILTER(REGEX(STR(?nom), "{q}", "i"))
    }}
    """

    results = []

    for row in g.query(query):
        results.append({
            "name": str(row.nom),
            "img": str(row.url_img),
        })
    
    sorted_result = sorted(
        results,
        key=lambda item: (
            not item["name"].lower().startswith(q.lower()),
            item["name"].lower()
        )
    )
        
        
    return sorted_result



# @app.get("/pokemon/{pokemon_name}", response_class=HTMLResponse)
# def pokemon_page(request: Request, pokemon_name: str):

#     pokemon_name_clean = pokemon_name.strip()
#     prefix = f"PREFIX : <{str(ONTO)}>"

#     query = f"""
#     {prefix}

#     SELECT ?p ?img ?type ?type_img ?egg ?evo
#            ?pv ?atk ?defense ?spatk ?spdef ?vit
#     WHERE {{

#         ?p a :Pokemon ;
#            :nom "{pokemon_name_clean}" ;
#            :url_img ?img .

#         OPTIONAL {{ ?p :Pokemon_IsTypeOf ?type .
#                    ?type :url_img ?type_img . }}

#         OPTIONAL {{ ?p :BelongsToEggGroup ?egg . }}
#         OPTIONAL {{ ?p :IsEvolutionOf ?evo . }}

#         OPTIONAL {{ ?p :base_PV ?pv . }}
#         OPTIONAL {{ ?p :base_Attaque ?atk . }}
#         OPTIONAL {{ ?p :base_Defense ?defense . }}
#         OPTIONAL {{ ?p :base_Attaque_Speciale ?spatk . }}
#         OPTIONAL {{ ?p :base_Defense_Speciale ?spdef . }}
#         OPTIONAL {{ ?p :base_Vitesse ?vit . }}
#     }}
#     """

#     rows = list(g.query(query))

#     if not rows:
#         raise HTTPException(status_code=404, detail="Pokémon non trouvé")

#     pokemon = {
#         "name": pokemon_name_clean,
#         "img": str(rows[0].img),
#         "types": [],
#         "eggs": [],
#         "evo": None,
#         "stats": {
#             "pv": int(rows[0].pv) if rows[0].pv else 0,
#             "atk": int(rows[0].atk) if rows[0].atk else 0,
#             "defense": int(rows[0].defense) if rows[0].defense else 0,
#             "spatk": int(rows[0].spatk) if rows[0].spatk else 0,
#             "spdef": int(rows[0].spdef) if rows[0].spdef else 0,
#             "vit": int(rows[0].vit) if rows[0].vit else 0
#         }
#     }

#     for r in rows:
#         if r.type_img and str(r.type_img) not in pokemon["types"]:
#             pokemon["types"].append(str(r.type_img))
#         if r.egg and str(r.egg) not in pokemon["eggs"]:
#             pokemon["eggs"].append(str(r.egg))
#         print(r.evo)
#         if r.evo and pokemon["evo"] is not None and str(r.evo) not in pokemon["evo"]:
#             pokemon["evo"] = str(r.evo)

#     return templates.TemplateResponse("pokemon.html", {
#         "request": request,
#         "pokemon": pokemon
#     })


@app.get("/objet/{item_name}", response_class=HTMLResponse)
def item_page(request: Request, item_name: str):

    item_name_clean = item_name.strip()
    prefix = f"PREFIX : <{str(ONTO)}>"

    query = f"""
    {prefix}
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?item ?nom ?img ?effect ?type
    WHERE {{
        ?item :nom "{item_name}" ;
              :nom ?nom ;
              :url_img ?img ;
              :effect_name ?effect ;
              rdf:type ?type .

        FILTER(?type != owl:NamedIndividual)
    }}
    LIMIT 1
    """

    rows = list(g.query(query))

    if not rows:
        raise HTTPException(status_code=404, detail="Objet non trouvé")

    row = rows[0]

    item_data = {
        "name": str(row.nom),
        "img": str(row.img),
        "effect": str(row.effect),
        "type": str(row.type).split("/")[-1]
    }
    
    print(item_data)

    return templates.TemplateResponse(
        "item.html",
        {
            "request": request,
            "item": item_data
        }
    )




@app.get("/pokemon/{pokemon_name}", response_class=HTMLResponse)
def pokemon_page(request: Request, pokemon_name: str):
    
    t0 = t.time()
    
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
    SELECT ?evo ?preevo ?desc
    WHERE {{
        ?p a :Pokemon ;
           :nom "{pokemon_name_clean}" ;
           :descriptionEvolution ?desc
           OPTIONAL {{ ?p :EvolvesTo ?evo . }}
           OPTIONAL {{ ?p :IsEvolutionOf ?preevo . }}
           
    }}
    """
    rows_evo = list(g.query(query_evo))
    pokemon["evo"] = [
        str(r.evo).split('/')[-1]
        for r in rows_evo
        if r.evo
    ]

    pokemon["preevo"] = [
        str(r.preevo).split('/')[-1]
        for r in rows_evo
        if r.preevo
    ]
    
    pokemon["evodesc"] = [
        str(r.desc) for r in rows_evo if r.desc
    ]


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
    rows_moves_2 = []
    for r in rows_moves:
        if str(r.categorie) in ['http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_physique',
                                'http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_speciale',
                                'http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_statut']:
            rows_moves_2.append(r)
    
    image_capacite = {
        'http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_physique' : 'https://www.pokepedia.fr/images/1/1f/Miniature_Cat%C3%A9gorie_Physique_HOME.png',
        'http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_speciale' : 'https://www.pokepedia.fr/images/2/26/Miniature_Cat%C3%A9gorie_Sp%C3%A9ciale_HOME.png',
        'http://www.semanticweb.org/arthu/ontologies/2026/0/OntoPokemon/Capacite_statut'   : 'https://www.pokepedia.fr/images/8/8a/Miniature_Cat%C3%A9gorie_Statut_HOME.png'
    }
    

    
    pokemon["moves"] = []
    for r in rows_moves_2:
        pokemon["moves"].append({
            "uri": str(r.move),
            "name": str(r.move_name),
            "category": image_capacite[str(r.categorie)] if r.categorie else None,
            "type_img": types[str(r.type)] if r.type else None,
            "power": int(r.puissance) if r.puissance else None,
            "accuracy": int(r.precision) if r.precision else None,
            "pp": int(r.pp) if r.pp else None,
            "priority": int(r.priorite) if r.priorite else 0,
        })

    tf = t.time() - t0
    print(f"requête effectuée en {tf}s")

    return templates.TemplateResponse("pokemon.html", {
        "request": request,
        "pokemon": pokemon
    })
