import streamlit as st
from pymongo import MongoClient
import pandas as pd
from neo4j import GraphDatabase

# Connexion à MongoDB
client = MongoClient("mongodb+srv://mathis:HDazs1xt6hW6tcFS@projetnosql.3msce.mongodb.net/?retryWrites=true&w=majority&appName=ProjetNoSQL")
db = client["projet"]
collection = db["movies"]

# Connexion à Neo4j
NEO4J_URI = "neo4j+s://6b909039.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "n8x5MbiTrvmLCG3aywCNJ-10rDhcPYbs_PRzdNqx5_s"

neo4j_conn = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Charger les données depuis MongoDB
def load_data():
    data = list(collection.find({}, {"_id": 1, "title": 1, "genre": 1, "year": 1, "rating": 1, "Votes": 1, "Revenue (Millions)": 1, "Director": 1, "Actors": 1}))
    return pd.DataFrame(data)

# Ajouter un film et ses relations dans Neo4j
def add_movie_to_neo4j(movie_id, title, year, votes, revenue, rating, director, actors):
    with neo4j_conn.session() as session:
        session.run("""
            MERGE (m:Movie {_id: $movie_id})
            SET m.title = $title, m.year = $year, m.votes = $votes, m.revenue = $revenue, m.rating = $rating
        """, movie_id=movie_id, title=title, year=year, votes=votes, revenue=revenue, rating=rating)
        
        session.run("""
            MERGE (d:Director {name: $director})
            MERGE (d)-[:A_REALISE]->(m)
        """, director=director)

        for actor in actors.split(","):
            actor = actor.strip()
            session.run("""
                MERGE (a:Actor {name: $actor})
                MERGE (a)-[:A_JOUE]->(m)
            """, actor=actor)

# Interface Streamlit
st.title("🎬 Gestion des Films - NoSQL (MongoDB & Neo4j)")

# 📊 Affichage des films
st.subheader("📋 Liste des Films")
df = load_data()
st.dataframe(df)

# 📌 Formulaire pour ajouter un film
st.subheader("➕ Ajouter un Film")
with st.form("insert_form"):
    col1, col2 = st.columns(2)
    with col1:
        movie_id = st.text_input("ID du Film (unique)")
        title = st.text_input("Titre")
        genre = st.text_input("Genre")
        director = st.text_input("Réalisateur")
    with col2:
        year = st.number_input("Année", min_value=1900, max_value=2100, step=1)
        rating = st.text_input("Classification (Ex: PG, G)")
        votes = st.number_input("Nombre de Votes", min_value=0, step=1)
        revenue = st.number_input("Revenu (Millions)", min_value=0.0, step=0.1)

    description = st.text_area("Description")
    actors = st.text_area("Acteurs (séparés par des virgules)")
    metascore = st.slider("Metascore", 0, 100, 50)

    submit_insert = st.form_submit_button("Ajouter")
    if submit_insert and movie_id and title:
        collection.insert_one({
            "_id": movie_id,
            "title": title,
            "genre": genre,
            "Director": director,
            "year": year,
            "rating": rating,
            "Votes": votes,
            "Revenue (Millions)": revenue,
            "Description": description,
            "Actors": actors,
            "Metascore": metascore
        })

        add_movie_to_neo4j(movie_id, title, year, votes, revenue, rating, director, actors)
        
        st.success(f"Film '{title}' ajouté à MongoDB et Neo4j ✅")
        st.experimental_rerun()

# 📌 Requêtes Neo4j : Trouver les films d'un acteur
st.subheader("🔎 Trouver les films d'un acteur")
actor_search = st.text_input("Nom de l'acteur")
if st.button("Rechercher"):
    with neo4j_conn.session() as session:
        result = session.run("""
            MATCH (a:Actor {name: $actor})-[:A_JOUE]->(m:Movie)
            RETURN m.title
        """, actor=actor_search)
        
        films = [record["m.title"] for record in result]
        if films:
            st.write(f"📽️ Films avec {actor_search}: {', '.join(films)}")
        else:
            st.warning(f"Aucun film trouvé pour {actor_search}.")

# 📌 Requêtes Neo4j : Trouver les réalisateurs d'un film
st.subheader("🎬 Trouver le réalisateur d'un film")
movie_search = st.text_input("Titre du film")
if st.button("Chercher Réalisateur"):
    with neo4j_conn.session() as session:
        result = session.run("""
            MATCH (d:Director)-[:A_REALISE]->(m:Movie {title: $title})
            RETURN d.name
        """, title=movie_search)
        
        directors = [record["d.name"] for record in result]
        if directors:
            st.write(f"🎬 Réalisateur de {movie_search}: {', '.join(directors)}")
        else:
            st.warning(f"Aucun réalisateur trouvé pour {movie_search}.")

# 📌 Requêtes Neo4j : Trouver les relations entre acteurs
st.subheader("🎭 Relations entre acteurs")
actor1 = st.text_input("Acteur 1")
actor2 = st.text_input("Acteur 2")
if st.button("Trouver un lien"):
    with neo4j_conn.session() as session:
        result = session.run("""
            MATCH path=shortestPath((a1:Actor {name: $actor1})-[:A_JOUE*]-(a2:Actor {name: $actor2}))
            RETURN path
        """, actor1=actor1, actor2=actor2)

        if result.single():
            st.success(f"🎭 Il existe une connexion entre {actor1} et {actor2} via un ou plusieurs films.")
        else:
            st.warning(f"Aucune connexion directe entre {actor1} et {actor2}.")
