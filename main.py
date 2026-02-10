from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rdflib import Graph
from rdflib.namespace import RDFS
from rdflib import Namespace

from owlrl import RDFS_Semantics

from fastapi.middleware.cors import CORSMiddleware

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

    SELECT ?pokemon ?nom
    WHERE {{
        ?pokemon a :Pokemon ;
                 :nom ?nom .
        FILTER(CONTAINS(LCASE(STR(?nom)), LCASE("{q}")))
    }}
    LIMIT 10
    """

    results = []

    for row in g.query(query):
        results.append({
            "name": str(row.nom),
            "img1": "https://picsum.photos/80",
            "img2": "https://picsum.photos/81"
        })

    return results


@app.get("/search/objet")
def search_objet(q: str = ""):

    prefix = f"PREFIX : <{str(ONTO)}>"

    q = q.replace('"', '').strip()

    query = f"""
    {prefix}

    SELECT ?entity ?nom
    WHERE {{
        ?entity a :Objet ;
                :nom ?nom .
        FILTER(REGEX(STR(?nom), "{q}", "i"))
    }}
    LIMIT 10
    """

    results = []

    for row in g.query(query):
        results.append({
            "name": str(row.nom),
            "img1": "https://picsum.photos/80",
            "img2": "https://picsum.photos/81"
        })

    return results



# Endpoint dynamique par Pokémon
@app.get("/pokemon/{pokemon_name}", response_class=HTMLResponse)
def pokemon_page(request: Request, pokemon_name: str):
    pokemon_name_clean = pokemon_name.strip()
    prefix = f"PREFIX : <{str(ONTO)}>"

    query = f"""
    {prefix}
    SELECT ?prop ?val
    WHERE {{
        ?p a :Pokemon ;
           :nom "{pokemon_name_clean}" .
        ?p ?prop ?val .
    }}
    """

    results = []
    for row in g.query(query):
        prop = str(row.prop)
        val = str(row.val)
        results.append((prop, val))

    if not results:
        raise HTTPException(status_code=404, detail="Pokémon non trouvé")

    # passe les résultats au template HTML
    return templates.TemplateResponse("pokemon.html", {
        "request": request,
        "pokemon_name": pokemon_name_clean,
        "results": results
    })