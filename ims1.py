import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from neuralprophet import NeuralProphet
import pickle
import warnings
import traceback
import random
import plotly.graph_objs as go
import plotly
      
warnings.filterwarnings('ignore')
warnings.filterwarnings("ignore", category=UserWarning)
        
class InventoryManagementSystem:
    def __init__(self, n_products=500, n_days=365):
        self.n_products = n_products
        self.n_days = n_days
        self.product_names = self.generate_product_names()
        self.inventory_data = self.create_synthetic_data()
        self.forecast_models = {}
        
    def generate_product_names(self):
        categories = [  # Pharmaceuticals
                        "Antibiotic", "Painkiller", "Insulin Pen", "Antiviral Drug", "Blood Thinner", 
                        "Cough Syrup", "Sedative", "Hormone Injection", "Vitamin Supplement", 
                        "IV Fluid", "Anesthetic Agent", "Antihistamine", "Steroid Injection",

                        # Medical Equipment
                        "Stethoscope", "Blood Pressure Monitor", "ECG Machine", "Defibrillator", 
                        "Ventilator", "Oxygen Cylinder", "Ultrasound Machine", "X-Ray Machine", 
                        "MRI Scanner", "CT Scanner", "Endoscope", "Laryngoscope", "Nebulizer", 
                        "Dialysis Machine", "Infusion Pump", "Patient Monitor",

                        # Surgical Instruments
                        "Scalpel", "Surgical Sutures", "Forceps", "Hemostats", "Retractor", 
                        "Bone Saw", "Cautery Machine", "Surgical Drill", "Laparoscope", 
                        "Electrosurgical Pencil", "Trocars", "Surgical Stapler", "Speculum",

                        # Diagnostic & Lab Supplies
                        "Blood Glucose Monitor", "Urine Test Strips", "Specimen Container", 
                        "Test Tubes", "Petri Dish", "Microscope Slides", "Centrifuge", 
                        "Biopsy Needle", "Pipette", "Culture Media", "ELISA Kit", "PCR Kit",

                        # Wound Care & First Aid
                        "Sterile Dressing", "Bandage", "Gauze Pads", "Adhesive Tape", "Wound Cleanser", 
                        "Antiseptic Solution", "Compression Bandage", "Tourniquet", "Cotton Swabs", 
                        "Wound Closure Strips",

                        # Personal Protective Equipment (PPE)
                        "Face Mask", "N95 Respirator", "Surgical Cap", "Medical Gown", "Gloves", 
                        "Face Shield", "Shoe Covers", "Protective Apron",

                        # Intravenous (IV) Supplies
                        "IV Cannula", "IV Drip Set", "IV Tubing", "Syringe", "Needles", "Infusion Bag",

                        # Orthopedic & Rehabilitation
                        "Crutches", "Wheelchair", "Walking Stick", "Orthopedic Brace", 
                        "Compression Stockings", "Neck Collar", "Arm Sling", "Splints", 
                        "Knee Brace", "Physiotherapy Equipment",

                        # Disposable & Consumables
                        "Medical Waste Bags", "Sanitary Napkins", "Incontinence Pads", 
                        "Sterilization Pouch", "Disposable Bedsheets", "Surgical Blades", 
                        "Dental Bibs", "Gown Covers",

                        # Miscellaneous Hospital Supplies
                        "Hearing Aid", "Dental Drill", "Suction Machine", "Otoscope", 
                        "Thermometer", "Pulse Oximeter", "Anesthesia Machine", "Hospital Bed", 
                        "Trolley", "Sterilizer", "Bedpan", "Urine Collection Bag", "Catheter",

                        # Emergency & Trauma Supplies
                        "Ambu Bag", "Splint Kit", "Burn Dressing", "Emergency Oxygen Kit", 
                        "Hemostatic Dressing", "Trauma Shears", "Emergency Blanket",
                    ]
        
        
        product_names = {i: f"{random.choice(categories)}-{i}" for i in range(1, self.n_products + 1)}
        return product_names    
    
    def create_synthetic_data(self):
        start_date = datetime(2022, 1, 1)
        dates = [start_date + timedelta(days=i) for i in range(self.n_days)]  
        data = []
        for product_id in range(1, self.n_products + 1):
            product_name = self.product_names[product_id]
            base_demand = np.random.randint(50, 150)  
            trend = np.random.uniform(-0.2, 0.2)  
            seasonality = np.random.uniform(10, 30)  
            noise = np.random.normal(0, 10, self.n_days) 
            
            for i, date in enumerate(dates):
                
                seasonal_factor = np.sin(2 * np.pi * i / 365) + np.sin(2 * np.pi * i / 30)  
                demand = max(1, int(base_demand * (1 + trend * i/365) + seasonality * seasonal_factor + noise[i]))
                min_stock = max(1, int(demand * 0.8))  
                max_stock = int(demand * 2.5)  
                stock_level = np.random.randint(min_stock, max_stock)
                shelf_life = np.random.randint(30, 365)
                expiry_date = date + timedelta(days=shelf_life)
                criticality = np.random.randint(1, 6)
                
                data.append({
                    'date': date,
                    'product_id': product_id,
                    'product_name': product_name,
                    'demand': demand,
                    'stock_level': stock_level,
                    'shelf_life': shelf_life,
                    'expiry_date': expiry_date,
                    'criticality': criticality
                })
        
        return pd.DataFrame(data)

    def train_forecast_models(self):
        for product_id in range(1, self.n_products + 1):
            product_data = self.inventory_data[self.inventory_data['product_id'] == product_id]
            prophet_data = pd.DataFrame({
                'ds': product_data['date'],
                'y': product_data['demand']
            })
            model = NeuralProphet(
                growth="linear",
                n_forecasts=30,
                n_lags=14,
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                batch_size=32,
                epochs=50,
                learning_rate=1e-3
            )
            
            print(f"\nTraining model for product {product_id}...")  
            metrics = model.fit(prophet_data, freq='D')
            self.forecast_models[product_id] = model  
            with open("neuralprophet_model.pkl", "wb") as file:
                pickle.dump(model, file)
            print(f"Completed training for product {product_id}")
        print
        
    def forecast_demand(self, product_id, days=30):
        if product_id not in self.forecast_models:
                self.train_forecast_models()
            
        model = self.forecast_models[product_id]
        product_data = self.inventory_data[
            self.inventory_data['product_id'] == product_id
        ][['date', 'demand']].rename(
            columns={'date': 'ds', 'demand': 'y'}
        )
    
        future_df = model.make_future_dataframe(product_data, periods=days)
        forecast = model.predict(future_df)
        print(f"\nTraining model for product {product_id} ({self.product_names[product_id]})...")
        forecast_values = []
        for i in range(1, days+1):
            col_name = f'yhat{i}'
            if col_name in forecast.columns:
                last_valid = forecast[col_name].dropna().iloc[-1] if not forecast[col_name].dropna().empty else None
                if last_valid is not None:
                    forecast_values.append(float(last_valid))
        
        print(f"Generated {len(forecast_values)} forecast values")
        
        if len(forecast_values) >= days:
            return np.array(forecast_values)
        
        elif 'yhat1' in forecast.columns:
            return forecast['yhat1'].dropna().values[-days:]
        
        else:
            print("WARNING: Using fallback synthetic forecast data")
            last_demand = product_data['y'].mean()
            return np.array([last_demand + np.random.normal(0, last_demand * 0.1) for _ in range(days)])
        
    def optimize_stock_levels(self, product_id, target_service_level=0.95):
     
        product_data = self.inventory_data[self.inventory_data['product_id'] == product_id]   
        if product_data.empty:
            raise ValueError(f"No data found for product {product_id}")

        avg_daily_demand = product_data['demand'].mean()
        demand_std = product_data['demand'].std()
        lead_time = 7  
        z_score = 1.645 
        ordering_cost = 100  
        holding_cost_rate = 0.2 
        safety_stock = z_score * demand_std * np.sqrt(lead_time)  
        reorder_point = (avg_daily_demand * lead_time) + safety_stock
        annual_demand = avg_daily_demand * 365
        avg_unit_cost = 100 
        economic_order_quantity = np.sqrt(
            (2 * annual_demand * ordering_cost) / 
            (holding_cost_rate * avg_unit_cost)
        )

        return {
            'product_id': product_id,
            'product_name': self.product_names[product_id],
            'reorder_point': float(reorder_point),
            'economic_order_quantity': float(economic_order_quantity),
            'safety_stock': float(safety_stock),
            'avg_daily_demand': float(avg_daily_demand),
            'demand_std': float(demand_std)
        }

    def generate_alerts(self):
    
        current_date = datetime.now()
        alerts = []
        
        for product_id in range(1, self.n_products + 1):
            product_data = self.inventory_data[self.inventory_data['product_id'] == product_id]
            
            if product_data.empty:
                continue
                
            latest_data = product_data.iloc[-1]  
            avg_demand = product_data['demand'].mean()
            stock_days = latest_data['stock_level'] / avg_demand if avg_demand > 0 else float('inf')  
            if stock_days < 7: 
                alerts.append(
                    f"Low stock alert: {latest_data['product_name']} (ID: {product_id}) - "
                    f"Current stock: {int(latest_data['stock_level'])} "
                    f"({avg_demand:.1f}/day, {stock_days:.1f} days remaining)"
                )   
            if current_date + timedelta(days=30) > latest_data['expiry_date']:
                days_to_expiry = (latest_data['expiry_date'] - current_date).days
                if days_to_expiry > 0:  
                    alerts.append(
                        f"Expiry alert: Product {product_id} - "
                        f"Expires in {days_to_expiry} days"
                    )       
            if latest_data['criticality'] >= 4 and stock_days < 14: 
                alerts.append(
                    f"Critical item alert: Product {product_id} - "
                    f"High criticality item running low"
                )

        return alerts
    
    def visualize_forecast(self, product_id, forecast):
        try:
            actual_data = self.inventory_data[self.inventory_data['product_id'] == product_id]
            
            if actual_data.empty:
                print(f"No actual data found for product_id {product_id}")
                return "{}"
                
            product_name = self.product_names.get(product_id, f"Product {product_id}")
            last_date = actual_data['date'].max()
            forecast_dates = [(last_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, len(forecast) + 1)]
            
            actual_trace = go.Scatter(
                x=actual_data['date'].astype(str).tolist(),
                y=actual_data['demand'].tolist(),
                name="Historical Demand",
                line=dict(color='blue', width=2)
            )
            
            forecast_trace = go.Scatter(
                x=forecast_dates,
                y=forecast.tolist() if hasattr(forecast, 'tolist') else list(forecast),
                name="Forecast",
                line=dict(color='red', width=2, dash='dot')
            )
            
            forecast_values = forecast.tolist() if hasattr(forecast, 'tolist') else list(forecast)
            lower_bound = [max(0, value * 0.8) for value in forecast_values]
            upper_bound = [value * 1.2 for value in forecast_values]
            
            ci_trace = go.Scatter(
                x=forecast_dates + forecast_dates[::-1],
                y=upper_bound + lower_bound[::-1],
                fill='toself',
                fillcolor='rgba(231,107,243,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name="80-120% Confidence"
            )
            
            data = [actual_trace, ci_trace, forecast_trace]
            layout = go.Layout(
                title=f"Demand Forecast for {product_name}",
                xaxis=dict(title="Date"),
                yaxis=dict(title="Demand"),
                hovermode="x unified",
                template="plotly_white"
            )
            fig = go.Figure(data=data, layout=layout)
            json_data = fig.to_json()
            
            return json_data
            
        except Exception as e:
            print(f"Error in visualization: {str(e)}")
            print(traceback.format_exc())
            return "{}"
            
    def get_inventory_status(self):
 
        current_date = max(self.inventory_data['date'])
        latest_data = self.inventory_data[self.inventory_data['date'] == current_date]
        
        inventory_status = {}
        for _, row in latest_data.iterrows():
            product_id = row['product_id']
        
            product_data = self.inventory_data[self.inventory_data['product_id'] == product_id]
            avg_demand = product_data['demand'].mean()
        
            days_remaining = float('inf') if avg_demand == 0 else row['stock_level'] / avg_demand
            
            try:
                optimization = self.optimize_stock_levels(product_id)
                reorder_point = optimization['reorder_point']
            except:
                reorder_point = avg_demand * 7 
            
            inventory_status[self.product_names[product_id]] = {
                'product_name': row['product_name'],
                'stock_level': row['stock_level'],
                'reorder_point': reorder_point,
                'days_remaining': days_remaining,
                'criticality': row['criticality'],
                'expiry_date': row['expiry_date'].strftime('%Y-%m-%d') if hasattr(row['expiry_date'], 'strftime') else str(row['expiry_date'])
            }
        
        return inventory_status
    
    def get_supplier_concentration(self):
        
        supplier_concentration = {}
        np.random.seed(42) 
        
        for product_id in range(1, self.n_products + 1):
            n_suppliers = max(1, int(np.random.exponential(2)))
            n_suppliers = min(n_suppliers, 5) 
            
            if n_suppliers == 1:
                concentration = 1.0
            else:
                market_shares = np.random.dirichlet(np.ones(n_suppliers))
                concentration = sum(share**2 for share in market_shares)
                concentration = (concentration - 1/n_suppliers) / (1 - 1/n_suppliers)
            
            supplier_concentration[self.product_names[product_id]] = concentration
        
        return supplier_concentration

    def get_route_efficiency(self):

        np.random.seed(42)  
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        dates = [start_date + timedelta(days=i) for i in range(31)]
        
        base_efficiency = np.random.normal(0.8, 0.05, len(dates))
        base_efficiency = np.clip(base_efficiency, 0, 1)  

        weekday_effect = np.array([
            -0.05 if d.weekday() < 5 else 0.05 for d in dates
        ])
        
        disruption_day = np.random.randint(7, 25)  
        disruption_effect = np.zeros(len(dates))
        disruption_length = np.random.randint(2, 5)  
        
        for i in range(disruption_length):
            if disruption_day + i < len(disruption_effect):
                disruption_effect[disruption_day + i] = -0.2 * (disruption_length - i) / disruption_length
        
        efficiency = base_efficiency + weekday_effect + disruption_effect
        efficiency = np.clip(efficiency, 0, 1) 
        
        base_cost = 1000
        cost = base_cost * (2 - efficiency)
        
        base_time = 120  
        time = base_time * (2 - efficiency)
        
        route_data = pd.DataFrame({
            'date': dates,
            'efficiency': efficiency,
            'cost': cost,
            'time': time
        })
        
        return route_data
    
