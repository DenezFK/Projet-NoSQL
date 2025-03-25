import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Connexion à MongoDB
client = MongoClient("mongodb+srv://mathis:HDazs1xt6hW6tcFS@projetnosql.3msce.mongodb.net/?retryWrites=true&w=majority&appName=ProjetNoSQL")
db = client["projet"]  # Nom de la base de données
collection = db["movies"]  # Collection contenant les films

# Fonction pour charger les données sous forme de DataFrame 
def load_data():
    data = list(collection.find({}, {"_id": 1, "title": 1, "genre": 1, "year": 1, "rating": 1, "Metascore": 1}))
    return pd.DataFrame(data)

st.title("🎬 Gestion des Films - NoSQL (MongoDB)")

# 📊 Affichage des films actuels
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
    actors = st.text_area("Acteurs")
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
        st.success(f"Film '{title}' ajouté ✅")
        st.experimental_rerun()

# 📌 Formulaire pour mettre à jour un film
st.subheader("✏️ Mettre à jour un Film")
with st.form("update_form"):
    update_id = st.text_input("ID du Film à modifier")
    new_title = st.text_input("Nouveau Titre")
    new_genre = st.text_input("Nouveau Genre")
    submit_update = st.form_submit_button("Mettre à jour")

    if submit_update and update_id:
        update_fields = {}
        if new_title:
            update_fields["title"] = new_title
        if new_genre:
            update_fields["genre"] = new_genre

        if update_fields:
            result = collection.update_one({"_id": update_id}, {"$set": update_fields})
            if result.modified_count > 0:
                st.success("Film mis à jour ✅")
            else:
                st.warning("Aucun film correspondant trouvé ❌")
            st.experimental_rerun()

# 📌 Formulaire pour supprimer un film
st.subheader("🗑️ Supprimer un Film")
with st.form("delete_form"):
    delete_id = st.text_input("ID du Film à supprimer")
    submit_delete = st.form_submit_button("Supprimer")

    if submit_delete and delete_id:
        result = collection.delete_one({"_id": delete_id})
        if result.deleted_count > 0:
            st.success("Film supprimé ✅")
        else:
            st.warning("Aucun film trouvé ❌")
        st.experimental_rerun()
