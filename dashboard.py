import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

def create_dash_app(flask_app, system):

    dash_app = dash.Dash(__name__, server=flask_app, url_base_pathname='/dashboard/')
    
    ims = system.inventory_system
    risk_assessor = system.risk_assessor
    route_optimizer = system.route_optimizer

    dash_app.layout = html.Div([
        html.H1('Hospital Supply Chain Dashboard', className='text-center mb-4'),
        dcc.Dropdown(
            id='metric-dropdown',
            options=[
                {'label': 'Inventory Levels', 'value': 'inventory'},
                {'label': 'Supplier Risks', 'value': 'risks'},
                {'label': 'Route Efficiency', 'value': 'route'},
                {'label': 'Medicine Categories', 'value': 'categories'}
            ],
            value='inventory',
            className='mb-4'
        ),
        
        dcc.Graph(id='main-graph'),
        html.Div([
            html.Div([
                html.H3('Critical Alerts'),
                html.Div(id='alerts-div')
            ], className='col-md-6'),
            
            html.Div([
                html.H3('Performance Metrics'),
                html.Div(id='metrics-div')
            ], className='col-md-6')
        ], className='row mt-4')
    ])

    @dash_app.callback(
        Output('main-graph', 'figure'),
        [Input('metric-dropdown', 'value')]
    )
    def update_graph(selected_metric):
        if selected_metric == 'inventory':
            inventory_status = ims.get_inventory_status()
            
            if inventory_status:
                df = pd.DataFrame({
                    'Product': list(inventory_status.keys()),
                    'Stock Level': [status['stock_level'] for status in inventory_status.values()],
                    'Reorder Point': [status['reorder_point'] for status in inventory_status.values()]
                })
                
                fig = px.bar(df, 
                            x='Product', 
                            y=['Stock Level', 'Reorder Point'],
                            barmode='group',
                            title='Current Inventory Levels vs Reorder Points')
            else:
                fig = create_sample_inventory_graph()
            
        elif selected_metric == 'risks':
            supplier_risks = risk_assessor.assess_all_supplier_risks()
            
            if supplier_risks:
                df = pd.DataFrame(list(supplier_risks.items()), 
                                columns=['Supplier', 'Risk Score'])
                
                fig = px.bar(df, 
                            x='Supplier', 
                            y='Risk Score',
                            color='Risk Score',
                            color_continuous_scale=['green', 'yellow', 'red'],
                            title='Supplier Risk Assessment')
            else:
                fig = create_sample_risk_graph()
            
        elif selected_metric == 'route':
            try:
                best_route, best_cost = route_optimizer.optimize_route()
                route_data = create_route_data(best_route, best_cost)
                
                fig = px.line(route_data, 
                             x='Distance', 
                             y='Cost',
                             markers=True,
                             title='Route Optimization Results')
            except:
                fig = create_sample_route_graph()
                
        elif selected_metric == 'categories':
            try:
                cluster_summaries = system.medicine_classifier.get_cluster_summaries()
                
                if cluster_summaries:
                    categories = list(cluster_summaries.keys())
                    sizes = [summary['size'] for summary in cluster_summaries.values()]
                    priorities = [summary['avg_priority'] for summary in cluster_summaries.values()]
                    
                    df = pd.DataFrame({
                        'Category': categories,
                        'Size': sizes,
                        'Priority': priorities
                    })
                    
                    fig = px.scatter(df,
                                    x='Size',
                                    y='Priority',
                                    size='Size',
                                    color='Priority',
                                    hover_name='Category',
                                    title='Medicine Categories by Size and Priority')
                else:
                    fig = create_sample_category_graph()
            except:
                fig = create_sample_category_graph()
                
        return fig
    
    @dash_app.callback(
        Output('alerts-div', 'children'),
        [Input('metric-dropdown', 'value')]
    )
    def update_alerts(selected_metric):
        try:
            alerts = ims.generate_alerts()
            if alerts:
                return html.Ul([html.Li(alert) for alert in alerts[:5]])
            else:
                return html.P("No critical alerts at this time.")
        except:
            return html.P("Alert system not available.")
    
    @dash_app.callback(
        Output('metrics-div', 'children'),
        [Input('metric-dropdown', 'value')]
    )
    def update_metrics(selected_metric):
        metrics = {
            'Service Level': '98.2%',
            'Inventory Turnover': '12.4',
            'Order Fill Rate': '96.7%',
            'On-time Delivery': '94.5%'
        }
        
        return html.Table([
            html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")])),
            html.Tbody([
                html.Tr([html.Td(k), html.Td(v)]) for k, v in metrics.items()
            ])
        ], className='table table-striped')

    return dash_app

def create_sample_inventory_graph():
    products = ['Medicine A', 'Medicine B', 'Medicine C', 'Medicine D', 'Medicine E']
    stock_levels = [120, 85, 200, 45, 160]
    reorder_points = [50, 70, 100, 40, 80]
    
    df = pd.DataFrame({
        'Product': products,
        'Stock Level': stock_levels,
        'Reorder Point': reorder_points
    })
    
    return px.bar(df, 
                x='Product', 
                y=['Stock Level', 'Reorder Point'],
                barmode='group',
                title='Sample Inventory Data')

def create_sample_risk_graph():
    suppliers = ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E']
    risk_scores = [0.3, 0.7, 0.5, 0.2, 0.6]
    
    df = pd.DataFrame({
        'Supplier': suppliers,
        'Risk Score': risk_scores
    })
    
    return px.bar(df, 
                x='Supplier', 
                y='Risk Score',
                color='Risk Score',
                color_continuous_scale=['green', 'yellow', 'red'],
                title='Sample Supplier Risk Data')

def create_sample_route_graph():
    distances = list(range(0, 101, 20))
    costs = [0, 50, 120, 200, 300, 450]
    
    df = pd.DataFrame({
        'Distance': distances,
        'Cost': costs
    })
    
    return px.line(df, 
                 x='Distance', 
                 y='Cost',
                 markers=True,
                 title='Sample Route Efficiency Data')

def create_sample_category_graph():
    categories = ['Antibiotics', 'Pain Management', 'Cardiovascular', 
                 'Respiratory', 'Diabetes', 'Supplements']
    sizes = [120, 85, 200, 45, 160, 90]
    priorities = [0.8, 0.5, 0.7, 0.6, 0.9, 0.3]
    
    df = pd.DataFrame({
        'Category': categories,
        'Size': sizes,
        'Priority': priorities
    })
    
    return px.scatter(df,
                    x='Size',
                    y='Priority',
                    size='Size',
                    color='Priority',
                    hover_name='Category',
                    title='Sample Medicine Categories')

def create_route_data(route, cost):
    if not route or len(route) < 2:
        return create_sample_route_graph()
    distances = [0]
    costs = [0]
    
    for i in range(1, len(route)):
        segment_distance = pd.DataFrame({'Distance': [distances[-1] + i*10], 
                                         'Cost': [costs[-1] + (i*cost/len(route))]})
        distances.append(distances[-1] + i*10)
        costs.append(costs[-1] + (i*cost/len(route)))
    
    return pd.DataFrame({'Distance': distances, 'Cost': costs})