class InventoryRLAgent:
        def __init__(self, n_products, n_states=10, n_actions=10):
            self.n_products = n_products
            self.n_states = n_states
            self.n_actions = n_actions
            self.q_table = np.zeros((n_products, n_states, n_actions))
            self.learning_rate = 0.1
            self.discount_factor = 0.95
            self.epsilon = 0.1
            
            self.action_meanings = {
            0: "No order needed",
            1: "Order small quantity (25% of max)",
            2: "Order medium quantity (50% of max)",
            3: "Order large quantity (75% of max)",
            4: "Order maximum quantity"
        }

        def get_state_index(self, stock_level, max_stock=1000):
            state_size = max_stock / self.n_states
            return min(int(stock_level / state_size), self.n_states - 1)

        def get_action(self, product_id, stock_level):
           
            state = self.get_state_index(stock_level)
                   
            if np.random.random() < self.epsilon:
                action_idx = np.random.randint(0, self.n_actions)
            else:
                action_idx = np.argmax(self.q_table[product_id-1, state])
    
            max_order = 1000
            order_quantity = 0
            if action_idx > 0:
                order_quantity = (action_idx * 0.25) * max_order
                
            return {
                'action_idx': action_idx, 
                'action_meaning': self.action_meanings[action_idx],
                'order_quantity': int(order_quantity)
            }

        def update_q_table(self, product_id, stock_level, action_info, reward, next_stock_level):
            state = self.get_state_index(stock_level)
            next_state = self.get_state_index(next_stock_level)
            action_idx = action_info['action_idx']
            old_value = self.q_table[product_id-1, state, action_idx]
            next_max = np.max(self.q_table[product_id-1, next_state])
            new_value = (1 - self.learning_rate) * old_value + \
                        self.learning_rate * (reward + self.discount_factor * next_max)
            
            self.q_table[product_id-1, state, action_idx] = new_value
            
            return new_value

ims = InventoryManagementSystem(n_products=10, n_days=365)
first_day_data = ims.inventory_data[ims.inventory_data['date'] == '2022-01-01']
print(first_day_data.head(10)) 
rl_agent = InventoryRLAgent(n_products=10)

ims.train_forecast_models()

product_id = 1
forecast = ims.forecast_demand(product_id)

optimization_result = ims.optimize_stock_levels(product_id)
print("\nStock level optimization result:")
print(optimization_result)

alerts = ims.generate_alerts()
print("\nAlerts:")
for alert in alerts[:5]:  
    print(alert)
    
product_id = 1
current_stock = 5
action_info = rl_agent.get_action(product_id, current_stock)
print(f"\nRL Agent recommended action for product {product_id} with stock level {current_stock}: {action_info}")

reward = 1  
next_stock = 6  
rl_agent.update_q_table(product_id, current_stock, action_info, reward, next_stock)

