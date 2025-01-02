import pickle

# Path ke file model
model_path = "model_random_forest.pkl"

# Membuka file model
with open(model_path, "rb") as file:
    model_data = pickle.load(file)

# Menampilkan isi file model
print("Isi file model:", model_data)
print(model_data['model'])  # Menampilkan informasi tentang model
print(model_data['features'])  # Menampilkan fitur penting
