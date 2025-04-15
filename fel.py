import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# ---------------- Configuración del navegador ----------------
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# ---------------- Función de extracción ----------------
def extract_info(url):
    driver = get_driver()
    driver.get(url)
    time.sleep(3)  # Esperar a que cargue el contenido
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    productos = soup.find_all("b", {"class": "jsx-2325455629 title1 secondary jsx-3451706699 bold pod-title title-rebrand"})
    marcas = soup.find_all("b", {"class": "jsx-2325455629 copy2 primary jsx-3451706699 normal pod-sellerText seller-text-rebrand"})

    productos = [p.text.strip() for p in productos]
    marcas = [m.text.strip() for m in marcas]

    data = [{"Producto": p, "Marca": marcas[i] if i < len(marcas) else ""} for i, p in enumerate(productos)]
    return data

# ---------------- Interfaz Streamlit ----------------
st.title("🛒 Scraper de Falabella con Selenium")

# Inicializar session state para acumular resultados
if "datos_scrapeados" not in st.session_state:
    st.session_state.datos_scrapeados = []

url = st.text_input("🔗 Ingresa URL del sitio de Falabella")

if st.button("📥 Extraer datos"):
    if url:
        resultados = extract_info(url)
        if resultados:
            st.session_state.datos_scrapeados.extend(resultados)
            st.success(f"✅ Se extrajeron {len(resultados)} productos.")
        else:
            st.warning("No se encontraron productos.")

# Mostrar tabla con datos acumulados
if st.session_state.datos_scrapeados:
    df_resultados = pd.DataFrame(st.session_state.datos_scrapeados)
    st.markdown("### 📊 Resultados Acumulados")
    st.dataframe(df_resultados)

    # Botón de descarga
    csv = df_resultados.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", data=csv, file_name="resultados_falabella.csv", mime="text/csv")
else:
    st.info("Todavía no hay datos. Ingresa una URL y extrae información.")

