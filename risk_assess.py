import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm
import plotly.graph_objs as go
        
class SupplyChainRiskAssessment:
    def __init__(self, sc_data_path, sc2_data_path):
        self.sc_data = pd.read_csv("SC.csv")
        self.sc2_data = pd.read_csv("SC2.csv")
        self.suppliers = self.create_synthetic_supplier_data()
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)

    def create_synthetic_supplier_data(self):
        suppliers = pd.DataFrame({
            'supplier_id': range(1, 21),
            'reliability_score': np.random.uniform(0.5, 1, 20),
            'avg_lead_time': np.random.uniform(1, 30, 20),
            'avg_defect_rate': np.random.uniform(0, 0.1, 20),
            'on_time_delivery_rate': np.random.uniform(0.8, 1, 20),
            'weather_risk': np.random.uniform(0, 1, 20),
            'traffic_risk': np.random.uniform(0, 1, 20)
        })
        return suppliers

    def assess_supplier_risk(self, supplier_id):
        supplier = self.suppliers[self.suppliers['supplier_id'] == supplier_id].iloc[0]
        risk_score = (
            (1 - supplier['reliability_score']) * 0.3 +
            (supplier['avg_lead_time'] / 30) * 0.2 +
            supplier['avg_defect_rate'] * 0.2 +
            (1 - supplier['on_time_delivery_rate']) * 0.1 +
            supplier['weather_risk'] * 0.1 +
            supplier['traffic_risk'] * 0.1
        )
        return risk_score
    def assess_all_supplier_risks(self):

        risk_scores = {}
        for index, row in self.suppliers.iterrows():

            supplier_id = row['supplier_id']
            risk_score = self.assess_supplier_risk(supplier_id)
            try:
                X = supplier_id.drop('supplier_id').values.reshape(1, -1)
                X_scaled = self.scaler.transform(X)
                anomaly_score = self.anomaly_detector.decision_function(X_scaled)[0]
                if anomaly_score < 0:
                    anomaly_adjustment = min(0.2, abs(anomaly_score) * 0.1)
                    risk_score = min(1.0, risk_score + anomaly_adjustment)
            except:
                pass
            
            try:
                simulation_results = self.monte_carlo_simulation(supplier_id, n_simulations=1000)
                confidence_interval = simulation_results['95%_confidence_interval']
                interval_width = confidence_interval[1] - confidence_interval[0]
                uncertainty_factor = min(0.15, interval_width / 30)  
                risk_score = min(1.0, risk_score + uncertainty_factor)
            except:
                pass
        
            supplier_name = f"Supplier {supplier_id}"
            risk_scores[supplier_name] = round(risk_score, 2)
        
        high_risk_suppliers = {k: v for k, v in risk_scores.items() if v >= 0.7}
        if high_risk_suppliers:
            print(f"High risk suppliers detected: {', '.join(high_risk_suppliers.keys())}")

        avg_risk = sum(risk_scores.values()) / len(risk_scores) if risk_scores else 0
        print(f"Average supplier risk: {avg_risk:.2f}")
        
        return risk_scores
    
    def predict_disruptions(self):
        X = self.scaler.fit_transform(self.suppliers.drop('supplier_id', axis=1))
        self.anomaly_detector.fit(X)
        anomaly_scores = self.anomaly_detector.decision_function(X)
        self.suppliers['anomaly_score'] = anomaly_scores
        return self.suppliers[self.suppliers['anomaly_score'] < 0]

    def detect_unusual_patterns(self, data):
        X = self.scaler.fit_transform(data)
        anomalies = self.anomaly_detector.fit_predict(X)
        return data[anomalies == -1]

    def calculate_supplier_reliability(self):
        self.suppliers['reliability_score'] = (
            self.suppliers['reliability_score'] * 0.3 +
            (1 - self.suppliers['avg_lead_time'] / 30) * 0.2 +
            (1 - self.suppliers['avg_defect_rate']) * 0.2 +
            self.suppliers['on_time_delivery_rate'] * 0.3
        )
        return self.suppliers[['supplier_id', 'reliability_score']]

    def monte_carlo_simulation(self, supplier_id, n_simulations=10000):
        supplier = self.suppliers[self.suppliers['supplier_id'] == supplier_id].iloc[0]
        lead_time_mean = supplier['avg_lead_time']
        lead_time_std = lead_time_mean * 0.2  
        
        simulated_lead_times = np.random.normal(lead_time_mean, lead_time_std, n_simulations)
        simulated_lead_times = np.maximum(simulated_lead_times, 0)  
        counts, bins = np.histogram(simulated_lead_times, bins=50)
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
    
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=bin_centers,
            y=counts,
            marker_color='skyblue',
            opacity=0.7,
            name='Simulated Lead Times'
        ))
        fig.add_trace(go.Scatter(
            x=[lead_time_mean, lead_time_mean],
            y=[0, counts.max() * 1.1],
            mode='lines',
            line=dict(color='red', dash='dash', width=2),
            name='Mean Lead Time'
        ))
        fig.update_layout(
            title=f"Monte Carlo Simulation of Lead Times for Supplier {supplier_id}",
            xaxis_title="Lead Time (days)",
            yaxis_title="Frequency",
            template='plotly_white'
        )
        confidence_interval = norm.interval(0.95, loc=lead_time_mean, scale=lead_time_std)
        
        return {
            'chart': fig.to_json(),
            'mean_lead_time': lead_time_mean,
            '95%_confidence_interval': confidence_interval.tolist() if hasattr(confidence_interval, 'tolist') else list(confidence_interval)
        }
        
risk_assessor = SupplyChainRiskAssessment('SC', 'SC2')


supplier_id = 1
risk_score = risk_assessor.assess_supplier_risk(supplier_id)
print(f"Risk score for supplier {supplier_id}: {risk_score:.2f}")


disruptions = risk_assessor.predict_disruptions()
print("\nPotential disruptions:")
print(disruptions)

unusual_patterns = risk_assessor.detect_unusual_patterns(risk_assessor.sc_data[['Days_for_shipping_real', 'Days_for_shipment_scheduled', 'Benefit_per_order']])
print("\nUnusual patterns in shipping data:")
print(unusual_patterns)


reliability_scores = risk_assessor.calculate_supplier_reliability()
print("\nSupplier reliability scores:")
print(reliability_scores)

simulation_result = risk_assessor.monte_carlo_simulation(supplier_id)
print(f"\nMonte Carlo simulation results for supplier {supplier_id}:")
print(f"Mean lead time: {simulation_result['mean_lead_time']:.2f} days")
print(f"95% Confidence Interval: {simulation_result['95%_confidence_interval']}")