import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import re

News_API_KEY = "d8f46f24488d469f82ef0f1987fb91e1"
Newsdata_API_KEY = "pub_440061d1f1fe64f7148fd8824c34326aaf6d6"

def fetch_news_articles(api_key_newsapi, api_key_newsdata, category, page_size=40):
    # Standard format for articles
    def standardize_article(article, source):
        if source == 'newsapi':
            return {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'image': article.get('urlToImage', '')  # Assuming 'urlToImage' holds the image URL
            }
        elif source == 'newsdata':
            return {
                'title': article.get('title', ''),
                'description': article.get('content', ''),  # Assuming 'content' holds the description
                'url': article.get('link', ''),  # Assuming 'link' holds the URL
                'image': article.get('image_url', '')  # Assuming 'image_url' holds the image URL
            }

    # Fetch from News API
    url_newsapi = f'https://newsapi.org/v2/top-headlines?country=us&category={category}&pageSize={page_size}&apiKey={api_key_newsapi}'
    response_newsapi = requests.get(url_newsapi)
    if response_newsapi.status_code == 200:
        try:
            data_newsapi = response_newsapi.json()
            print("News API Response:", data_newsapi)  # Debug print
        except ValueError:
            print("Failed to parse JSON from News API")
            data_newsapi = {}
    else:
        print(f"News API returned status code {response_newsapi.status_code}")
        data_newsapi = {}

    articles_newsapi = [
        standardize_article(article, 'newsapi') 
        for article in data_newsapi.get('articles', []) 
        if article.get('description') and '[Removed]' not in article.get('title', '') and '[Removed]' not in article.get('description', '')
    ]

    # Fetch from Newsdata.io API
    url_newsdata = f'https://newsdata.io/api/1/news?apikey={api_key_newsdata}&category={category}&language=en&page_size={page_size}'
    response_newsdata = requests.get(url_newsdata)
    if response_newsdata.status_code == 200:
        try:
            data_newsdata = response_newsdata.json()
            print("Newsdata.io Response:", data_newsdata)  # Debug print
        except ValueError:
            print("Failed to parse JSON from Newsdata.io")
            data_newsdata = {}
    else:
        print(f"Newsdata.io returned status code {response_newsdata.status_code}")
        data_newsdata = {}

    articles_newsdata = [
        standardize_article(article, 'newsdata') 
        for article in data_newsdata.get('results', []) 
        if article.get('content') and '[Removed]' not in article.get('title', '') and '[Removed]' not in article.get('content', '')
    ]

    # Merge and return the results
    return articles_newsapi + articles_newsdata

def preprocess_text(text):
    """
    Preprocess text data.

    Args:
    - text (str): The text to preprocess.

    Returns:
    - str: The preprocessed text.
    """
    # Remove HTML tags
    text = re.sub('<[^<]+?>', '', text)
    # Remove special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    return text

def topic_modeling(news_articles, num_clusters=5):
    """
    Perform topic modeling and categorization.

    Args:
    - news_articles (list): A list of dictionaries containing news article titles and descriptions.
    - num_clusters (int): The number of clusters for K-means clustering.

    Returns:
    - list: A list of cluster labels for the news articles.
    """
    tfidf_vectorizer = TfidfVectorizer()
    titles = [article['title'] for article in news_articles]
    tfidf_matrix = tfidf_vectorizer.fit_transform(titles)

    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(tfidf_matrix)
    clusters = kmeans.labels_

    return clusters

def detect_duplicates(articles, threshold=0.8):
    """
    Detect duplicate articles.

    Args:
    - articles (list): A list of dictionaries containing news article titles and descriptions.
    - threshold (float): The similarity threshold for considering articles as duplicates.

    Returns:
    - set: A set of tuple pairs representing duplicate article indices.
    """
    tfidf_vectorizer = TfidfVectorizer()
    titles = [article['title'] for article in articles]
    tfidf_matrix = tfidf_vectorizer.fit_transform(titles)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    duplicates = set()
    for i in range(len(articles)):
        for j in range(i+1, len(articles)):
            if similarity_matrix[i][j] > threshold:
                duplicates.add((i, j))

    return duplicates

def get_default_news(api_key_newsapi=News_API_KEY, api_key_newsdata=Newsdata_API_KEY, category='general'):
    """
    Fetch and merge news articles from both News API and Newsdata.io API for a given category.

    Args:
    - api_key_newsapi (str): Your News API key.
    - api_key_newsdata (str): Your Newsdata.io API key.
    - category (str): The category of news articles to fetch.

    Returns:
    - list: A merged list of dictionaries containing news article titles, descriptions, URLs, and images.
    """
    newsapi_articles = fetch_news_articles(News_API_KEY, Newsdata_API_KEY, category)

    return newsapi_articles

