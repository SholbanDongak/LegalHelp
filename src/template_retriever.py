import chromadb

class TemplateRetriever:
    def __init__(self, db_path="./legal_chromadb", collection_name="templates", top_k=1):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(collection_name)

    def retrieve(self, query: str, subtype: str = None):
        if subtype:
            try:
                result = self.collection.get(ids=[subtype])
                if result['documents'] and result['documents'][0]:
                    return result['documents'][0], result['metadatas'][0]
            except Exception:
                pass
        return None, None
