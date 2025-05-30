# main.py

import streamlit as st
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from deep_translator import GoogleTranslator
from wordcloud import WordCloud
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')

st.title("Avaliação de Atendimento")
st.write("Insira um texto em português ou envie um CSV para análise em lote.")

text = st.text_area("Texto manual:")

csv_file = st.file_uploader("Ou envie um arquivo CSV com a coluna 'Tweet'", type=["csv"])

if st.button("Analisar"):
    sid = SentimentIntensityAnalyzer()

    def classificar_sentimento(texto):
        try:
            traduzido = GoogleTranslator(source='auto', target='en').translate(texto)
            score = sid.polarity_scores(traduzido)
            if score['compound'] >= 0.05:
                return 'Positivo'
            elif score['compound'] <= -0.05:
                return 'Negativo'
            else:
                return 'Neutro'
        except:
            return 'Erro'

    if text.strip():
        resultado = classificar_sentimento(text)
        st.subheader("Resultado da Análise de Sentimento:")
        st.write(f"Sentimento: {resultado}")

    if csv_file:
        try:
            df = pd.read_csv(csv_file)
            if 'Tweet' not in df.columns:
                st.error("CSV precisa conter uma coluna chamada 'Tweet'")
            else:
                df['Sentimento'] = df['Tweet'].astype(str).apply(classificar_sentimento)

                st.subheader("Resultado por Linha:")
                st.dataframe(df[['Tweet', 'Sentimento']])

                st.subheader("Distribuição de Sentimentos:")
                contagem = df['Sentimento'].value_counts()
                fig, ax = plt.subplots()
                ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Erro ao processar CSV: {e}")
