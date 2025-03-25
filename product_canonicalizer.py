import sys

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class ProductCanonicalizer:
    def __init__(self, products_path: str, classes_path: str, output_path: str):
        self.output_path = output_path
        self.canonicalized_df = None
        self.products_df = self.load_file_to_df(products_path, sep='|', encoding='ISO-8859-1')
        self.classes_df = self.load_file_to_df(classes_path, sep='\t', encoding='ISO-8859-1')
        
    
    def canonicalize(self):
        sim_matrix = self.similarity_matrix()
        best_match_indices = np.argmax(sim_matrix, axis=1)
        
        product_base = self.products_df.drop(columns=['itemType'], errors='ignore').reset_index(drop=True)   
        matched_classes = self.classes_df.iloc[best_match_indices][
            ["product_class_id", "product_subcategory", "product_category", "product_department", "product_family"]
        ].reset_index(drop=True)
        
        self.canonicalized_df = pd.concat([product_base, matched_classes], axis=1)
    
    def generate_embeddings(self):
        class_columns = ["product_subcategory", "product_category", "product_department", "product_family"]
        product_columns = ["Manufacturer", "Product Name", "itemType"]

        class_descriptions = self._generate_descriptions(self.classes_df, class_columns, sep='|')
        product_descriptions = self._generate_descriptions(self.products_df, product_columns, sep='|')        
        
        model = SentenceTransformer('sentence-t5-large')
        
        self.class_embeddings = self._embeddings_from_descriptions(class_descriptions, model)
        self.product_embeddings = self._embeddings_from_descriptions(product_descriptions, model)
    
    def similarity_matrix(self):
        return cosine_similarity(self.product_embeddings, self.class_embeddings)
        
    def load_file_to_df(self, path: str, sep: str, encoding: str):
        try:
            return pd.read_csv(path, sep=sep, encoding=encoding)
        
        except FileNotFoundError:
            print(f"File not found: {path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading input file: {e}")
            sys.exit(1)
    
    def write_df_to_file(self, df: pd.DataFrame, sep: str):
        try:
            df.to_csv(self.output_path, sep=sep, encoding='ISO-8859-1')
        except Exception as e:
            print(f"Error writing output file: {e}")
            sys.exit(1)
            
    def _embeddings_from_descriptions(self, descriptions: pd.Series, model: SentenceTransformer):
        return model.encode(descriptions, show_progress_bar=True)
    
    def _generate_descriptions(self, df: pd.DataFrame, columns: list[str], sep: str):
        return df[columns].astype(str).apply(lambda x: sep.join(x), axis=1)

if __name__ == "__main__":
    usage_str = "Usage: python product_canonicalizer.py <products_path> <classes_path> <output_path>"
    
    if "--help" in sys.argv or '-h' in sys.argv or len(sys.argv) < 4:
        print(usage_str)
        sys.exit(1)
    
    canonicalizer = ProductCanonicalizer(sys.argv[1], sys.argv[2], sys.argv[3])        
    canonicalizer.generate_embeddings()
    canonicalizer.canonicalize()
    canonicalizer.write_df_to_file(canonicalizer.canonicalized_df, sep='|')
    