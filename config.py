class Config:
    # Flask settings
    SECRET_KEY = 'your_secret_key'
    DEBUG = True

    # Elasticsearch settings
    ELASTICSEARCH_HOST = 'localhost'
    ELASTICSEARCH_PORT = 9200
    ELASTICSEARCH_INDEX = 'your_index_name'
    ELASTICSEARCH_USER = 'elastic'
    ELASTICSEARCH_PASSWORD = '7e*s+S7SsiF36CV0Tghd'
    ELASTICSEARCH_SCHEME = 'https'
    ELASTICSEARCH_VERIFY_CERTS = False

    @staticmethod
    def get_elasticsearch_url():
        return f"{Config.ELASTICSEARCH_SCHEME}://{Config.ELASTICSEARCH_HOST}:{Config.ELASTICSEARCH_PORT}"
