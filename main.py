import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
import string
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from textblob import TextBlob

# Configuração de estilo
plt.style.use('default')
sns.set_palette("pastel")
nltk.download(['vader_lexicon', 'stopwords', 'punkt'])

# Função de limpeza de texto aprimorada
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text

# Carregar e preparar dados
url = "https://raw.githubusercontent.com/amankharwal/Website-data/master/twitter.csv"
data = pd.read_csv(url)
data = data.sample(frac=0.1, random_state=42)  # Amostra para desempenho
data['tweet'] = data['tweet'].apply(clean_text)

# Análise de Sentimento
sia = SentimentIntensityAnalyzer()
stopwords_set = set(stopwords.words('english'))

def get_sentiment_scores(text):
    scores = sia.polarity_scores(text)
    return scores['compound'], scores['pos'], scores['neg'], scores['neu']

data[['Compound', 'Positive', 'Negative', 'Neutral']] = data['tweet'].apply(
    lambda x: pd.Series(get_sentiment_scores(x))
)

# Classificação de sentimento
data['Sentimento'] = data['Compound'].apply(
    lambda x: 'Positivo' if x >= 0.05 else ('Negativo' if x <= -0.05 else 'Neutro')
)

# Gerar relatório
def generate_report(df):
    report = []
    
    # 1. Estatísticas básicas
    sentiment_counts = df['Sentimento'].value_counts()
    report.append("## Análise de Sentimento de Tweets")
    report.append(f"**Total de Tweets:** {len(df)}")
    report.append(f"**Distribuição:**\n{sentiment_counts.to_markdown()}")
    
    # 2. Médias de sentimentos
    avg_scores = df[['Positive', 'Negative', 'Neutral']].mean().to_frame('Média')
    report.append("\n### Médias de Sentimentos")
    report.append(avg_scores.to_markdown())
    
    return "\n\n".join(report)

# Salvar resultados
data.to_csv("sentiment_analysis.csv", index=False)
with open("relatorio_sentimentos.md", "w", encoding="utf-8") as f:
    f.write(generate_report(data))

# Visualizações
def create_visualizations(df):
    fig, axs = plt.subplots(2, 2, figsize=(18, 14))
    
    # Gráfico 1: Distribuição de Sentimentos
    sentiment_palette = {'Positivo': '#66c2a5', 'Negativo': '#fc8d62', 'Neutro': '#8da0cb'}
    sns.countplot(data=df, x='Sentimento', ax=axs[0,0], palette=sentiment_palette)
    axs[0,0].set_title('Distribuição de Sentimentos', fontsize=14, pad=20)
    axs[0,0].set_ylabel('Contagem', fontsize=12)
    
    # Gráfico 2: Densidade dos Scores
    for sentiment, color in sentiment_palette.items():
        sns.kdeplot(
            df[df['Sentimento'] == sentiment]['Compound'],
            ax=axs[0,1], color=color, fill=True, alpha=0.3, label=sentiment
        )
    axs[0,1].set_title('Densidade dos Scores Compostos', fontsize=14, pad=20)
    axs[0,1].set_xlabel('Score Composto', fontsize=12)
    axs[0,1].legend()
    
    # Gráfico 3: Médias Comparativas
    avg_scores = df[['Positive', 'Negative', 'Neutral']].mean().reset_index()
    avg_scores.columns = ['Sentimento', 'Média']
    sns.barplot(data=avg_scores, x='Sentimento', y='Média', ax=axs[1,0], 
                palette=['#66c2a5', '#fc8d62', '#8da0cb'])
    axs[1,0].set_title('Médias de Scores de Sentimento', fontsize=14, pad=20)
    axs[1,0].set_ylim(0, 1)
    
    # Gráfico 4: Word Cloud
    all_text = " ".join(tweet for tweet in df['tweet'])
    wordcloud = WordCloud(
        width=800, height=400, 
        background_color='white', 
        stopwords=stopwords_set,
        max_words=200
    ).generate(all_text)
    axs[1,1].imshow(wordcloud, interpolation='bilinear')
    axs[1,1].set_title('Palavras mais Frequentes', fontsize=14, pad=20)
    axs[1,1].axis('off')
    
    # Ajustes finais
    plt.suptitle('Análise de Sentimento em Tweets', fontsize=18, y=0.98)
    plt.tight_layout(pad=3.0)
    plt.savefig('twitter_sentiment_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

create_visualizations(data)

print("Análise concluída! Arquivos gerados:")
print("- sentiment_analysis.csv")
print("- relatorio_sentimentos.md")
print("- twitter_sentiment_analysis.png")