from minio import Minio
import json
import io
import duckdb
from dotenv import load_dotenv

load_dotenv()
# Configurer le client Minio
con = duckdb.connect('echowize.db')
print(con)

con.sql("select * from negative_reviews").show()
con.sql("DESCRIBE conso_reviews").show()

con.sql("""SELECT DATE_TRUNC('month', iso_date) as month, 
                   AVG(rating) as avg_rating,
                   COUNT(*) as review_count
            FROM conso_reviews
            GROUP BY month""").show()

