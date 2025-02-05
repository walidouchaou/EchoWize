from typing import Dict, Any
import duckdb
from dotenv import load_dotenv
import os

class DataTransformer:
    def __init__(self):
        load_dotenv()
        self.con = duckdb.connect('echowize.db')
        self._configure_s3()
    
    def _configure_s3(self):
        self.con.query("""
            INSTALL httpfs;
            LOAD httpfs;
            SET s3_region='eu-east-1';
            SET s3_url_style='path';
            SET s3_endpoint='localhost:9000';
            SET s3_access_key_id='1hDxjeNAlqUuVQqHQZbO';
            SET s3_secret_access_key='M2FsRid6WCDQCZNh7x0gmNj7IitM9qKlxlqFhEY0';
            SET s3_use_ssl=false;
        """)
    
    def transform_reviews(self):
        self.con.query("""CREATE OR REPLACE TABLE conso_reviews AS 
            SELECT *
            FROM read_csv('s3://echowize/reviews.csv')
        """)
        
        self.con.query("""CREATE OR REPLACE TABLE negative_reviews AS 
            SELECT
            rating, 
            snippet,
            iso_date ,
            '' as recommendation,
            UUID() as review_id
            FROM conso_reviews 
            WHERE rating < 2
        """)
    
    def close(self):
        self.con.close() 