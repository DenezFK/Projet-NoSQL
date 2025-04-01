import streamlit as st
from pymongo import MongoClient
from neo4j import GraphDatabase
import pandas as pd

# Connexion à MongoDB
client = MongoClient("mongodb+srv://mathis:HDazs1xt6hW6tcFS@projetnosql.3msce.mongodb.net/?retryWrites=true&w=majority&appName=ProjetNoSQL")
db = client["projet"]
collection = db["movies"]

def load_data():
    data = list(collection.find({}, {"_id": 1, "title": 1, "genre": 1, "year": 1, "rating": 1, "Metascore": 1}))
    return pd.DataFrame(data)

st.title("🎬 Gestion des Films - NoSQL")

# 📊 Affichage des films actuels dans MongoDB
st.subheader("📋 Liste des Films (MongoDB)")
df = load_data()
st.dataframe(df)

# Connexion à Neo4j
NEO4J_URI = "neo4j+s://6b909039.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "n8x5MbiTrvmLCG3aywCNJ-10rDhcPYbs_PRzdNqx5_s"

def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_query(query, parameters=None):
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]

st.subheader("🎭 Films enregistrés dans Neo4j")
query = "MATCH (m:Movie) RETURN m.title AS title, m.genre AS genre, m.year AS year LIMIT 10"
data = run_query(query)

df = pd.DataFrame(data)
st.dataframe(df)

# 📌 Ajouter un film dans MongoDB
st.subheader("➕ Ajouter un Film (MongoDB)")
with st.form("insert_form_mongo"):
    col1, col2 = st.columns(2)
    with col1:
        movie_id = st.text_input("ID du Film (unique)")
        title = st.text_input("Titre")
        genre = st.text_input("Genre")
    with col2:
        year = st.number_input("Année", min_value=1900, max_value=2100, step=1)
        rating = st.text_input("Classification (Ex: PG, G)")
        metascore = st.slider("Metascore", 0, 100, 50)

    submit_insert = st.form_submit_button("Ajouter")
    if submit_insert and movie_id and title:
        collection.insert_one({
            "_id": movie_id,
            "title": title,
            "genre": genre,
            "year": year,
            "rating": rating,
            "Metascore": metascore
        })
        st.success(f"Film '{title}' ajouté ✅")
        st.experimental_rerun()

# 📌 Ajouter un film dans Neo4j
st.subheader("➕ Ajouter un Film (Neo4j)")
with st.form("insert_form_neo4j"):
    title = st.text_input("Titre")
    genre = st.text_input("Genre")
    year = st.number_input("Année", min_value=1900, max_value=2100, step=1)
    submit_insert = st.form_submit_button("Ajouter")
    
    if submit_insert and title:
        query = "CREATE (m:Movie {title: $title, genre: $genre, year: $year})"
        run_query(query, {"title": title, "genre": genre, "year": year})
        st.success(f"Film '{title}' ajouté ✅")
        st.experimental_rerun()

# 📌 Mise à jour d'un film dans Neo4j
st.subheader("✏️ Mettre à jour un Film (Neo4j)")
with st.form("update_form_neo4j"):
    old_title = st.text_input("Titre du Film à modifier")
    new_genre = st.text_input("Nouveau Genre")
    new_year = st.number_input("Nouvelle Année", min_value=1900, max_value=2100, step=1)
    submit_update = st.form_submit_button("Mettre à jour")
    
    if submit_update and old_title:
        query = "MATCH (m:Movie {title: $old_title}) SET m.genre = $new_genre, m.year = $new_year"
        run_query(query, {"old_title": old_title, "new_genre": new_genre, "new_year": new_year})
        st.success("Film mis à jour ✅")
        st.experimental_rerun()

# 📌 Supprimer un film dans Neo4j
st.subheader("🗑️ Supprimer un Film (Neo4j)")
with st.form("delete_form_neo4j"):
    delete_title = st.text_input("Titre du Film à supprimer")
    submit_delete = st.form_submit_button("Supprimer")
    
    if submit_delete and delete_title:
        query = "MATCH (m:Movie {title: $delete_title}) DETACH DELETE m"
        run_query(query, {"delete_title": delete_title})
        st.success("Film supprimé ✅")
        st.experimental_rerun()
