import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
import heapq
from datetime import datetime
import time

class RouteOptimizer:
    def __init__(self, hospital_address, openweathermap_api_key, tomtom_api_key):
        self.hospital_address = hospital_address
        self.openweathermap_api_key = "9d93cff80115b3152f8732f2679b738c"
        self.tomtom_api_key = "4fkroF84IrwfpSZOmpatPDHUbr1GNih8"
        self.geolocator = Nominatim(user_agent="hospital_supply_chain")
        self.hospital_location = self.geolocate(hospital_address)
        self.suppliers = self.load_suppliers()
        self.traffic_data = {}
        self.weather_data = {}

    def load_suppliers(self):
        suppliers = [
            {"name": "Supplier A", "address": "Kochi, Kerala, India"},
            {"name": "Supplier B", "address": "Chennai, Tamil Nadu, India"},
            {"name": "Supplier C", "address": "Bangalore, Karnataka, India"},
        ]
        for supplier in suppliers:
            supplier["location"] = self.geolocate(supplier["address"])
        return suppliers

    def geolocate(self, address):
        location = self.geolocator.geocode(address)
        return (location.latitude, location.longitude)

    def get_traffic_data(self, origin, destination):
        try:
            url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin[0]},{origin[1]}:{destination[0]},{destination[1]}/json"
            params = {
                "key": self.tomtom_api_key,
                "routeType": "fastest",
                "traffic": "true",
                "travelMode": "truck",  
                "vehicleMaxSpeed": 90,  
                "computeTravelTimeFor": "all",
                "routeRepresentation": "polyline"
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'routes' in data and len(data['routes']) > 0:     
                    legs = data['routes'][0]['legs']
                    route_coords = []
                    for leg in legs:
                        if 'points' in leg:
                            route_coords.extend([(point['latitude'], point['longitude']) for point in leg['points']])
                        
                    summary = data['routes'][0]['summary']
                    distance_km = summary.get('lengthInMeters', 0) / 1000
                    time_mins = summary.get('travelTimeInSeconds', 0) / 60
                    
                    return {
                        'coordinates': route_coords,
                        'distance': distance_km,
                        'time': time_mins
                    }
            
            print("Could not get TomTom route, falling back to direct line")
            return None
        
        except Exception as e:
            print(f"Error getting TomTom route: {e}")
            return None
    def get_weather_data(self, location):
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": location[0],
            "lon": location[1],
            "appid": self.openweathermap_api_key,
            "units": "metric"
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'weather' in data and len(data['weather']) > 0:
            weather_id = data['weather'][0]['id']
            
            if weather_id < 300:  
                return 0.9
            elif weather_id < 500: 
                return 0.3
            elif weather_id < 600: 
                return 0.6
            elif weather_id < 700:  
                return 0.8
            elif weather_id < 800: 
                return 0.5
            elif weather_id == 800:  
                return 0
            else: 
                return 0.1
        else:
            return 0  

    def calculate_cost(self, origin, destination):
        try:
           
            origin_coords = (float(origin[0]), float(origin[1]))
            dest_coords = (float(destination[0]), float(destination[1]))

            distance = float(geodesic(origin_coords, dest_coords).kilometers)

            current_hour = datetime.now().hour
            if 7 <= current_hour <= 10 or 16 <= current_hour <= 19:
                traffic_factor = 1.5  
            else:
                traffic_factor = 1.0

            weather_risk = min(1.0, distance / 1000) 

            total_cost = distance * traffic_factor * (1 + weather_risk)
            
            return total_cost

        except Exception as e:
            print(f"Error in calculate_cost: {str(e)}")
            print(f"Origin: {origin}, type: {type(origin)}")
            print(f"Destination: {destination}, type: {type(destination)}")
            try:
                return float(geodesic(origin, destination).kilometers)
            except:
                return 1000.0  

    def a_star(self, start, goal):
        def heuristic(a, b):
            return geodesic(a, b).kilometers

        
        if not (isinstance(start, tuple) and isinstance(goal, tuple)):
            raise ValueError("Start and goal must be tuples")
        if not len(start) == len(goal) == 2:
            raise ValueError("Coordinates must be (lat, lon) pairs")
        if not all(isinstance(x, (int, float)) for x in start + goal):
            raise ValueError("Coordinates must be numbers")

        open_list = [(0, start)]
        closed_set = set()
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_list:
            current = heapq.heappop(open_list)[1]
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            closed_set.add(current)
            neighbors = [supplier["location"] for supplier in self.suppliers]
            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue

                try:
                    tentative_g_score = g_score[current] + self.calculate_cost(current, neighbor)
                except Exception as e:
                    print(f"Error calculating cost for neighbor {neighbor}: {e}")
                    continue

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

        return None

    def optimize_route(self):
        try:
            start = self.hospital_location
            best_route = None
            best_cost = float('inf')
            best_route_details = None
            
            for supplier in self.suppliers:
                supplier_name = supplier["name"]
                supplier_loc = supplier["location"]
                route_data = self.get_traffic_data(start, supplier_loc)
            
            if route_data and 'coordinates' in route_data and len(route_data['coordinates']) > 0:
                route = route_data['coordinates']
                cost = route_data['distance'] * 1.0 + route_data['time'] * 0.1
                
                print(f"Route to {supplier_name} has {len(route)} points, distance: {route_data['distance']:.2f} km, time: {route_data['time']:.1f} min, cost: {cost:.2f}")
                
                if cost < best_cost:
                    best_cost = cost
                    best_route = route
                    best_route_details = {
                        'supplier': supplier_name,
                        'distance_km': route_data['distance'],
                        'time_mins': route_data['time']
                    }
                    print(f"Found better route to {supplier_name} with cost: {cost:.2f}")
                else:
                    direct_route = [start, supplier_loc]
                    direct_cost = self.calculate_cost(start, supplier_loc)
                    
                    print(f"Using direct line to {supplier_name}, cost: {direct_cost:.2f}")
                    
                    if direct_cost < best_cost:
                        best_cost = direct_cost
                        best_route = direct_route
                        best_route_details = {
                            'supplier': supplier_name,
                            'is_direct': True
                        }
                        print(f"Found better direct route to {supplier_name} with cost: {direct_cost:.2f}")

            if not best_route:
                print("No valid routes found")
                return [start, start], float('inf'), {}
                
            return best_route, best_cost, best_route_details

        except Exception as e:
            print(f"Error in optimize_route: {str(e)}")
            return [self.hospital_location, self.hospital_location], float('inf'), {}

    def calculate_normal_cost(self, route):
        if not route or len(route) < 2:
            return 0.0
            
        total_normal_cost = 0.0
        
        try:
            for i in range(len(route) - 1):
                origin = route[i]
                destination = route[i + 1]
               
                origin_coords = (float(origin[0]), float(origin[1]))
                dest_coords = (float(destination[0]), float(destination[1]))
            
                distance = float(geodesic(origin_coords, dest_coords).kilometers)
                standard_cost_per_km = 1.0
            
                segment_cost = distance * standard_cost_per_km
                total_normal_cost += segment_cost
                
            return total_normal_cost
            
        except Exception as e:
            print(f"Error calculating normal cost: {str(e)}")
            try:
                start = route[0]
                end = route[-1]
                direct_distance = float(geodesic(start, end).kilometers)
                return direct_distance * 1.0  
            except:
                return 100.0  
        
    def visualize_route(self, route, route_details=None):
      
        try:
            m = folium.Map(location=self.hospital_location, zoom_start=8)
            folium.Marker(
                self.hospital_location,
                popup="Hospital",
                icon=folium.Icon(color="red", icon="hospital-o", prefix='fa')
            ).add_to(m)

            for supplier in self.suppliers:
                folium.Marker(
                    supplier["location"],
                    popup=supplier["name"],
                    icon=folium.Icon(color="blue", icon="industry", prefix='fa')
                ).add_to(m)

            if route and len(route) >= 2:
                
                is_detailed_route = len(route) > 2
                folium.PolyLine(
                    locations=route,
                    weight=4,
                    color='green' if is_detailed_route else 'red',
                    opacity=0.8,
                    tooltip="Road Route" if is_detailed_route else "Direct Route"
                ).add_to(m)

                if route_details:
                    mid_index = len(route) // 2
                    mid_point = route[mid_index]
                    popup_content = f"""
                    <div style="width:200px;">
                        <h4 style="margin-top:0;">Route Details</h4>
                        <ul style="padding-left:20px;margin-bottom:0;">
                            <li>Destination: {route_details.get('supplier', 'Unknown')}</li>
                    """

                    if 'distance_km' in route_details:
                        popup_content += f"<li>Distance: {route_details['distance_km']:.2f} km</li>"
                    
                    if 'time_mins' in route_details:
                        popup_content += f"<li>Est. Time: {route_details['time_mins']:.1f} mins</li>"
                    
                    if route_details.get('is_direct'):
                        popup_content += "<li><strong>Note:</strong> Using direct route (API route unavailable)</li>"
                    
                    popup_content += """
                        </ul>
                    </div>
                    """
                    
                    folium.Popup(popup_content, max_width=300).add_to(
                        folium.Marker(
                            mid_point,
                            icon=folium.DivIcon(
                                icon_size=(150, 36),
                                icon_anchor=(75, 18),
                                html='<div style="background-color:white; padding:5px; border-radius:5px; border:1px solid green;"><b>Route Info</b></div>'
                            )
                        ).add_to(m)
                    )

            if route and len(route) >= 2:
                all_points = route + [supplier["location"] for supplier in self.suppliers] + [self.hospital_location]
                sw = [min(p[0] for p in all_points), min(p[1] for p in all_points)]
                ne = [max(p[0] for p in all_points), max(p[1] for p in all_points)]
                m.fit_bounds([sw, ne])

            output_path = "optimized_route.html"
            m.save(output_path)
            print(f"Route map saved as '{output_path}'")
            return m._repr_html_()

        except Exception as e:
            print(f"Error in visualize_route: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"<div class='alert alert-danger'>Error generating route map: {str(e)}</div>"

    def continuous_optimization(self, interval_minutes=30):
        while True:
            print(f"Optimizing route at {datetime.now()}")
            best_route, best_cost = self.optimize_route()
            print(f"Best route cost: {best_cost:.2f}")
            self.visualize_route(best_route)
            
            print(f"Waiting {interval_minutes} minutes for next optimization...")
            time.sleep(interval_minutes * 60)

optimizer = RouteOptimizer(
    "Medical College, Trivandrum, Kerala, India",
    "9d93cff80115b3152f8732f2679b738c",
    "4fkroF84IrwfpSZOmpatPDHUbr1GNih8"
)
best_route, best_cost, best_route_details = optimizer.optimize_route()
print(f"Best route cost: {best_cost:.2f}")
optimizer.visualize_route(best_route)
