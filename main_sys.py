from config import CONFIG
from classifier import MedicineClassifier
from ims1 import InventoryManagementSystem
from risk_assess import SupplyChainRiskAssessment
from route_opt import RouteOptimizer
from mitigation_rec import RiskMitigator
from flask import Flask

app = Flask(__name__)

class HospitalSupplyChainSystem:
    def __init__(self):
        self.medicine_classifier = MedicineClassifier(CONFIG['medicine_data_path'])
        self.inventory_system = InventoryManagementSystem(n_products= 20, n_days=365)
        self.risk_assessor = SupplyChainRiskAssessment(CONFIG['sc_data_path'], CONFIG['sc2_data_path'])
        self.route_optimizer = RouteOptimizer(
            CONFIG[ 'hospital_address'],
            CONFIG['openweathermap_api_key'],
            CONFIG['tomtom_api_key']
        )
        self.risk_mitigator = RiskMitigator(
            self.medicine_classifier,
            self.inventory_system,
            self.risk_assessor,
            self.route_optimizer
        )

    def classify_medicines(self):
        return self.medicine_classifier.run_classification()

    def get_inventory_status(self):
        return self.inventory_system.get_inventory_status()

    def assess_supplier_risks(self):
        return self.risk_assessor.assess_all_supplier_risks()

    def optimize_route(self):
        return self.route_optimizer.optimize_route()

    def generate_risk_mitigation_report(self):
        return self.risk_mitigator.generate_report()
    
