# faq_loader.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

class FAQStore:
    def __init__(self, csv_path="faqs.csv"):
        self.df = pd.read_csv(csv_path)
        self.questions = self.df['question'].astype(str).tolist()
        self.answers = self.df['answer'].astype(str).tolist()
        self.ids = self.df['id'].tolist()
        # TF-IDF vectorizer trained on FAQ questions
        self.vectorizer = TfidfVectorizer(stop_words='english').fit(self.questions)
        self.q_vectors = self.vectorizer.transform(self.questions)

    def nearest(self, query, top_k=1):
        qv = self.vectorizer.transform([query])
        from sklearn.metrics.pairwise import cosine_similarity
        sims = cosine_similarity(qv, self.q_vectors).flatten()
        idx_sorted = sims.argsort()[::-1]
        results = []
        for idx in idx_sorted[:top_k]:
            results.append({
                "id": self.ids[idx],
                "question": self.questions[idx],
                "answer": self.answers[idx],
                "score": float(sims[idx])
            })
        return results
