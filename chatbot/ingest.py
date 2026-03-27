from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import chromadb
from chromadb.utils import embedding_functions


df = pd.read_csv("data/Video_Games.csv")
df = df.fillna("Unknown")
# convert year to int then back to string, replace 0 with N/A for display
df["Year_of_Release"] = df["Year_of_Release"].replace({"": "0", "Unknown": "0"}).astype(float).astype(int).astype(str).replace("0", "N/A")


client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# drop existing collection so we don't get duplicate records on re-run
try:
    client.delete_collection("vgsales")
except:
    pass
collection = client.get_or_create_collection("vgsales", embedding_function=ef)


documents, ids = [], []
for i, row in df.iterrows():
    # build a natural language string so semantic search works well
    doc = (
        f"{row['Name']} was released on {row['Platform']} in {row['Year_of_Release']}. "
        f"Genre: {row['Genre']}. Publisher: {row['Publisher']}. "
        f"Developer: {row['Developer']}. "
        f"Global sales: {row['Global_Sales']} million copies. "
        f"NA sales: {row['NA_Sales']}M, EU sales: {row['EU_Sales']}M, JP sales: {row['JP_Sales']}M. "
        f"Critic score: {row['Critic_Score']}, User score: {row['User_Score']}. "
        f"Rating: {row['Rating']}."
    )
    documents.append(doc)
    ids.append(str(i))


# batch to avoid memory issues with large datasets
batch_size = 5000
for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    collection.add(documents=batch_docs, ids=batch_ids)
    print(f"Ingested batch {i//batch_size + 1} ({len(batch_docs)} records)")


print(f"Successfully ingested {len(documents)} total records into ChromaDB.")