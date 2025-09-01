import plotly.graph_objects as go
import plotly.express as px
import folium
import plotly.graph_objects as go
import plotly.io
from datetime import datetime, timedelta
import traceback
import random
from branca.element import Figure
from geopy.distance import geodesic
import math


def create_inventory_chart(inventory_status):
    products = list(inventory_status.keys())
    stock_levels = [status['stock_level'] for status in inventory_status.values()]
    reorder_points = [status['reorder_point'] for status in inventory_status.values()]

    fig = go.Figure(data=[
        go.Bar(name='Stock Level', x=products, y=stock_levels),
        go.Bar(name='Reorder Point', x=products, y=reorder_points)
    ])

    fig.update_layout(barmode='group', title='Inventory Status')
    return fig.to_json()

def create_risk_heatmap(supplier_risks):
    suppliers = list(supplier_risks.keys())
    risk_scores = list(supplier_risks.values())

    fig = px.imshow([risk_scores], x=suppliers, y=['Risk Score'],
                    color_continuous_scale='RdYlGn_r', aspect='auto')
    fig.update_layout(title='Supplier Risk Heatmap')
    return fig.to_json()
def create_forecast_chart(forecast_data, product_id, historical_data=None):

    try:
        current_date = datetime.now()
        forecast_dates = [(current_date + timedelta(days=i)).strftime("%Y-%m-%d") 
                         for i in range(len(forecast_data))]
        
        fig = go.Figure()
        
        if historical_data is not None and not historical_data.empty:
            historical_dates = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d) 
                              for d in historical_data['date']]
            
            fig.add_trace(
                go.Scatter(
                    x=historical_dates,
                    y=historical_data['demand'],
                    mode='lines',
                    name='Historical Demand',
                    line=dict(color='#1f77b4', width=2)
                )
            )
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_data,
                mode='lines+markers',
                name='Forecast',
                line=dict(color='#ff7f0e', width=2, dash='dot'),
                marker=dict(size=6)
            )
        )
        lower_bound = [max(0, val * 0.8) for val in forecast_data]
        upper_bound = [val * 1.2 for val in forecast_data]
        
        fig.add_trace(
            go.Scatter(
                x=forecast_dates + forecast_dates[::-1],
                y=upper_bound + lower_bound[::-1],
                fill='toself',
                fillcolor='rgba(255,127,14,0.2)',
                line=dict(color='rgba(255,127,14,0)'),
                hoverinfo='skip',
                showlegend=False
            )
        )
        fig.update_layout(
            title=f"Demand Forecast for Product {product_id}",
            xaxis_title="Date",
            yaxis_title="Demand",
            hovermode='x unified',
            template='plotly_white',
            autosize=True,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        trend = "Increasing" if forecast_data[-1] > forecast_data[0] else "Decreasing" if forecast_data[-1] < forecast_data[0] else "Stable"
        trend_color = "#28a745" if trend == "Increasing" else "#dc3545" if trend == "Decreasing" else "#17a2b8"
        
        fig.add_annotation(
            x=0.02,
            y=0.98,
            xref="paper",
            yref="paper",
            text=f"Trend: {trend}",
            showarrow=False,
            font=dict(
                family="Arial",
                size=14,
                color=trend_color
            ),
            align="left",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.3)",
            borderwidth=1,
            borderpad=4,
            borderradius=5
        )
        
        seasonal_pattern = "Weekly" if sum(forecast_data) > 0 else "None detected"
        if seasonal_pattern != "None detected":
            fig.add_annotation(
                x=0.02,
                y=0.92,
                xref="paper",
                yref="paper",
                text=f"Pattern: {seasonal_pattern}",
                showarrow=False,
                font=dict(
                    family="Arial",
                    size=14,
                    color="#17a2b8"
                ),
                align="left",
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.3)",
                borderwidth=1,
                borderpad=4,
                borderradius=5
            )
        return plotly.io.to_json(fig)
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error creating forecast chart: {error_details}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating forecast chart: {str(e)}",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(title='Error Creating Forecast Chart')
        return plotly.io.to_json(fig)
    
def create_route_map(route):
    try:
        if not route or len(route) < 2:
            default_center = [10.8505, 76.2711] 
            fig = Figure(width=800, height=600)
            m = folium.Map(location=default_center, zoom_start=8, tiles="OpenStreetMap")
            fig.add_child(m)
            
            folium.Marker(
                default_center,
                popup="No route data available",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
            
            return m._repr_html_()

        enhanced_route = []
        for i in range(len(route) - 1):
            start = route[i]
            end = route[i + 1]
            enhanced_route.append(start)
            num_points = 3 
            for j in range(1, num_points + 1):
                frac = j / (num_points + 1)
                lat = start[0] + frac * (end[0] - start[0])
                lon = start[1] + frac * (end[1] - start[1])
                lat_variation = random.uniform(-0.005, 0.005)
                lon_variation = random.uniform(-0.005, 0.005)           
                enhanced_route.append((lat + lat_variation, lon + lon_variation))
        enhanced_route.append(route[-1])

        lats = [point[0] for point in route]
        lons = [point[1] for point in route]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        padding = 0.05  
        bounds = [
            [min_lat - padding, min_lon - padding],
            [max_lat + padding, max_lon + padding]
        ]
        
        fig = Figure(width=800, height=600)
        m = folium.Map(location=route[0], zoom_start=10)
        fig.add_child(m)
    
        folium.PolyLine(
            enhanced_route,
            weight=4,
            color='blue',
            opacity=0.8,
            dash_array='5, 10'
        ).add_to(m)
        
        folium.Marker(
            route[0],
            popup="Start: Hospital",
            icon=folium.Icon(color="green", icon="hospital", prefix='fa')
        ).add_to(m)
    
        folium.Marker(
            route[-1],
            popup="Destination: Supplier",
            icon=folium.Icon(color="red", icon="industry", prefix='fa')
        ).add_to(m)

        for i, point in enumerate(route[1:-1], 1):
            folium.CircleMarker(
                point,
                radius=5,
                color='#3186cc',
                fill=True,
                fill_color='#3186cc'
            ).add_to(m)
        total_distance = calculate_route_distance(route)

        distance_html = f"""
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 90px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color: white; padding: 8px; border-radius: 5px;">
            <b>Route Information:</b><br>
            Distance: {total_distance:.2f} km<br>
            Stops: {len(route)}<br>
            Estimated Time: {int(total_distance * 2)} min
        </div>
        """
        m.get_root().html.add_child(folium.Element(distance_html))
        m.fit_bounds(bounds)
        return m._repr_html_()
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error creating route map: {error_details}")
        error_html = f"""
        <div style="width:800px; height:600px; 
                   display:flex; align-items:center; justify-content:center; 
                   border: 1px solid #ddd; background-color: #f8f9fa;">
            <div style="text-align:center;">
                <h3 style="color:red;">Error Creating Route Map</h3>
                <p>{str(e)}</p>
                <p>Please try again or contact support.</p>
            </div>
        </div>
        """
        return error_html
    
def calculate_route_distance(route):
    try:
        total_distance = 0
        for i in range(len(route) - 1):
            point1 = route[i]
            point2 = route[i + 1]
            segment_distance = geodesic(point1, point2).kilometers
            total_distance += segment_distance
            
        return total_distance
    except:
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371 
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            distance = R * c
            
            return distance
        total_distance = 0
        for i in range(len(route) - 1):
            point1 = route[i]
            point2 = route[i + 1]
            segment_distance = haversine(point1[0], point1[1], point2[0], point2[1])
            total_distance += segment_distance       
        return total_distance