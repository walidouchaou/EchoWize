from dotenv import load_dotenv
from openai import OpenAI
import duckdb 
import os


class integrationOpenIA :
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    def __init__(self):
        load_dotenv()
        self.con = duckdb.connect('echowize.db')
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)
    
    def get_comment_negative(self):
        #self.con.execute("ALTER TABLE negative_reviews ADD COLUMN recommendation TEXT")
        #self.con.execute("ALTER TABLE negative_reviews ADD COLUMN review_id UUID DEFAULT UUID()")
        data = self.con.sql("SELECT review_id, snippet FROM negative_reviews").fetchall()
        return data

    def get_recommendation(self, negative_review):
        prompt = f"""
        Analysez cet avis négatif et donnez uniquement :
        - Un bref résumé en 2-3 phrases maximum
        - Une liste de recommandations concrètes numérotées

        Avis: {negative_review}
        """
        
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en analyse d'avis clients. Soyez bref et concis dans vos réponses."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

    def process_negative_reviews(self):
        negative_reviews = self.get_comment_negative()
        
        for review_id, snippet in negative_reviews:
            recommendation = self.get_recommendation(snippet)
            
            self.con.execute("""
                UPDATE negative_reviews 
                SET recommendation = ? 
                WHERE review_id = ?
            """, [recommendation, review_id])


