# Hospital Supply Chain Management System

An intelligent **hospital supply chain management system** that integrates machine learning, optimization, and visualization to improve decision-making in medical supply logistics.

## 📌 Project Overview
This application provides a unified platform for:
- **Medicine Classification**: Categorize and prioritize medicines using clustering and TF-IDF.
- **Inventory Management**: Monitor stock levels, forecast demand, and generate alerts.
- **Risk Assessment**: Identify supplier risks via anomaly detection and Monte Carlo simulation.
- **Route Optimization**: Optimize supply routes using **TomTom API**, geolocation, and weather data.
- **Risk Mitigation**: Generate data-driven recommendations using **rule-based + ML strategies**.
- **Visualization**: Interactive charts, heatmaps, and maps via **Plotly, Dash, and Folium**.

## 🛠️ Features
- **Flask API** endpoints for report generation, inventory, risk, routes, forecasts, and medicine classification.
- **Dash Dashboard** for interactive monitoring of inventory, supplier risks, categories, and route efficiency.
- **Machine Learning** models (KMeans, RandomForest, IsolationForest) for clustering, prediction, and anomaly detection.
- **Simulation & Optimization** for supply chain resilience.

## 📂 Project Structure
```
├── app.py                # Flask app entry point
├── dashboard.py          # Dash dashboard integration
├── main_sys.py           # Core system orchestrator
├── classifier.py         # Medicine classification module
├── risk_assess.py        # Supplier risk assessment
├── mitigation_rec.py     # Risk mitigation strategies
├── route_opt.py          # Route optimization with APIs
├── visual.py             # Visualization utilities
├── config.py             # Config file (API keys, dataset paths)
├── hbmodelf.ipynb        # Demand forecasting notebook
├── datasets/             # Medicine, supply chain, and inventory data
```

## ⚙️ Requirements
Install dependencies:
```bash
pip install flask dash plotly pandas numpy scikit-learn folium geopy requests flask-cors
```

Additional requirements:
- **API Keys** (configured in `config.py`):
  - OpenWeatherMap API key
  - TomTom API key

## 🚀 Usage
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/hospital-supply-chain.git
   cd hospital-supply-chain
   ```

2. Update `config.py` with your dataset paths and API keys.

3. Run the application:
   ```bash
   python app.py
   ```

4. Access endpoints:
   - API: `http://127.0.0.1:5000/`
   - Dashboard: `http://127.0.0.1:5000/dashboard/`

## 📊 Core Modules
- **Medicine Classifier** (`classifier.py`): Clusters and assigns categories to medicines.
- **Inventory System**: Tracks stock levels, forecasts demand.
- **Risk Assessment** (`risk_assess.py`): Calculates supplier risks and simulates disruptions.
- **Route Optimizer** (`route_opt.py`): Optimizes supply routes considering traffic & weather.
- **Risk Mitigator** (`mitigation_rec.py`): Generates strategic recommendations.
- **Visualization** (`visual.py`): Interactive graphs and maps.

## 📈 Example Visuals
- Inventory bar charts
- Supplier risk heatmaps
- Demand forecast curves with confidence bands
- Interactive route maps (Folium)

## 🤝 Contributing
Contributions are welcome! Please fork the repo, create a branch, and submit a PR.

## 📜 License
This project is licensed under the MIT License.

