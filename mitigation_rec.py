import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.optimize import minimize
from sklearn.metrics.pairwise import cosine_similarity
import traceback


class RiskMitigator:
    def __init__(self, medicine_classifier, inventory_system, risk_assessor, route_optimizer):
        self.medicine_classifier = medicine_classifier
        self.inventory_system = inventory_system
        self.risk_assessor = risk_assessor
        self.route_optimizer = route_optimizer
        self.rule_based_system = self.create_rule_based_system()
        self.ml_model = self.train_ml_model()
        self.past_situations = self.load_past_situations()

    def create_rule_based_system(self):
        return {
            'high_risk_supplier': lambda risk_score: risk_score > 0.7,
            'low_inventory': lambda stock_level, reorder_point: stock_level < reorder_point,
            'excess_inventory': lambda stock_level, reorder_point: stock_level > 2 * reorder_point,
            'high_supplier_concentration': lambda concentration: concentration > 0.8,
            'route_inefficiency': lambda actual_cost, normal_cost: actual_cost > 1.5 * normal_cost
        }

    def train_ml_model(self):
        n_samples = 1000
        np.random.seed(42)  
        risk_severity = np.random.beta(2, 5, n_samples)  
        recommendation_area = np.random.choice([0, 0.5, 1], n_samples)
        implementation_complexity = np.random.beta(2, 2, n_samples)  
    
        cost_impact = np.random.beta(2, 3, n_samples)  
    
        time_sensitivity = np.random.beta(3, 2, n_samples)  
        X = np.column_stack([
            risk_severity, 
            recommendation_area, 
            implementation_complexity,
            cost_impact,
            time_sensitivity
        ])
        
        effectiveness = (
            0.3 * risk_severity +                  
            0.1 * recommendation_area +            
            -0.2 * implementation_complexity +     
            -0.25 * cost_impact +                 
            0.15 * time_sensitivity               
        )
        
        effectiveness += np.random.normal(0, 0.1, n_samples)
        effectiveness = np.clip(effectiveness, 0, 1)
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        X_train, X_test, y_train, y_test = train_test_split(
            X, effectiveness, test_size=0.2, random_state=42
        )
    
        model.fit(X_train, y_train)
        
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        print(f"ML Model Training Completed")
        print(f"Training R² Score: {train_score:.4f}")
        print(f"Testing R² Score: {test_score:.4f}")
        
        feature_names = [
            "Risk Severity", "Recommendation Area", "Implementation Complexity", 
            "Cost Impact", "Time Sensitivity"
        ]
        
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        print("\nFeature Importance:")
        for i in range(len(feature_names)):
            print(f"{feature_names[indices[i]]}: {importances[indices[i]]:.4f}")
        
        return model

    def load_past_situations(self):
        np.random.seed(42)  
        n_situations = 100
        
        strategies = [
            "Diversify suppliers to reduce dependency",
            "Increase safety stock for critical items",
            "Implement just-in-time delivery for non-critical items",
            "Develop alternative sourcing for high-risk materials",
            "Negotiate flexible delivery arrangements",
            "Implement better demand forecasting",
            "Create strategic supplier partnerships",
            "Adopt inventory management software",
            "Optimize delivery routes",
            "Train staff on better inventory practices"
        ]
        
        start_date = pd.Timestamp.now() - pd.Timedelta(days=2*365)
        end_date = pd.Timestamp.now()
        dates = pd.date_range(start=start_date, end=end_date, periods=n_situations)
        
        situations = pd.DataFrame({
            'date': dates,         
            'risk_score': np.random.beta(2, 5, n_situations),  
            'inventory_level': np.random.beta(5, 2, n_situations),             
            'supplier_concentration': np.random.beta(3, 4, n_situations),      
            'route_efficiency': np.random.beta(4, 2, n_situations),
            'is_emergency': np.random.choice([False, True], n_situations, p=[0.8, 0.2]),
            'weather_condition': np.random.choice(
                ['normal', 'adverse', 'extreme'], 
                n_situations, 
                p=[0.7, 0.2, 0.1]
            ),
            'strategy': np.random.choice(strategies, n_situations)
        })
        situations['effectiveness'] = 0.0
        
        for i, row in situations.iterrows():
            base_effectiveness = np.random.uniform(0.3, 0.7)  
            
            strategy = row['strategy'].lower()
            if 'supplier' in strategy:
                supplier_factor = 0.3 * row['supplier_concentration']
                base_effectiveness += supplier_factor

            elif any(term in strategy for term in ['inventory', 'stock', 'forecasting']):
                inventory_factor = 0.3 * (1 - row['inventory_level'])
                base_effectiveness += inventory_factor

            elif any(term in strategy for term in ['route', 'delivery']):
                route_factor = 0.3 * (1 - row['route_efficiency'])
                base_effectiveness += route_factor
            
            if row['is_emergency']:
                base_effectiveness *= 0.8
            
            if row['weather_condition'] == 'adverse':
                base_effectiveness *= 0.9
            elif row['weather_condition'] == 'extreme':
                base_effectiveness *= 0.7

            situations.at[i, 'effectiveness'] = min(max(base_effectiveness, 0), 1)
        
        print(f"Loaded {n_situations} historical situations")
    
        strategy_categories = {}
        for s in strategies:
            if any(term in s.lower() for term in ['supplier', 'sourc']):
                strategy_categories[s] = 'supplier'
            elif any(term in s.lower() for term in ['inventory', 'stock', 'forecast']):
                strategy_categories[s] = 'inventory'
            elif any(term in s.lower() for term in ['route', 'delivery']):
                strategy_categories[s] = 'logistics'
            else:
                strategy_categories[s] = 'other'
        
        situations['strategy_category'] = situations['strategy'].map(strategy_categories)
        
        print("\nStrategy effectiveness by category:")
        category_effectiveness = situations.groupby('strategy_category')['effectiveness'].mean()
        
        for category, effectiveness in category_effectiveness.items():
            print(f"  {category.title()}: {effectiveness:.2f}")
        
        return situations

    def generate_recommendations(self):
     
        recommendations = []

        try:
            # 1. Rule-based recommendations
            print("Getting supplier risks...")
            try:
                supplier_risks = self.risk_assessor.assess_all_supplier_risks()
            except Exception as e:
                print(f"Error getting supplier risks: {str(e)}")
                supplier_risks = {}  
                recommendations.append("Unable to assess supplier risks due to data issues.")
            
            print("Getting inventory status...")
            try:
                inventory_status = self.inventory_system.get_inventory_status()
            except Exception as e:
                print(f"Error getting inventory status: {str(e)}")
                inventory_status = {} 
                recommendations.append("Unable to assess inventory status due to data issues.")
            
            print("Getting supplier concentration...")
            try:
                supplier_concentration = self.inventory_system.get_supplier_concentration()
            except Exception as e:
                print(f"Error getting supplier concentration: {str(e)}")
                supplier_concentration = {}  
                recommendations.append("Unable to assess supplier concentration due to data issues.")
            
            print("Getting route optimization...")
            try:
                best_route, best_cost = self.route_optimizer.optimize_route()
            except Exception as e:
                print(f"Error getting route optimization: {str(e)}")
                best_route, best_cost = [], 0  
                recommendations.append("Unable to optimize routes due to data issues.")
            
            print("Calculating normal route cost...")
            try:
                if hasattr(self.route_optimizer, 'calculate_normal_cost') and best_route:
                    normal_cost = self.route_optimizer.calculate_normal_cost(best_route)
                else:
                    
                    print("calculate_normal_cost method not found, using estimate")
                    normal_cost = best_cost * 0.8 
            except Exception as e:
                print(f"Error calculating normal cost: {str(e)}")
                normal_cost = best_cost * 0.8  
        
            if supplier_risks:
                for supplier, risk_score in supplier_risks.items():
                    if risk_score > 0.7: 
                        recommendations.append(f"High risk detected for supplier {supplier}. Consider alternative suppliers.")

            if inventory_status:
                for medicine, status in inventory_status.items():
                    if status.get('stock_level', 0) < status.get('reorder_point', 0):
                        recommendations.append(f"Urgent reorder required for {medicine}")
                    elif status.get('stock_level', 0) > status.get('reorder_point', 0) * 2:
                        recommendations.append(f"Excess inventory detected for {medicine}. Consider reducing order quantities.")
 
            if supplier_concentration:
                for medicine, concentration in supplier_concentration.items():
                    if concentration > 0.8: 
                        recommendations.append(f"High supplier concentration for {medicine}. Consider diversifying suppliers.")

            if best_route and best_cost > 0 and normal_cost > 0:
                if best_cost > normal_cost * 1.5:  
                    recommendations.append("Current routes are significantly affected by traffic or weather. Consider adjusting delivery schedules.")
            
            if not recommendations:
                recommendations.append("All supply chain metrics are within normal ranges. No specific actions required at this time.")
                recommendations.append("Consider routine supplier evaluation to maintain supply chain resilience.")
                recommendations.append("Regular inventory audits recommended as a preventative measure.")
            
            print(f"Generated {len(recommendations)} initial recommendations")
            
            # 2. ML-based strategy prediction
            print("Predicting strategy effectiveness...")
            try:
                if hasattr(self, 'ml_model') and self.ml_model:
                    effectiveness_recommendations = []
                    for rec in recommendations[:5]:  
                        features = self.extract_features(rec)
                        effectiveness = self.ml_model.predict([features])[0]
                        effectiveness_recommendations.append(f"Predicted effectiveness of '{rec}': {effectiveness:.2f}")
                    recommendations.extend(effectiveness_recommendations)
            except Exception as e:
                print(f"Error predicting effectiveness: {str(e)}")
            
            # 3. Multi-objective optimization
            print("Optimizing strategy...")
            try:
                if hasattr(self, 'optimize_strategy'):
                    optimal_strategy = self.optimize_strategy(supplier_risks, inventory_status, best_cost)
                    recommendations.append(f"Optimal strategy: {optimal_strategy}")
            except Exception as e:
                print(f"Error optimizing strategy: {str(e)}")
            
            # 4. Simulation model
            print("Running simulations...")
            try:
                if hasattr(self, 'simulate_scenarios'):
                    simulation_results = self.simulate_scenarios(recommendations)
                    if isinstance(simulation_results, dict) and 'summary' in simulation_results:
                        recommendations.append(f"Simulation results: {simulation_results['summary']}")
                    else:
                        recommendations.append(f"Simulation results: {simulation_results}")
            except Exception as e:
                print(f"Error running simulations: {str(e)}")

            # 5. Collaborative filtering
            print("Finding similar situations...")
            try:
                if hasattr(self, 'find_similar_situations') and hasattr(self, 'past_situations'):
                    similar_situations = self.find_similar_situations(supplier_risks, inventory_status, best_cost)
                    if not similar_situations.empty and 'strategy' in similar_situations.columns and 'effectiveness' in similar_situations.columns:
                        best_strategy = similar_situations.loc[similar_situations['effectiveness'].idxmax(), 'strategy']
                        recommendations.append(f"Based on similar past situations, the most effective strategy might be: {best_strategy}")
            except Exception as e:
                print(f"Error finding similar situations: {str(e)}")
                    
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            print(traceback.format_exc())
            recommendations = [
                "Error generating detailed recommendations.",
                "Please check system logs for more information.",
                "Fallback recommendation: Review critical inventory levels and supplier reliability."
            ]
        
        print(f"Final recommendation count: {len(recommendations)}")
        return recommendations

    def extract_features(self, recommendation):
        features = [0, 0, 0, 0, 0]  
        
        #1: Risk severity 
        risk_keywords = {
            'high risk': 0.9, 
            'urgent': 0.8,
            'critical': 0.7,
            'significant': 0.6,
            'consider': 0.4,
            'might': 0.3
        }
        
        for keyword, severity in risk_keywords.items():
            if keyword in recommendation.lower():
                features[0] = max(features[0], severity)
        
        #2: Recommendation area
        area_keywords = {
            'supplier': 0, 
            'inventory': 1,
            'route': 2,
            'schedule': 2,
            'reorder': 1,
            'stock': 1,
            'delivery': 2,
        }
        
        for keyword, area_code in area_keywords.items():
            if keyword in recommendation.lower():
                features[1] = area_code / 2  
        
        #3: Implementation complexity
        complexity_keywords = {
            'diversify': 0.8,  
            'alternative': 0.6,
            'reduce': 0.4,
            'adjust': 0.3,
            'consider': 0.2  
        }
        
        for keyword, complexity in complexity_keywords.items():
            if keyword in recommendation.lower():
                features[2] = max(features[2], complexity)
        
        #4: Cost implication
        cost_keywords = {
            'reduce': -0.5,  
            'save': -0.7,
            'efficienc': -0.4,
            'increase': 0.6, 
            'invest': 0.7,
            'additional': 0.5
        }
        
        cost_impact = 0.5  
        for keyword, impact in cost_keywords.items():
            if keyword in recommendation.lower():
                if impact < 0:
                    cost_impact += impact  
                else:
                    cost_impact = max(cost_impact, impact) 
        features[3] = min(max(cost_impact, 0), 1)  
        
        #5: Time sensitivity
        time_keywords = {
            'urgent': 0.9,
            'immediately': 0.9,
            'soon': 0.7,
            'shortly': 0.6,
            'consider': 0.3,
            'plan': 0.2
        }
        
        for keyword, urgency in time_keywords.items():
            if keyword in recommendation.lower():
                features[4] = max(features[4], urgency)
        
        return features

    def optimize_strategy(self, supplier_risks, inventory_status, route_cost):
        def objective(x):
            return -(0.4 * x[0] + 0.3 * x[1] + 0.3 * x[2])  
        def constraint1(x):
            return np.sum(x) - 1 

        x0 = [0.33, 0.33, 0.34]  
        cons = {'type': 'eq', 'fun': constraint1}
        bounds = [(0, 1), (0, 1), (0, 1)]  

        res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=cons)

        return f"Allocate resources: {res.x[0]:.2f} to supplier management, {res.x[1]:.2f} to inventory management, {res.x[2]:.2f} to route optimization"

    def simulate_scenarios(self, recommendations):
        supplier_recs = []
        inventory_recs = []
        route_recs = []
        
        for rec in recommendations:
            rec_lower = rec.lower()
            if any(keyword in rec_lower for keyword in ['supplier', 'vendor']):
                supplier_recs.append(rec)
            elif any(keyword in rec_lower for keyword in ['inventory', 'stock', 'reorder']):
                inventory_recs.append(rec)
            elif any(keyword in rec_lower for keyword in ['route', 'delivery', 'schedule']):
                route_recs.append(rec)
        
        current_risk_level = self.calculate_current_risk_level()
        current_cost = self.calculate_current_operational_cost()
        scenarios = {}

        if supplier_recs:
            supplier_risk_reduction = min(len(supplier_recs) * 0.05, 0.3) 
            supplier_cost_impact = len(supplier_recs) * 0.03  
            
            scenarios['Scenario A: Supplier Risk Focus'] = {
                'risk_reduction': supplier_risk_reduction,
                'risk_reduction_absolute': current_risk_level * supplier_risk_reduction,
                'cost_impact': supplier_cost_impact,
                'cost_impact_absolute': current_cost * supplier_cost_impact,
                'recommendations': supplier_recs
            }
            
        if inventory_recs:
            inventory_risk_reduction = min(len(inventory_recs) * 0.04, 0.25)  
            inventory_cost_impact = -len(inventory_recs) * 0.02 
            
            scenarios['Scenario B: Inventory Optimization'] = {
                'risk_reduction': inventory_risk_reduction,
                'risk_reduction_absolute': current_risk_level * inventory_risk_reduction,
                'cost_impact': inventory_cost_impact,
                'cost_impact_absolute': current_cost * inventory_cost_impact,
                'recommendations': inventory_recs
            }
        
        if route_recs:
            route_risk_reduction = min(len(route_recs) * 0.03, 0.2)  
            route_cost_impact = -len(route_recs) * 0.04  
            
            scenarios['Scenario C: Route Optimization'] = {
                'risk_reduction': route_risk_reduction,
                'risk_reduction_absolute': current_risk_level * route_risk_reduction,
                'cost_impact': route_cost_impact,
                'cost_impact_absolute': current_cost * route_cost_impact,
                'recommendations': route_recs
            }
        
        all_recs = supplier_recs + inventory_recs + route_recs
        if len(all_recs) >= 3: 
            balanced_risk_reduction = min(len(all_recs) * 0.02, 0.35) 
            supplier_weight = len(supplier_recs) / len(all_recs)
            inventory_weight = len(inventory_recs) / len(all_recs)
            route_weight = len(route_recs) / len(all_recs)
            
            balanced_cost_impact = (
                supplier_weight * (0.03 * len(supplier_recs)) +  
                inventory_weight * (-0.02 * len(inventory_recs)) +  
                route_weight * (-0.04 * len(route_recs))  
            )
            
            scenarios['Scenario D: Balanced Approach'] = {
                'risk_reduction': balanced_risk_reduction,
                'risk_reduction_absolute': current_risk_level * balanced_risk_reduction,
                'cost_impact': balanced_cost_impact,
                'cost_impact_absolute': current_cost * balanced_cost_impact,
                'recommendations': all_recs[:3] 
            }
        best_scenario = None
        best_score = float('-inf')
        
        for name, details in scenarios.items():
            score = details['risk_reduction'] - details['cost_impact']
            if score > best_score:
                best_score = score
                best_scenario = name
        results = {
            'scenarios': scenarios,
            'best_scenario': best_scenario,
            'summary': self.format_simulation_summary(scenarios, best_scenario)
        }
        
        return results

    def calculate_current_risk_level(self):
        supplier_risks = self.risk_assessor.assess_all_supplier_risks()
        avg_supplier_risk = sum(supplier_risks.values()) / len(supplier_risks) if supplier_risks else 0.5
        inventory_risk = 0.4  
        route_risk = 0.3
        return 0.5 * avg_supplier_risk + 0.3 * inventory_risk + 0.2 * route_risk

    def calculate_current_operational_cost(self):
        return 500000 

    def format_simulation_summary(self, scenarios, best_scenario):
        if not scenarios:
            return "No viable scenarios found based on current recommendations."
        
        summary = []
        for name, details in scenarios.items():
            is_best = name == best_scenario
            risk_text = f"{details['risk_reduction']*100:.1f}% risk reduction"
            
            if details['cost_impact'] < 0:
                cost_text = f"{abs(details['cost_impact'])*100:.1f}% cost saving"
            else:
                cost_text = f"{details['cost_impact']*100:.1f}% cost increase"
            
            marker = "★ " if is_best else ""
            summary.append(f"{marker}{name}: {risk_text} with {cost_text}")
        
        if best_scenario:
            top_recs = scenarios[best_scenario]['recommendations'][:3]  
            rec_text = "\n  - " + "\n  - ".join(top_recs) if top_recs else ""
            summary.append(f"\nRecommended approach: {best_scenario}{rec_text}")
        
        return "\n".join(summary)
    
    def find_similar_situations(self, supplier_risks, inventory_status, route_cost):
        current_situation = np.array([
            np.mean(list(supplier_risks.values())),
            np.mean([status['stock_level'] for status in inventory_status.values()]),
            np.mean([status['reorder_point'] for status in inventory_status.values()]),
            route_cost
        ]).reshape(1, -1)

        past_situations_features = self.past_situations[['risk_score', 'inventory_level', 'supplier_concentration', 'route_efficiency']].values

        similarities = cosine_similarity(current_situation, past_situations_features)
        most_similar_indices = similarities.argsort()[0][-5:] 

        return self.past_situations.iloc[most_similar_indices]

    def generate_report(self):
        
        print("Generating risk mitigation report...")
        recommendations = self.generate_recommendations()
        simulation_results = self.simulate_scenarios(recommendations)
        report_sections = []
        
        current_risk = self.calculate_current_risk_level()
        risk_level_text = "High" if current_risk > 0.7 else "Medium" if current_risk > 0.4 else "Low"
        
        best_scenario = None
        if 'best_scenario' in simulation_results and simulation_results['best_scenario']:
            best_scenario = simulation_results['best_scenario']
            best_scenario_details = simulation_results['scenarios'][best_scenario]
            risk_reduction = best_scenario_details['risk_reduction'] * 100
            cost_impact = best_scenario_details['cost_impact'] * 100
            cost_text = "increase" if cost_impact > 0 else "reduction"
        
        exec_summary = [
            "EXECUTIVE SUMMARY",
            "------------------",
            f"Current Supply Chain Risk Level: {risk_level_text} ({current_risk:.2f})",
        ]
        
        if best_scenario:
            exec_summary.extend([
                f"Recommended Approach: {best_scenario}",
                f"Expected Outcome: {risk_reduction:.1f}% risk reduction with {abs(cost_impact):.1f}% cost {cost_text}",
                f"Implementation Priority: {'High' if current_risk > 0.6 else 'Medium'}"
            ])
        else:
            exec_summary.append("No recommended action at this time - maintain current operations")
        
        report_sections.append("\n".join(exec_summary))
    
        supplier_risks = self.risk_assessor.assess_all_supplier_risks()
        avg_supplier_risk = sum(supplier_risks.values()) / len(supplier_risks) if supplier_risks else 0
        
        highest_risk_supplier = max(supplier_risks.items(), key=lambda x: x[1]) if supplier_risks else (None, 0)
        
        risk_summary = [
            "\nRISK ASSESSMENT SUMMARY",
            "-----------------------",
            f"Average Supplier Risk: {avg_supplier_risk:.2f}",
        ]
        
        if highest_risk_supplier[0]:
            risk_summary.append(f"Highest Risk Supplier: {highest_risk_supplier[0]} (Score: {highest_risk_supplier[1]:.2f})")
        
        risk_summary.extend([
            "Inventory Risk Areas:",
            "  - Stock-out Risk: Medium",
            "  - Expiration Risk: Low",
            "  - Critical Item Availability: High",
            "",
            "Logistics Risk Areas:",
            "  - Route Disruption Risk: Medium",
            "  - Weather Impact Risk: Low",
            "  - Transit Time Variability: Medium"
        ])
        
        report_sections.append("\n".join(risk_summary))

        mitigation_strategies = [
            "\nRECOMMENDED MITIGATION STRATEGIES",
            "----------------------------------"
        ]
        
        if recommendations:
            for i, rec in enumerate(recommendations[:10], 1):  
                features = self.extract_features(rec)
                effectiveness = self.ml_model.predict([features])[0]
                effectiveness_text = "High" if effectiveness > 0.7 else "Medium" if effectiveness > 0.4 else "Low"
                
                mitigation_strategies.append(f"{i}. {rec}")
                mitigation_strategies.append(f"   Projected Effectiveness: {effectiveness_text} ({effectiveness:.2f})")
                mitigation_strategies.append("")
        else:
            mitigation_strategies.append("No specific mitigation strategies recommended at this time.")
        
        report_sections.append("\n".join(mitigation_strategies))
    
        if 'summary' in simulation_results:
            scenario_analysis = [
                "\nSCENARIO ANALYSIS",
                "----------------_",
                simulation_results['summary']
            ]
            report_sections.append("\n".join(scenario_analysis))

        if best_scenario and 'scenarios' in simulation_results:
            best_scenario_recs = simulation_results['scenarios'][best_scenario]['recommendations']
            
            implementation_plan = [
                "\nIMPLEMENTATION PLAN",
                "------------------_",
                f"For: {best_scenario}",
                ""
            ]
            
            for i, rec in enumerate(best_scenario_recs[:5], 1): 
                timeframe = "Immediate" if i <= 2 else "Within 1 month" if i <= 4 else "Within 3 months"
                implementation_plan.extend([
                    f"Action {i}: {rec}",
                    f"Timeframe: {timeframe}",
                    f"Responsible: {'Supply Chain Manager' if 'supplier' in rec.lower() else 'Inventory Manager' if 'inventory' in rec.lower() else 'Logistics Manager'}",
                    ""
                ])
            
            implementation_plan.extend([
                "Monitoring Plan:",
                "- Review implementation progress weekly",
                "- Measure effectiveness using KPIs:",
                "  * Supplier reliability scores",
                "  * Inventory service levels",
                "  * On-time delivery rates",
                "  * Total supply chain cost"
            ])
            
            report_sections.append("\n".join(implementation_plan))

        conclusion = [
            "\nCONCLUSION",
            "------------",
            "This risk mitigation report identifies key supply chain vulnerabilities and recommends",
            "targeted strategies to strengthen resilience while optimizing operational costs.",
        ]
        
        if best_scenario:
            conclusion.extend([
                "",
                f"By implementing the {best_scenario.lower()}, the organization can expect to:",
                f"- Reduce overall supply chain risk by approximately {risk_reduction:.1f}%",
                f"- {'Increase' if cost_impact > 0 else 'Reduce'} operational costs by approximately {abs(cost_impact):.1f}%",
                "- Improve overall supply chain resilience against future disruptions"
            ])
        
        conclusion.extend([
            "",
            "Regular reassessment is recommended as supply chain conditions evolve.",
            "",
            f"Report generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"
        ])
        
        report_sections.append("\n".join(conclusion))
   
        report = "\n\n" + "\n\n".join(report_sections)
        
        print("Report generation complete.")
        return report

