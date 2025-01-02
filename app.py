import streamlit as st
import pandas as pd
import numpy as np
import pickle
import cv2
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from fpdf import FPDF

# Fungsi untuk memuat model
def load_model(model_path):
    with open(model_path, 'rb') as file:
        model_data = pickle.load(file)
    return model_data

# Fungsi untuk memproses gambar dan mengekstrak fitur
def preprocess_image_all_features(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Gambar tidak valid atau tidak ditemukan.")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mean_rgb = np.mean(image_rgb, axis=(0, 1))
        mean_hsv = np.mean(image_hsv, axis=(0, 1))
        features = {
            'Red': mean_rgb[0],
            'Green': mean_rgb[1],
            'Blue': mean_rgb[2],
            'Hue': mean_hsv[0],
            'Saturation': mean_hsv[1],
            'Value': mean_hsv[2],
        }
        return features
    except Exception as e:
        st.error(f"Error in preprocess_image_all_features: {e}")
        return None

# Fungsi untuk memprediksi dosis
def predict_dose(image_path, model, significant_features):
    try:
        features = preprocess_image_all_features(image_path)
        if features is None:
            raise ValueError("Fitur gambar tidak valid.")
        selected_features = [features[feature] for feature in significant_features]
        dose = model.predict([selected_features])[0]
        return dose, features
    except Exception as e:
        st.error(f"Error in predict_dose: {e}")
        return None, None

# Fungsi untuk membuat PDF laporan
def generate_pdf(sample_name, dose, features):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Laporan Pembacaan Dosimeter", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Nama Sampel: {sample_name}", ln=True)
    pdf.cell(200, 10, txt=f"Dosis yang Diprediksi: {dose:.2f} Gy", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Fitur Warna:", ln=True)
    for key, value in features.items():
        pdf.cell(200, 10, txt=f"{key}: {value:.2f}", ln=True)
    file_path = "laporan_dosimeter.pdf"
    pdf.output(file_path)
    return file_path

# Fungsi untuk visualisasi analisis fitur
def visualize_features(dataset):
    try:
        features = ['Green', 'Blue', 'Saturation']
        for feature in features:
            x = dataset[feature].values.reshape(-1, 1)
            y = dataset['Dose']

            model = LinearRegression()
            model.fit(x, y)

            plt.figure(figsize=(8, 6))
            plt.scatter(x, y, color='blue', label='Data')
            plt.plot(x, model.predict(x), color='red', label='Regresi Linear')
            plt.title(f"Hubungan {feature} vs Dose")
            plt.xlabel(feature)
            plt.ylabel("Dose (Gy)")
            plt.legend()
            plt.grid()
            st.pyplot(plt)

            r2_score = model.score(x, y)
            slope = model.coef_[0]
            intercept = model.intercept_
            st.write(f"**Feature: {feature}**")
            st.write(f"R-squared: **{r2_score:.2f}**")
            st.write(f"Persamaan Regresi: Dose = {slope:.2f} * {feature} + {intercept:.2f}")
    except Exception as e:
        st.error(f"Error in visualize_features: {e}")

# Fungsi utama aplikasi
def main():
    st.sidebar.title("Menu Navigasi")
    menu = st.sidebar.selectbox("Pilih Menu", ["Beranda", "Unggah Sampel", "Analisis Fitur", "History", "Tentang", "Buat Metode Baru"])

    if menu == "Beranda":
        st.title("Aplikasi Dosimeter Film Reader")
        st.write("Selamat datang di aplikasi Dosimeter Film Reader!")

    elif menu == "Unggah Sampel":
        st.title("Unggah Sampel")
        model_data = load_model("model_random_forest.pkl")
        model = model_data['model']
        significant_features = model_data['features']
        uploaded_file = st.file_uploader("Unggah gambar dosimeter", type=['jpg', 'png'])
        if uploaded_file:
            with open("temp_image.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            dose, features = predict_dose("temp_image.jpg", model, significant_features)
            if dose is not None:
                st.write(f"Dosis yang diprediksi: {dose:.2f} Gy")
                st.write("Fitur warna yang diekstraksi:")
                st.json(features)
                sample_name = st.text_input("Masukkan nama sampel:", value="Sampel 1")
                if st.button("Unduh Laporan PDF"):
                    pdf_path = generate_pdf(sample_name, dose, features)
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="Klik untuk mengunduh laporan",
                            data=pdf_file,
                            file_name="laporan_dosimeter.pdf",
                            mime="application/pdf",
                        )

    elif menu == "Analisis Fitur":
        st.title("Analisis Fitur")
        dataset_path = "dataset_dosimeter.csv"
        try:
            dataset = pd.read_csv(dataset_path)
            st.write("Dataset yang dimuat:")
            st.dataframe(dataset.head())
            visualize_features(dataset)
        except Exception as e:
            st.error(f"Error loading dataset: {e}")

    elif menu == "History":
        st.title("Riwayat Pembacaan")
        history_file = "history.csv"
        if st.button("Muat Riwayat"):
            try:
                history_data = pd.read_csv(history_file)
                st.dataframe(history_data)
            except Exception as e:
                st.error("Belum ada data riwayat yang tersedia.")

    elif menu == "Tentang":
        st.title("Tentang Aplikasi")
        st.write("Aplikasi ini dibuat untuk membaca dosimeter film menggunakan teknologi machine learning.")

    elif menu == "Buat Metode Baru":
        st.title("Buat Metode Baru")
        method_name = st.text_input("Nama Metode")
        scanner_type = st.text_input("Jenis Scanner")
        doses = st.text_input("Masukkan deret dosis (pisahkan dengan koma)", "1,2,3,4,5,6,7,8")

        if st.button("Buat Metode"):
            try:
                dose_list = [float(d) for d in doses.split(",")]
                st.write("Deret dosis berhasil diinput:", dose_list)
                scan_data = []
                for dose in dose_list:
                    st.write(f"Scan untuk dosis {dose} kGy...")
                    dummy_features = {"Red": np.random.uniform(0, 255),
                                      "Green": np.random.uniform(0, 255),
                                      "Blue": np.random.uniform(0, 255),
                                      "Hue": np.random.uniform(0, 180),
                                      "Saturation": np.random.uniform(0, 255),
                                      "Value": np.random.uniform(0, 255)}
                    dummy_features["Dose"] = dose
                    scan_data.append(dummy_features)

                df_scan_data = pd.DataFrame(scan_data)
                file_path = f"dataset_{method_name.lower().replace(' ', '_')}.csv"
                df_scan_data.to_csv(file_path, index=False)
                st.write(f"Data hasil scan disimpan di {file_path}")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
