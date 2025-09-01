from flask import Flask, render_template, request, jsonify
from dashboard import create_dash_app
import visual as viz
from main_sys import HospitalSupplyChainSystem
import numpy as np
import traceback
from geopy.distance import geodesic
import plotly.graph_objs as go
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 
system = HospitalSupplyChainSystem()

create_dash_app(app, system)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_report')
def generate_report():
    try:
        report = system.risk_mitigator.generate_report()
        return jsonify({"report": report})
    except Exception as e:
        return jsonify({"error": f"Error generating report: {str(e)}"})

@app.route('/inventory_status')
def inventory_status():
    try:
        status = system.get_inventory_status()
        chart = viz.create_inventory_chart(status)
        return jsonify({"chart": chart})
    except Exception as e:
        return jsonify({"error": f"Error getting inventory status: {str(e)}"})

@app.route('/supplier_risks')
def supplier_risks():
    try:
        risks = system.risk_assessor.assess_all_supplier_risks()
        chart = viz.create_risk_heatmap(risks)
        
        monte_carlo_results = system.risk_assessor.monte_carlo_simulation(1)
        
        return jsonify({
            "chart": chart, 
            "monte_carlo_chart": monte_carlo_results['chart'],
            "monte_carlo_stats": {
                "mean_lead_time": monte_carlo_results['mean_lead_time'],
                "confidence_interval": monte_carlo_results['95%_confidence_interval']
            }
        })
    except Exception as e:
        return jsonify({"error": f"Error assessing supplier risks: {str(e)}"})

@app.route('/optimized_route')
def optimized_route():
    try:
        best_route, best_cost, route_details = system.route_optimizer.optimize_route()
        
        print(f"Optimized route retrieved with {len(best_route) if best_route else 0} points and cost {best_cost}")
        
        if not best_route or len(best_route) < 2:
            return jsonify({
                "error": "Invalid route data returned",
                "map": generate_fallback_map_html("Invalid route data")
            })
            
        map_html = system.route_optimizer.visualize_route(best_route, route_details)
        metrics = calculate_route_metrics(best_route, best_cost)
        
        if route_details:
            if 'distance_km' in route_details:
                metrics['distance_km'] = route_details['distance_km']
            if 'time_mins' in route_details:
                metrics['estimated_time_min'] = route_details['time_mins']
        
        print(f"Route map created successfully: {len(map_html) if map_html else 0} characters")
        
        return jsonify({
            "map": map_html, 
            "cost": best_cost,
            "metrics": metrics,
            "follows_roads": len(best_route) > 2 
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error optimizing route: {error_details}")
        
        return jsonify({
            "error": f"Error optimizing route: {str(e)}",
            "map": generate_fallback_map_html(f"Error: {str(e)}")
        })
        
@app.route('/demand_forecast')
def demand_forecast():
    try:
        product_id = int(request.args.get('product_id', 1))
        forecast = system.inventory_system.forecast_demand(product_id, days=30)
        

        print(f"Forecast for product {product_id}:")
        print(f"  Type: {type(forecast)}")
        print(f"  Shape/Length: {forecast.shape if hasattr(forecast, 'shape') else len(forecast)}")
        print(f"  First few values: {forecast[:5]}")
        
        chart_data = system.inventory_system.visualize_forecast(product_id, forecast)
        forecast_array = forecast.to_numpy() if hasattr(forecast, 'to_numpy') else np.array(forecast)

        stats = {
            'mean': float(np.mean(forecast_array)),
            'min': float(np.min(forecast_array)),
            'max': float(np.max(forecast_array)),
            'total': float(np.sum(forecast_array)),
            'days': len(forecast_array)
        }
        
        print(f"Stats calculated: {stats}")
        
        return jsonify({
            "chart": chart_data, 
            "forecast": forecast_array.tolist(),
            "stats": stats,
            "product_id": product_id
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating demand forecast: {error_details}")
        
        return jsonify({"error": f"Error generating demand forecast: {str(e)}"})

def create_fallback_chart(product_id, forecast):
    try:
        days = [f"Day {i+1}" for i in range(len(forecast))]
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=days,
            y=forecast,
            mode='lines+markers',
            name='Forecast',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title=f"Demand Forecast for Product {product_id}",
            xaxis_title="Day",
            yaxis_title="Predicted Demand",
            template="plotly_white"
        )
        
        return fig.to_json()
        
    except Exception as e:
        print(f"Error creating fallback chart: {str(e)}")
        return "{}"
        
def generate_fallback_map_html(message):
    return f"""
    <div style="width:800px; height:600px; 
               display:flex; align-items:center; justify-content:center; 
               border: 1px solid #ddd; background-color: #f8f9fa;">
        <div style="text-align:center;">
            <h3>Route Visualization Unavailable</h3>
            <p>{message}</p>
            <p>Please try again or view the dashboard for more information.</p>
        </div>
    </div>
    """
    
def calculate_route_metrics(route, cost):
    try:
        total_distance = 0
        for i in range(len(route) - 1):
            point1 = route[i]
            point2 = route[i + 1]
            segment_distance = geodesic(point1, point2).kilometers
            total_distance += segment_distance
            
        estimated_time = total_distance / 30 * 60 
        fuel_usage = total_distance / 10
        co2_emissions = fuel_usage * 2.3
        
        return {
            "distance_km": round(total_distance, 2),
            "estimated_time_min": round(estimated_time),
            "fuel_usage_liters": round(fuel_usage, 2),
            "co2_emissions_kg": round(co2_emissions, 2),
            "cost_per_km": round(cost / total_distance if total_distance > 0 else 0, 2)
        }
    except:
        return {
            "distance_km": "N/A",
            "estimated_time_min": "N/A",
            "cost": cost
        }

@app.route('/medicine_classification')
def medicine_classification():
    try:
        if not hasattr(system, 'classify_medicines'):
            return jsonify({"error": "Medicine classification not available in system"})
        
        classification = system.classify_medicines()
        
        print(f"Classification completed successfully with {len(classification) if classification else 0} categories")
        
        return jsonify({"classification": classification})
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error classifying medicines: {error_details}")
        
        return jsonify({"error": f"Error classifying medicines: {str(e)}"})

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        "status": "online",
        "components": {
            "inventory_system": "operational",
            "risk_assessment": "operational",
            "route_optimization": "operational",
            "medicine_classification": "operational"
        },
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(debug=False)