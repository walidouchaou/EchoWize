from serpapi import GoogleSearch
from dotenv import load_dotenv
from minio import Minio
import os
import json
from io import BytesIO
import csv
from io import StringIO



class SerapiService:
    def __init__(self):
        load_dotenv()
        self.api_key: str = os.getenv('SERPAPI_KEY')
        self.page_count: int = 0
        self.max_pages: int = 5
        self.all_reviews: list = []
        self.next_page_token: str = None
        self.minio_client: Minio = Minio(
            endpoint=os.getenv('MINIO_ENDPOINT'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),
            secret_key=os.getenv('MINIO_SECRET_KEY'),
            secure=False
        )
        self.bucket_name: str = os.getenv('MINIO_BUCKET_NAME')

    def get_data_id(self, restaurant_name: str)->str:
        search_params = {
            "engine": "google_maps",
            "q": restaurant_name,
            "api_key": self.api_key,
            "hl": "fr"
        }
        search = GoogleSearch(search_params)
        results = search.get_dict()
        data_id = results['place_results']['data_id']
        return data_id
    
    def get_reviews(self, data_id: str) -> list:
        # Réinitialiser les variables d'état pour permettre plusieurs appels
        self.page_count = 0
        self.all_reviews = []
        self.next_page_token = None
        
        search_params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "api_key": self.api_key,
            "hl": "fr"
        }
        
        while self.page_count < self.max_pages:
            if self.next_page_token:
                search_params["next_page_token"] = self.next_page_token
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            current_reviews = results.get('reviews', [])
            self.all_reviews.extend(current_reviews)
            
            if 'serpapi_pagination' in results and 'next_page_token' in results['serpapi_pagination']:
                self.next_page_token = results['serpapi_pagination']['next_page_token']
                self.page_count += 1
            else:
                break
                
        return self.all_reviews
    def upload_reviews_to_csv(self, reviews: list, restaurant_name: str) -> None:
        try:
            # Définir les en-têtes du CSV
            fieldnames = [
                'rating', 
                'date', 
                'iso_date',
                'user_name',
                'snippet',
                'service',
                'cuisine',
                'ambiance',
                'type_de_repas',
                'prix_par_personne'
            ]
            
            # Créer un buffer pour stocker le CSV
            csv_buffer = StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
            writer.writeheader()

            # Écrire chaque review
            for review in reviews:
                row = {
                    'rating': review.get('rating', ''),
                    'date': review.get('date', ''),
                    'iso_date': review.get('iso_date', ''),
                    'user_name': review.get('user', {}).get('name', ''),
                    'snippet': review.get('snippet', ''),
                    'service': review.get('details', {}).get('service', ''),
                    'cuisine': review.get('details', {}).get('cuisine', ''),
                    'ambiance': review.get('details', {}).get('ambiance', ''),
                    'type_de_repas': review.get('details', {}).get('type_de_repas', ''),
                    'prix_par_personne': review.get('details', {}).get('prix_par_personne', '')
                }
                writer.writerow(row)

            # Convertir en bytes pour MinIO
            csv_bytes = csv_buffer.getvalue().encode('utf-8')
            
            # Nom du fichier
            object_name = f"reviews.csv"
            
            # Upload vers MinIO
            with BytesIO(csv_bytes) as output:
                self.minio_client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    data=output,
                    length=len(csv_bytes),
                    content_type="text/csv"
                )
                
        except Exception as e:
            raise Exception(f"Erreur lors de l'upload vers MinIO: {str(e)}")



