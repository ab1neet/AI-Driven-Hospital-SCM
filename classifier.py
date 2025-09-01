import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import os
from collections import defaultdict

os.environ["LOKY_MAX_CPU_COUNT"] = "4"
medicine_data_path = "A_Z_medicines_dataset_of_India.csv"

class MedicineClassifier:
    def __init__(self, medicine_data_path):
        self.df = pd.read_csv(medicine_data_path)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.kmeans = KMeans(n_clusters=10, random_state=42)
        self.disease_priority = {
            # Life-saving/Emergency medicines
            'injection': 0.9,  
            'emergency': 0.9,
            'epinephrine': 0.9,
            'insulin': 0.9,
            
            # Critical Care
            'antibiotic': 0.8,
            'azithromycin': 0.8,
            'cefixime': 0.8,
            
            # Chronic Disease Management
            'heart': 0.7,
            'diabetes': 0.7,
            'respiratory': 0.7,
            'blood pressure': 0.7,
            'telmisartan': 0.7,
            
            # Pain Management
            'pain': 0.6,
            'paracetamol': 0.5,
            'aceclofenac': 0.5,
            
            # General Medications
            'vitamin': 0.3,
            'supplement': 0.3,
            'allergy': 0.4,
            'levocetirizine': 0.4
        }
        self.cluster_categories = {
            'diabetes': ['glimepiride', 'metformin', 'insulin'],
            'antibiotics': ['azithromycin', 'ofloxacin', 'cefixime'],
            'pain_management': ['paracetamol', 'aceclofenac', 'nimesulide'],
            'cardiovascular': ['telmisartan', 'blood pressure', 'heart'],
            'respiratory': ['montelukast', 'respiratory', 'bronchial'],
            'antiallergic': ['levocetirizine', 'allergy', 'antihistamine'],
            'gastrointestinal': ['pantoprazole', 'omeprazole', 'digestion'],
            'emergency': ['injection', 'emergency', 'critical'],
            'supplements': ['vitamin', 'supplement', 'mineral'],
            'general': ['tablet', 'capsule', 'syrup']
        }
    def preprocess_data(self):
        self.df['text_for_clustering'] = self.df['name'] + ' ' + self.df['short_composition1'] + ' ' + self.df['short_composition2'].fillna('')
        
        self.df['text_for_clustering'] = self.df['text_for_clustering'].str.lower()

    def cluster_medicines(self):
        tfidf_matrix = self.vectorizer.fit_transform(self.df['text_for_clustering'])
        
        self.kmeans.fit(tfidf_matrix)
        self.df['cluster'] = self.kmeans.labels_

    def assign_disease_categories(self):
        self.df['priority'] = 0.0
        
        for medicine_idx in self.df.index:
            total_priority = 0.0
            matches = 0
            
            medicine_text = str(self.df.loc[medicine_idx, 'text_for_clustering']).lower()
            
            for keyword, priority in self.disease_priority.items():
                if keyword in medicine_text:
                    total_priority += priority
                    matches += 1
            
            if matches > 0:
                self.df.loc[medicine_idx, 'priority'] = total_priority / matches
            
            if 'injection' in medicine_text:
                self.df.loc[medicine_idx, 'priority'] *= 1.2
                
            if 'high dose' in medicine_text or 'strong' in medicine_text:
                self.df.loc[medicine_idx, 'priority'] *= 1.1
                
            self.df.loc[medicine_idx, 'priority'] = min(self.df.loc[medicine_idx, 'priority'], 1.0)

    def calculate_cluster_priority(self, cluster_id):
        cluster_medicines = self.df[self.df['cluster'] == cluster_id]
        
        base_priority = cluster_medicines['priority'].mean()
        max_priority = cluster_medicines['priority'].max()
        
        cluster_priority = (0.7 * base_priority) + (0.3 * max_priority)
        
        return cluster_priority
    def assign_cluster_names(self, cluster_id, top_terms):
        category_matches = {category: 0 for category in self.cluster_categories}
        
        for term in top_terms:
            for category, keywords in self.cluster_categories.items():
                if any(keyword in term.lower() for keyword in keywords):
                    category_matches[category] += 1
        
        best_category = max(category_matches.items(), key=lambda x: x[1])[0]
        
        dosage_info = ''
        dosage_terms = [term for term in top_terms if 'mg' in term]
        if dosage_terms:
            dosage_info = f" ({', '.join(dosage_terms[:2])})"
        
        cluster_name = best_category.replace('_', ' ').title()
        return f"Cluster {cluster_id}: {cluster_name}{dosage_info}"
    
    def get_cluster_summaries(self):
        cluster_summaries = defaultdict(list)
        for cluster in range(self.kmeans.n_clusters):
            cluster_medicines = self.df[self.df['cluster'] == cluster]
            top_terms = self.get_top_terms_per_cluster(cluster)
            avg_priority = cluster_medicines['priority'].mean()
            
            cluster_name = self.assign_cluster_names(cluster, top_terms)
            
            cluster_summaries[cluster_name] = {
                'top_terms': top_terms,
                'avg_priority': avg_priority,
                'size': len(cluster_medicines)
            }
        return cluster_summaries

    def get_top_terms_per_cluster(self, cluster, top_n=5):
        cluster_center = self.kmeans.cluster_centers_[cluster]
        terms = self.vectorizer.get_feature_names_out()
        top_term_indices = cluster_center.argsort()[-top_n:][::-1]
        return [terms[i] for i in top_term_indices]

    def run_classification(self):
        self.preprocess_data()
        self.cluster_medicines()
        self.assign_disease_categories()
        return self.get_cluster_summaries()


classifier = MedicineClassifier(medicine_data_path)
cluster_summaries = classifier.run_classification()

for cluster_name, summary in cluster_summaries.items():
    print(f"{cluster_name}:")
    print(f"Top terms: {', '.join(summary['top_terms'])}")
    print(f"Average priority: {summary['avg_priority']:.2f}")
    print(f"Cluster size: {summary['size']}")
    print()

classified_medicines = classifier.df