from elasticsearch import Elasticsearch
import time
from config import Config

def wait_for_elasticsearch(max_retries=5, delay=5):
    retries = 0
    es = Elasticsearch(
        Config.get_elasticsearch_url(),
        basic_auth=(Config.ELASTICSEARCH_USER, Config.ELASTICSEARCH_PASSWORD),
        verify_certs=Config.ELASTICSEARCH_VERIFY_CERTS
    )
    
    while retries < max_retries:
        try:
            if es.ping():
                print("Successfully connected to Elasticsearch")
                return es
            else:
                print(f"Could not connect to Elasticsearch. Attempt {retries + 1}/{max_retries}")
        except Exception as e:
            print(f"Connection attempt {retries + 1} failed: {str(e)}")
        
        retries += 1
        time.sleep(delay)
    
    raise ConnectionError("Could not connect to Elasticsearch after maximum retries")

def index_exists(es, index_name):
    return es.indices.exists(index=index_name)