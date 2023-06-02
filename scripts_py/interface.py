import streamlit as st
import pickle
import pandas as pd
import numpy as np
import time
from sklearn.decomposition import PCA
import random
from sklearn.cluster import KMeans
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import StandardScaler


def executa_modelo():
    # ============================================================================
    # Operacional
    # ============================================================================
    if tonalidade == "Tonalidade maior":
        ton = 1
    else:
        ton = 0

    genero = {
        "Dark Trap": 1,
        "dnb": 2,
        "Emo": 3,
        "Hiphop": 4,
        "hardstyle": 5,
        "Pop": 6,
        "psytrance": 7,
        "Rap": 8,
        "RnB": 9,
        "techhouse": 10,
        "techno": 11,
        "trance": 12,
        "trap": 13,
        "Trap Metal": 14,
        "Underground Rap": 15,
    }
    colunas = [
        "dancabilidade",
        "energia",
        "nota",
        "volume",
        "tonalidade",
        "letra",
        "acustica",
        "instrumental",
        "ao_vivo",
        "alegre",
        "ritmo",
        "duracao_ms",
        "compasso",
        "genero",
    ]
    valores = [
        [
            dancabilidade,
            energia,
            nota,
            volume,
            ton,
            letra,
            acustica,
            instrumental,
            ao_vivo,
            alegria,
            ritmo,
            random.uniform(25600.00, 913052.00),
            random.uniform(1.0, 5.0),
            genero[option],
        ],
        [
            -0.48,
            1.1,
            -0.26,
            -0.58,
            0.72,
            -1.1,
            0.22,
            0.93,
            -1.42,
            -0.61,
            1.44,
            1.6,
            1.15,
            0.00,
        ],
    ]

    # Dados novos
    new_data = pd.DataFrame(valores, columns=colunas)

    with st.spinner("Loading..."):
        # ================================================================
        # Carregar o modelo
        # ================================================================
        df_raw = pd.read_csv("../dados/spotify.csv", low_memory=False)
        df_raw.drop_duplicates(subset="id", inplace=True)
        df2 = df_raw.copy().reset_index(drop=True)
        df2.columns = [
            "dancabilidade",
            "energia",
            "nota",
            "volume",
            "tonalidade",
            "letra",
            "acustica",
            "instrumental",
            "ao_vivo",
            "alegre",
            "ritmo",
            "tipo",
            "id",
            "uri",
            "track_href",
            "analysis_url",
            "duracao_ms",
            "compasso",
            "genero",
            "nome",
            "desconhecido",
            "compl_genero",
            "artista",
            "musica",
            "album",
        ]
        # Reduzindo tamanho para performance
        for col in df2.select_dtypes(include=["int64"]):
            df2[col] = df2[col].astype("int32")
        for col in df2.select_dtypes(include=["float64"]):
            df2[col] = df2[col].astype("float32")

        genero = {
            "Dark Trap": 1,
            "dnb": 2,
            "Emo": 3,
            "Hiphop": 4,
            "hardstyle": 5,
            "Pop": 6,
            "psytrance": 7,
            "Rap": 8,
            "RnB": 9,
            "techhouse": 10,
            "techno": 11,
            "trance": 12,
            "trap": 13,
            "Trap Metal": 14,
            "Underground Rap": 15,
        }
        df2.genero = df2.genero.map(genero)
        df3 = df2.copy()
        df3.drop(columns=["desconhecido", "tipo", "compl_genero"], inplace=True)
        # Excluindo colunas de identificação
        df_final = df3.drop(
            columns=[
                "id",
                "uri",
                "track_href",
                "analysis_url",
                "nome",
                "artista",
                "musica",
                "album",
            ]
        )

        # processamento das variáveis categóricas
        enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        df_final[["genero"]] = enc.fit_transform(df_final[["genero"]])

        # processamento das variáveis numéricas
        scaler = StandardScaler()
        df_final[
            [
                "dancabilidade",
                "energia",
                "nota",
                "volume",
                "tonalidade",
                "letra",
                "acustica",
                "instrumental",
                "ao_vivo",
                "alegre",
                "ritmo",
                "duracao_ms",
                "compasso",
            ]
        ] = scaler.fit_transform(
            df_final[
                [
                    "dancabilidade",
                    "energia",
                    "nota",
                    "volume",
                    "tonalidade",
                    "letra",
                    "acustica",
                    "instrumental",
                    "ao_vivo",
                    "alegre",
                    "ritmo",
                    "duracao_ms",
                    "compasso",
                ]
            ]
        )
        pca = PCA(2)

        # Usando PCA para reduzir dimensionalidade do dataset
        df_final2 = pca.fit_transform(df_final)
        # modelo final
        result = KMeans(
            n_clusters=9, init="k-means++", max_iter=1000, n_init=9, random_state=42
        )

        result.fit(df_final2)

        label = result.labels_
        df3["kmeans_cluster"] = label

        # Resultado do modelo no dado novo
        resultado = result.predict(pca.fit_transform(new_data))
        # st.write(resultado[0])

        # Carregando a lista de músicas
        df = pd.read_csv("../notebooks/lista_musicas.csv")
        st.dataframe(
            df[df.kmeans_cluster == resultado[0]]
            .drop(columns=["kmeans_cluster"])
            .sample(3)
            .reset_index(drop=True)
        )

        st.success("Done!")


# ============================================================================
# Barra lateral
# ============================================================================
with st.sidebar:
    st.write(
        "Preencha os parâmetros abaixo de acordo com seu gosto musical e clique no botão:"
    )

    # Selectbox
    option = st.selectbox(
        "Gênero:",
        (
            "Dark Trap",
            "dnb",
            "Emo",
            "Hiphop",
            "hardstyle",
            "Pop",
            "psytrance",
            "Rap",
            "RnB",
            "techhouse",
            "techno",
            "trance",
            "trap",
            "Trap Metal",
            "Underground Rap",
        ),
    )

    # slider
    dancabilidade = st.slider("Dançabilidade", 0.07, 0.99, 0.29)
    energia = st.slider("Energia", 0.0, 1.0, 0.3)
    nota = st.slider("Nota", 3.6, 11.0, 10.0)
    volume = st.slider("Volume", -33, 3, -3)
    letra = st.slider("Letra", 0.0, 1.0, 0.73)
    acustica = st.slider("acustica", 0.0, 1.0, 0.34)
    instrumental = st.slider("Instrumental", 0.0, 1.0, 0.4)
    ao_vivo = st.slider("Ao vivo", 0.0, 1.0, 0.34)
    alegria = st.slider("Alegria", 0.0, 1.0, 0.53)
    ritmo = st.slider("Ritmo", 57, 220, 92)

    # Radio button
    tonalidade = st.radio(
        "Escolha a tonalidade:", ("Tonalidade maior", "Tonalidade menor")
    )


# ============================================================================
# Body
# ============================================================================
st.title("Sistema de recomendação de músicas usando dados do :green[Spotify] :notes:")
st.write("------------------------------------------------")

st.title("Projeto Integrador IV")
st.write("UNIVESP - Mauá.")
st.write("Trabalho semestral desenvolvido por Leonardo Silva Francisco.")
st.write(
    "Sistema de recomendação de músicas utilizando algoritmo de Machine Learning KMeans e interface web usando framework python Streamlit."
)
st.write("------------------------------------------------")


st.write("Configure os controles na barra lateral e clique no botão abaixo:")
st.write("")
if st.button("Encontrar músicas"):
    executa_modelo()
