
import duckdb
from dotenv import load_dotenv
import os

class DataTransformer:
    def __init__(self):
        load_dotenv()
        self.con = duckdb.connect('echowize.db')
        self._configure_s3()
    
    def _configure_s3(self):
        self.con.query(f"""
            INSTALL httpfs;
            LOAD httpfs;
            SET s3_region='eu-east-1';
            SET s3_url_style='path';
            SET s3_endpoint='{os.getenv("MINIO_ENDPOINT")}';
            SET s3_access_key_id='{os.getenv("MINIO_ACCESS_KEY")}';
            SET s3_secret_access_key='{os.getenv("MINIO_SECRET_KEY")}';
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
