// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded, initializing event handlers');
    
    // Get reference to result container
    const resultContainer = document.getElementById('result-container');
    
    // Helper function to show a loading indicator
    function showLoading() {
        if (resultContainer) {
            resultContainer.innerHTML = '<div class="text-center my-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">Loading data...</p></div>';
        }
    }
    
    // Helper function to show an error message
    function showError(message) {
        if (resultContainer) {
            resultContainer.innerHTML = `<div class="alert alert-danger my-3">${message}</div>`;
        }
    }
    
    // Set up button click handlers
    setupButtonHandler('inventory-status-btn', '/inventory_status', handleInventoryData);
    setupButtonHandler('supplier-risk-btn', '/supplier_risks', handleSupplierRiskData);
    setupButtonHandler('route-optimization-btn', '/optimized_route', handleRouteData);
    setupButtonHandler('generate-report-btn', '/generate_report', handleReportData);
    setupButtonHandler('demand-forecast-btn', '/demand_forecast', handleForecastData);
    setupButtonHandler('medicine-classification-btn', '/medicine_classification', handleClassificationData);
    setupButtonHandler('risk-mitigation-btn', '/generate_report', handleReportData); // Uses same endpoint as generate report
    
    // Function to set up a button click handler
    function setupButtonHandler(buttonId, endpoint, dataHandler) {
        const button = document.getElementById(buttonId);
        console.log(`Setting up handler for ${buttonId}:`, button ? 'Found' : 'Not found');
        
        if (button) {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                console.log(`Button clicked: ${buttonId}`);
                
                // Scroll to result container
                if (resultContainer) {
                    resultContainer.scrollIntoView({ behavior: 'smooth' });
                }
                showLoading();
                fetch(endpoint)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Server responded with status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log(`Data received from ${endpoint}:`, data);
                        // Handle the data
                        if (data.error) {
                            showError(data.error);
                        } else {
                            dataHandler(data);
                        }
                    })
                    .catch(error => {
                        console.error(`Error fetching data from ${endpoint}:`, error);
                        showError(`Error fetching data: ${error.message}`);
                    });
            });
        }
    }

    function setupInventorySearch(inputId, buttonId, noResultsId, chartId) {
        const searchInput = document.getElementById(inputId);
        const searchButton = document.getElementById(buttonId);
        const noResultsMessage = document.getElementById(noResultsId);
        
        if (!searchInput || !searchButton || !window.originalChartData) return;
        
        // Function to filter chart data
        function filterChart() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            
            if (!searchTerm) {
                // If search is empty, restore original chart
                Plotly.newPlot(chartId, window.originalChartData.data, window.originalChartData.layout);
                noResultsMessage.classList.add('d-none');
                return;
            }
            
            // Get the original x-values (product names)
            const originalXValues = window.originalChartData.data[0].x;
            
            // Find which products match the search
            const matchingIndices = originalXValues.map((productName, index) => {
                return productName.toLowerCase().includes(searchTerm) ? index : -1;
            }).filter(index => index !== -1);
            
            if (matchingIndices.length === 0) {
                // No matching products
                noResultsMessage.classList.remove('d-none');
                // Create empty chart
                const emptyData = window.originalChartData.data.map(trace => {
                    return {
                        ...trace,
                        x: [],
                        y: []
                    };
                });
                Plotly.newPlot(chartId, emptyData, window.originalChartData.layout);
                return;
            }
            
            // Filter data for matching products
            const filteredData = window.originalChartData.data.map(trace => {
                return {
                    ...trace,
                    x: matchingIndices.map(i => trace.x[i]),
                    y: matchingIndices.map(i => trace.y[i])
                };
            });
            
            // Update chart with filtered data
            Plotly.newPlot(chartId, filteredData, window.originalChartData.layout);
            noResultsMessage.classList.add('d-none');
        }
        
        // Search on button click
        searchButton.addEventListener('click', filterChart);
        
        // Search when Enter key is pressed
        searchInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                filterChart();
            }
        });
        
        // Real-time filtering as user types
        searchInput.addEventListener('input', () => {
            clearTimeout(searchInput.debounceTimer);
            searchInput.debounceTimer = setTimeout(filterChart, 300);
        });
    }
    
    function setupTableSearch(inputId, buttonId, noResultsId, tableId) {
        const searchInput = document.getElementById(inputId);
        const searchButton = document.getElementById(buttonId);
        const noResultsMessage = document.getElementById(noResultsId);
        const table = document.getElementById(tableId);
        
        if (!searchInput || !searchButton || !table) return;
        
        // Function to filter table rows
        function filterTable() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            
            let matchFound = false;
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm) || !searchTerm) {
                    row.style.display = '';
                    matchFound = true;
                } else {
                    row.style.display = 'none';
                }
            });
            
            if (!matchFound && searchTerm) {
                noResultsMessage.classList.remove('d-none');
            } else {
                noResultsMessage.classList.add('d-none');
            }
        }
        
        // Search on button click
        searchButton.addEventListener('click', filterTable);
        
        // Search when Enter key is pressed
        searchInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                filterTable();
            }
        });
        
        // Real-time filtering as user types
        searchInput.addEventListener('input', () => {
            clearTimeout(searchInput.debounceTimer);
            searchInput.debounceTimer = setTimeout(filterTable, 300);
        });
    }
    
    function setupTableSorting(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.addEventListener('click', () => {
                sortTable(table, index);
            });
            header.style.cursor = 'pointer';
            header.title = 'Click to sort';
            
            // Add sort indicators
            const indicator = document.createElement('span');
            indicator.className = 'ms-1';
            indicator.innerHTML = '⇵';
            header.appendChild(indicator);
        });
    }
    
    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const headers = table.querySelectorAll('th');
        
        // Get current sort direction
        const header = headers[columnIndex];
        const currentDirection = header.getAttribute('data-sort') || 'none';
        const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
        
        // Update all headers to remove sorting indicators
        headers.forEach(h => {
            h.setAttribute('data-sort', 'none');
            const indicator = h.querySelector('span');
            if (indicator) indicator.innerHTML = '⇵';
        });
        
        // Set new sort direction and update indicator
        header.setAttribute('data-sort', newDirection);
        const indicator = header.querySelector('span');
        if (indicator) indicator.innerHTML = newDirection === 'asc' ? '↑' : '↓';
        
        // Sort the rows
        rows.sort((rowA, rowB) => {
            const cellA = rowA.cells[columnIndex].textContent.trim();
            const cellB = rowB.cells[columnIndex].textContent.trim();
            
            // Check if we're sorting numbers
            if (!isNaN(cellA) && !isNaN(cellB)) {
                return newDirection === 'asc' 
                    ? parseFloat(cellA) - parseFloat(cellB)
                    : parseFloat(cellB) - parseFloat(cellA);
            }
            
            // For text, use localeCompare
            return newDirection === 'asc'
                ? cellA.localeCompare(cellB)
                : cellB.localeCompare(cellA);
        });
        
        // Reorder the rows in the table
        rows.forEach(row => {
            tbody.appendChild(row);
        });
    }

    // Handler for inventory status data
    function handleInventoryData(data) {
        if (!data.chart) {
            showError('No inventory data available');
            return;
        }
        
        try {
            // Extract inventory data from the chart
            const chartData = JSON.parse(data.chart);
            const inventoryData = extractInventoryData(chartData);
            
            resultContainer.innerHTML = `
                <div class="card shadow-sm">
                    <div class="card-header bg-white">
                        <ul class="nav nav-tabs card-header-tabs" id="inventoryTabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="status-tab" data-bs-toggle="tab" 
                                        data-bs-target="#status-content" type="button" role="tab" 
                                        aria-controls="status-content" aria-selected="true">
                                    Status Overview
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="inventory-tab" data-bs-toggle="tab" 
                                        data-bs-target="#inventory-content" type="button" role="tab" 
                                        aria-controls="inventory-content" aria-selected="false">
                                    Inventory List
                                </button>
                            </li>
                        </ul>
                    </div>
                    <div class="card-body">
                        <div class="tab-content" id="inventoryTabsContent">
                            <!-- Status Tab -->
                            <div class="tab-pane fade show active" id="status-content" role="tabpanel" aria-labelledby="status-tab">
                                <div class="mb-3">
                                    <div class="input-group">
                                        <input type="text" id="chart-search" class="form-control" 
                                            placeholder="Search products...">
                                        <button class="btn btn-outline-primary" type="button" id="chart-search-button">
                                            <i class="fas fa-search"></i> Search
                                        </button>
                                    </div>
                                    <div class="form-text">Search by product name or type</div>
                                </div>
                                <div id="inventory-chart" style="height: 400px;"></div>
                                <div id="chart-no-results" class="alert alert-info mt-3 d-none">
                                    No products match your search criteria.
                                </div>
                    </div>
                        <!-- Inventory Tab -->
                        <div class="tab-pane fade" id="inventory-content" role="tabpanel" aria-labelledby="inventory-tab">
            <div class="mb-3">
                <div class="input-group">
                    <input type="text" id="table-search" class="form-control" 
                        placeholder="Search products...">
                    <button class="btn btn-outline-primary" type="button" id="table-search-button">
                        <i class="fas fa-search"></i> Search
                    </button>
                </div>
                <div class="form-text">Search products by name, category or stock status</div>
            </div>
            <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                <table class="table table-striped table-hover" id="inventory-table">
                    <thead class="sticky-top bg-white">
                        <tr>
                            <th>Product Name</th>
                            <th>Current Stock</th>
                            <th>Reorder Point</th>
                            <th>Status</th>
                            <th>Days Remaining</th>
                            <th>Criticality</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${generateInventoryTableRows(inventoryData)}
                    </tbody>
                </table>
            </div>
            <div id="table-no-results" class="alert alert-info mt-3 d-none">
                No products match your search criteria.
            </div>
        </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Plot the chart
            Plotly.newPlot('inventory-chart', chartData.data, chartData.layout);
            
            // Store the original chart data for filtering
            window.originalChartData = chartData;
            window.inventoryData = inventoryData;
            
            // Set up search functionality
            setupInventorySearch('chart-search', 'chart-search-button', 'chart-no-results', 'inventory-chart');
            setupTableSearch('table-search', 'table-search-button', 'table-no-results', 'inventory-table');
            setupTableSorting('inventory-table');
        } catch (error) {
            console.error('Error rendering inventory data:', error);
            showError(`Error rendering inventory data: ${error.message}`);
        }
    }
    function extractInventoryData(chartData) {
        // Extract data from chart to use in the table
        // Assuming chart data has product names in x and stock levels/reorder points in y
        const products = chartData.data[0].x;
        const stockLevels = chartData.data[0].y;
        const reorderPoints = chartData.data[1] ? chartData.data[1].y : [];
        
        // Create an array of product objects
        return products.map((name, index) => {
            const stockLevel = stockLevels[index] || 0;
            const reorderPoint = reorderPoints[index] || 0;
            
            // Calculate status based on stock level vs reorder point
            let status = "Adequate";
            let statusClass = "text-success";
            
            if (stockLevel <= reorderPoint * 0.5) {
                status = "Critical";
                statusClass = "text-danger";
            } else if (stockLevel <= reorderPoint) {
                status = "Low";
                statusClass = "text-warning";
            } else if (stockLevel >= reorderPoint * 2) {
                status = "Overstocked";
                statusClass = "text-info";
            }
            
            // Estimate days remaining (assuming average daily demand is stockLevel/30)
            const estimatedDailyDemand = stockLevel / 30; // Simple estimation
            const daysRemaining = estimatedDailyDemand > 0 ? Math.round(stockLevel / estimatedDailyDemand) : "N/A";
            
            // Random criticality value between 1-5 for demo
            const criticality = Math.floor(Math.random() * 5) + 1;
            
            return {
                name,
                stockLevel,
                reorderPoint,
                status,
                statusClass,
                daysRemaining,
                criticality
            };
        });
    }
    
    function generateInventoryTableRows(inventoryData) {
        if (!inventoryData || inventoryData.length === 0) {
            return '<tr><td colspan="6" class="text-center">No inventory data available</td></tr>';
        }
        
        return inventoryData.map(item => `
            <tr>
                <td>${item.name}</td>
                <td>${item.stockLevel}</td>
                <td>${item.reorderPoint}</td>
                <td><span class="${item.statusClass}">${item.status}</span></td>
                <td>${item.daysRemaining}</td>
                <td>${'★'.repeat(item.criticality)}</td>
            </tr>
        `).join('');
    }
    // Handler for route optimization data
    function handleRouteData(data) {
        if (!data.map) {
            showError('No route data available');
            return;
        }
        
        try {
            // Create route visualization container
            resultContainer.innerHTML = `
                <div class="card shadow-sm">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Optimized Delivery Route</h5>
                        <button class="btn btn-sm btn-outline-primary" onclick="printRouteMap()">
                            <i class="fa fa-print"></i> Print
                        </button>
                    </div>
                    <div class="card-body p-0">
                        <div class="row g-0">
                            <div class="col-md-9">
                                <div id="route-map" style="height: 500px;">${data.map}</div>
                            </div>
                            <div class="col-md-3 p-3">
                                <h6>Route Metrics</h6>
                                <ul class="list-group list-group-flush">
                                    ${data.metrics ? `
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span>Distance:</span>
                                            <span class="badge bg-primary rounded-pill">${data.metrics.distance_km} km</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span>Est. Time:</span>
                                            <span class="badge bg-primary rounded-pill">${data.metrics.estimated_time_min} min</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span>Fuel Usage:</span>
                                            <span class="badge bg-primary rounded-pill">${data.metrics.fuel_usage_liters} L</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span>CO2 Emissions:</span>
                                            <span class="badge bg-primary rounded-pill">${data.metrics.co2_emissions_kg} kg</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span>Cost/km:</span>
                                            <span class="badge bg-primary rounded-pill">₹${data.metrics.cost_per_km}</span>
                                        </li>
                                    ` : `
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span>Total Cost:</span>
                                            <span class="badge bg-primary rounded-pill">₹${data.cost ? data.cost.toFixed(2) : 'N/A'}</span>
                                        </li>
                                    `}
                                </ul>
                                <div class="mt-3">
                                    <h6>About This Route</h6>
                                    <p class="small text-muted">
                                        This optimized route considers current traffic conditions, weather, and road quality to find the most efficient path for delivery.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error rendering route map:', error);
            showError(`Error rendering route map: ${error.message}`);
        }
    }
    
    // Handler for report data
    function handleReportData(data) {
        if (!data.report) {
            showError('No report data available');
            return;
        }
        
        try {
            // Parse the report sections
            const reportSections = parseReportSections(data.report);
            
            // Create HTML structure
            let reportHtml = `
                <div class="card shadow">
                    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Risk Mitigation Report</h5>
                        <div>
                            <button class="btn btn-sm btn-light me-2" onclick="printReport()">
                                <i class="fas fa-print"></i> Print
                            </button>
                            <button class="btn btn-sm btn-light" onclick="downloadReportPDF()">
                                <i class="fas fa-file-pdf"></i> Download PDF
                            </button>
                        </div>
                    </div>
                    <div class="card-body p-4">
            `;
            
            // Add section for Executive Summary
            if (reportSections.executiveSummary) {
                reportHtml += `
                    <div class="mb-4">
                        <h4 class="text-primary">Executive Summary</h4>
                        <div class="mt-3">
                            ${formatSectionContent(reportSections.executiveSummary)}
                        </div>
                    </div>
                    <hr/>
                `;
            }
            
            // Create two-column layout for the main content
            reportHtml += `<div class="row">`;
            
            // Left column with Risk Assessment and Mitigation Strategies
            reportHtml += `<div class="col-md-6">`;
            
            // Add Risk Assessment section
            if (reportSections.RISK_ASSESSMENT_SUMMARY) {
                reportHtml += `
                    <div class="mb-4">
                        <h4 class="text-danger">Risk Assessment Summary</h4>
                        <div class="mt-3">
                            ${formatSectionContent(reportSections.RISK_ASSESSMENT_SUMMARY)}
                        </div>
                    </div>
                `;
            }
            
            // Add Recommended Mitigation Strategies
            if (reportSections.RECOMMENDED_MITIGATION_STRATEGIES) {
                reportHtml += `
                    <div class="mb-4">
                        <h4 class="text-success">Recommended Mitigation Strategies</h4>
                        <div class="mt-3">
                            ${formatSectionContent(reportSections.RECOMMENDED_MITIGATION_STRATEGIES)}
                        </div>
                    </div>
                `;
            }
            
            reportHtml += `</div>`; // End left column
            
            // Right column with Scenario Analysis and Implementation Plan
            reportHtml += `<div class="col-md-6">`;
            
            // Add Scenario Analysis
            if (reportSections.SCENARIO_ANALYSIS) {
                reportHtml += `
                    <div class="mb-4">
                        <h4 class="text-info">Scenario Analysis</h4>
                        <div class="mt-3">
                            ${formatSectionContent(reportSections.SCENARIO_ANALYSIS)}
                        </div>
                    </div>
                `;
            }
            
            // Add Implementation Plan
            if (reportSections.IMPLEMENTATION_PLAN) {
                reportHtml += `
                    <div class="mb-4">
                        <h4 class="text-warning">Implementation Plan</h4>
                        <div class="mt-3">
                            ${formatSectionContent(reportSections.IMPLEMENTATION_PLAN)}
                        </div>
                    </div>
                `;
            }
            
            reportHtml += `</div>`; // End right column
            reportHtml += `</div>`; // End row
            
            // Add Conclusion section (full width)
            if (reportSections.CONCLUSION) {
                reportHtml += `
                    <hr/>
                    <div class="mt-4">
                        <h4 class="text-primary">Conclusion</h4>
                        <div class="mt-3">
                            ${formatSectionContent(reportSections.CONCLUSION)}
                        </div>
                    </div>
                `;
            }
            
            reportHtml += `
                    <div class="card-footer text-muted text-end">
                        <small>Report generated on ${new Date().toLocaleString()}</small>
                    </div>
                </div>
            `;
            
            resultContainer.innerHTML = reportHtml;
            
            // Store the original report for printing
            window.originalReport = data.report;
        } catch (error) {
            console.error('Error rendering report:', error);
            showError(`Error rendering report: ${error.message}`);
        }
    }
    
    // Helper function to parse report into sections
    function parseReportSections(report) {
        const sections = {};
        
        // Extract Executive Summary (everything before the first section header)
        const firstSectionIndex = report.indexOf("\n\n", report.indexOf("======"));
        sections["executiveSummary"] = report.substring(0, firstSectionIndex).trim();
        
        // Define section markers to look for
        const sectionMarkers = [
            "RISK ASSESSMENT SUMMARY",
            "RECOMMENDED MITIGATION STRATEGIES",
            "SCENARIO ANALYSIS",
            "IMPLEMENTATION PLAN",
            "CONCLUSION"
        ];
        
        // Find each section
        for (let i = 0; i < sectionMarkers.length; i++) {
            const currentMarker = sectionMarkers[i];
            const nextMarker = i < sectionMarkers.length - 1 ? sectionMarkers[i + 1] : null;
            
            const startIdx = report.indexOf(currentMarker);
            if (startIdx !== -1) {
                // Find the content start (after the underline)
                const contentStart = report.indexOf("\n", report.indexOf("_", startIdx));
                
                // Find the content end (before the next section or end of report)
                let contentEnd;
                if (nextMarker && report.indexOf(nextMarker) !== -1) {
                    contentEnd = report.indexOf(nextMarker);
                } else {
                    contentEnd = report.length;
                }
                
                // Extract and store the section content
                const sectionKey = currentMarker.replace(/\s+/g, '_');
                sections[sectionKey] = report.substring(contentStart, contentEnd).trim();
            }
        }
        
        return sections;
    }
    
    // Helper function to format section titles
    function formatSectionTitle(title) {
        return title.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ');
    }
    
    // Helper function to format section content
    function formatSectionContent(content) {
        if (!content) return '';
        
        // Convert risk scores to badges
        content = content.replace(/risk level: (\w+) \(([0-9.]+)\)/gi, (match, level, score) => {
            const scoreNum = parseFloat(score);
            let badgeClass = 'bg-success';
            if (scoreNum > 0.6) badgeClass = 'bg-danger';
            else if (scoreNum > 0.3) badgeClass = 'bg-warning';
            
            return `risk level: <span class="badge ${badgeClass}">${level} (${score})</span>`;
        });
        
        // Format lists and special formatting
        const lines = content.split('\n');
        let formattedContent = '';
        let inList = false;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            if (!line) {
                // Empty line
                if (inList) {
                    formattedContent += '</ul>';
                    inList = false;
                }
                formattedContent += '<br/>';
                continue;
            }
            
            // Check if this is a list item
            if (line.match(/^\d+\.\s/) || line.match(/^-\s/) || line.match(/^\*\s/)) {
                if (!inList) {
                    formattedContent += '<ul class="list-group list-group-flush">';
                    inList = true;
                }
                const listContent = line.replace(/^\d+\.\s|-\s|\*\s/, '');
                formattedContent += `<li class="list-group-item border-0 ps-0">${listContent}</li>`;
            }
            // Check if this is a heading
            else if (line.match(/^[A-Z][a-zA-Z\s]+:$/)) {
                if (inList) {
                    formattedContent += '</ul>';
                    inList = false;
                }
                formattedContent += `<h5 class="mt-3 mb-2 text-secondary">${line}</h5>`;
            }
            // Check if line contains "Projected Effectiveness"
            else if (line.includes("Projected Effectiveness:")) {
                const [label, value] = line.split(":");
                const effectivenessLevel = value.trim().split(" ")[0];
                const effectivenessScore = value.trim().match(/\(([0-9.]+)\)/)[1];
                
                let badgeClass = 'bg-success';
                if (effectivenessLevel === 'Low') badgeClass = 'bg-danger';
                else if (effectivenessLevel === 'Medium') badgeClass = 'bg-warning';
                
                formattedContent += `<div class="ms-3 mb-2"><small class="text-muted">${label}: <span class="badge ${badgeClass}">${effectivenessLevel} (${effectivenessScore})</span></small></div>`;
            }
            // Regular paragraph
            else {
                if (inList) {
                    formattedContent += '</ul>';
                    inList = false;
                }
                formattedContent += `<p>${line}</p>`;
            }
        }
        
        // Close any open list
        if (inList) {
            formattedContent += '</ul>';
        }
        
        return formattedContent;
    }
    
    // Function to download the report as PDF
    window.downloadReportPDF = function() {
        if (window.originalReport) {
            // In a real implementation, you would use a library like jsPDF
            // For this demo, we'll simulate it with a new window
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Risk Mitigation Report</title>
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                            h1 { color: #333; text-align: center; margin-bottom: 20px; }
                            h2 { color: #0d6efd; margin-top: 30px; }
                            pre { white-space: pre-wrap; background-color: #f8f9fa; padding: 15px; border-radius: 5px; }
                            .footer { margin-top: 50px; text-align: center; font-size: 12px; color: #6c757d; }
                        </style>
                    </head>
                    <body>
                        <h1>Risk Mitigation Report</h1>
                        <pre>${window.originalReport}</pre>
                        <div class="footer">
                            Generated on ${new Date().toLocaleString()}<br>
                            Hospital Supply Chain Risk Management System
                        </div>
                        <script>
                            // In a real implementation, this would use jsPDF to generate a PDF
                            // For now, just offer to print
                            window.onload = function() {
                                alert("In a production environment, this would download a PDF. For now, you can print this page.");
                                setTimeout(() => { window.print(); }, 1000);
                            }
                        </script>
                    </body>
                </html>
            `);
            printWindow.document.close();
        }
    };
    
    // Handler for demand forecast data
    function handleForecastData(data) {
        if (!data.chart && !data.forecast) {
            showError('No forecast data available');
            return;
        }
        
        try {
            console.log("Received forecast data:", data);
            
            // Generate product options (1-10)
            let productOptions = '';
            for (let i = 1; i <= 10; i++) {
                productOptions += `<option value="${i}" ${data.product_id == i ? 'selected' : ''}>Product ${i}</option>`;
            }
            
            resultContainer.innerHTML = `
                <div class="card shadow-sm">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Demand Forecast Dashboard</h5>
                        <div class="btn-group" role="group">
                            <select id="product-selector" class="form-select form-select-sm me-2" style="width: auto;">
                                ${productOptions}
                            </select>
                            <button class="btn btn-sm btn-outline-primary" onclick="downloadForecastCSV()">
                                <i class="fas fa-download"></i> Export Data
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-9">
                                <div id="forecast-chart" style="height: 400px;"></div>
                            </div>
                            <div class="col-md-3">
                                ${data.stats ? renderForecastStats(data.stats) : ''}
                            </div>
                        </div>
                    </div>
                    <div class="card-footer bg-white">
                        <small class="text-muted">
                            Forecast generated using Neural Prophet model with 30-day prediction horizon.
                        </small>
                    </div>
                </div>
            `;
            
            // Store forecast data for potential CSV download
            window.forecastData = data.forecast;
            
            // Parse and render the chart
            if (data.chart) {
                console.log("Chart data length:", data.chart.length);
                try {
                    const chartData = JSON.parse(data.chart);
                    console.log("Successfully parsed chart data");
                    
                    // Check if there's a DOM element to render to
                    const chartElement = document.getElementById('forecast-chart');
                    if (chartElement) {
                        console.log("Found chart element, rendering Plotly chart");
                        Plotly.newPlot('forecast-chart', chartData.data, chartData.layout);
                        console.log("Chart rendered successfully");
                    } else {
                        console.error("Chart element not found in DOM");
                    }
                } catch (parseError) {
                    console.error("Error parsing chart JSON:", parseError);
                    showError(`Error parsing chart data: ${parseError.message}`);
                }
            } else {
                console.warn("No chart data received");
                document.getElementById('forecast-chart').innerHTML = `
                    <div class="alert alert-warning">
                        No visualization data available. Showing raw forecast data.
                    </div>
                    <pre>${JSON.stringify(data.forecast, null, 2)}</pre>
                `;
            }
            
            // Set up product selector event handler
            const productSelector = document.getElementById('product-selector');
            if (productSelector) {
                productSelector.addEventListener('change', function() {
                    console.log("Product selector changed to:", this.value);
                    fetchForecastForProduct(this.value);
                });
            }
            
        } catch (error) {
            console.error('Error rendering forecast data:', error);
            showError(`Error rendering forecast data: ${error.message}`);
        }
    }
    
    // Function to render forecast statistics
    function renderForecastStats(stats) {
        console.log("Rendering forecast stats:", stats);
        return `
            <div class="card h-100">
                <div class="card-header bg-light">
                    <h6 class="mb-0">Forecast Metrics</h6>
                </div>
                <div class="card-body p-0">
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Avg Daily Demand:</span>
                            <span class="badge bg-primary rounded-pill">${Math.round(stats.mean || 0)}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Min Demand:</span>
                            <span class="badge bg-primary rounded-pill">${Math.round(stats.min || 0)}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Max Demand:</span>
                            <span class="badge bg-primary rounded-pill">${Math.round(stats.max || 0)}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Total ${stats.days || 30}-Day Demand:</span>
                            <span class="badge bg-primary rounded-pill">${Math.round(stats.total || 0)}</span>
                        </li>
                    </ul>
                </div>
            </div>
        `;
    }
    
    // Function to fetch forecast for a specific product
    function fetchForecastForProduct(productId) {
        showLoading();
        
        fetch(`/demand_forecast?product_id=${productId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    handleForecastData(data);
                }
            })
            .catch(error => {
                console.error(`Error fetching forecast for product ${productId}:`, error);
                showError(`Error fetching forecast: ${error.message}`);
            });
    }
    
    // Function to download forecast data as CSV
    window.downloadForecastCSV = function() {
        if (window.forecastData) {
            const forecastData = window.forecastData;
            const csvContent = "data:text/csv;charset=utf-8,Day,Forecasted Demand\n" + 
                forecastData.map((value, index) => `${index + 1},${value}`).join("\n");
            
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `demand_forecast_${new Date().toISOString().slice(0, 10)}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert("No forecast data available to download");
        }
    };
    
    // Function to show optimization modal
    window.showOptimizationModal = function() {
        const modalHTML = `
            <div class="modal fade" id="optimizationModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Inventory Optimization</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>Based on the forecast, we recommend the following inventory parameters:</p>
                            <form>
                                <div class="mb-3">
                                    <label for="safetyStock" class="form-label">Safety Stock</label>
                                    <input type="number" class="form-control" id="safetyStock" value="${Math.round(window.forecastData ? Math.max(...window.forecastData) * 0.2 : 50)}">
                                    <div class="form-text">Minimum inventory level to maintain as buffer against uncertainty.</div>
                                </div>
                                <div class="mb-3">
                                    <label for="reorderPoint" class="form-label">Reorder Point</label>
                                    <input type="number" class="form-control" id="reorderPoint" value="${Math.round(window.forecastData ? Math.max(...window.forecastData) * 0.5 : 100)}">
                                    <div class="form-text">Inventory level that triggers a new order.</div>
                                </div>
                                <div class="mb-3">
                                    <label for="orderQuantity" class="form-label">Order Quantity</label>
                                    <input type="number" class="form-control" id="orderQuantity" value="${Math.round(window.forecastData ? Math.max(...window.forecastData) : 200)}">
                                    <div class="form-text">Quantity to order when reaching the reorder point.</div>
                                </div>
                                <div class="mb-3">
                                    <label for="leadTime" class="form-label">Lead Time (days)</label>
                                    <input type="number" class="form-control" id="leadTime" value="7">
                                    <div class="form-text">Average time between placing an order and receiving it.</div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" onclick="applyOptimization()">Apply Optimization</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body if it doesn't exist
        if (!document.getElementById('optimizationModal')) {
            const div = document.createElement('div');
            div.innerHTML = modalHTML;
            document.body.appendChild(div);
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('optimizationModal'));
        modal.show();
    };
    
    // Function to apply optimization
    window.applyOptimization = function() {
        alert("Optimization parameters applied. In a production system, these would be saved to the database and used to update inventory management policies.");
        bootstrap.Modal.getInstance(document.getElementById('optimizationModal')).hide();
    };
    
    // Handler for medicine classification data
    function handleClassificationData(data) {
        if (!data.classification) {
            showError('No classification data available');
            return;
        }
        
        try {
            let classificationHtml = '';
            const classification = data.classification;
            
            // Create HTML for each category
            for (const [category, details] of Object.entries(classification)) {
                const priorityClass = details.avg_priority > 0.7 ? 'bg-danger text-white' : 
                                    details.avg_priority > 0.4 ? 'bg-warning' : 'bg-success text-white';
                                    
                classificationHtml += `
                    <div class="col-md-6 mb-3">
                        <div class="card h-100">
                            <div class="card-header ${priorityClass}">
                                <h6 class="mb-0">${category}</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Top terms:</strong> ${details.top_terms.join(', ')}</p>
                                <p><strong>Priority:</strong> ${(details.avg_priority * 100).toFixed(1)}%</p>
                                <p><strong>Size:</strong> ${details.size} medicines</p>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            resultContainer.innerHTML = `
                <div class="card shadow-sm">
                    <div class="card-header bg-white">
                        <h5 class="mb-0">Medicine Classification Results</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            ${classificationHtml}
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error rendering classification data:', error);
            showError(`Error rendering classification data: ${error.message}`);
        }
    }
    
    // Function to print the report
    window.printReport = function() {
        const reportContent = document.querySelector('.report-content');
        if (reportContent) {
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Risk Mitigation Report</title>
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; }
                            h1 { color: #333; text-align: center; margin-bottom: 20px; }
                            pre { white-space: pre-wrap; }
                        </style>
                    </head>
                    <body>
                        <h1>Risk Mitigation Report</h1>
                        <pre>${reportContent.textContent}</pre>
                    </body>
                </html>
            `);
            printWindow.document.close();
            setTimeout(() => {
                printWindow.print();
            }, 250);
        }
    };
    
    // Function to print the route map
    window.printRouteMap = function() {
        const routeMap = document.getElementById('route-map');
        if (routeMap) {
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Optimized Delivery Route</title>
                        <style>
                            body { font-family: Arial, sans-serif; }
                            h1 { color: #333; text-align: center; margin-bottom: 20px; }
                        </style>
                    </head>
                    <body>
                        <h1>Optimized Delivery Route</h1>
                        ${routeMap.innerHTML}
                    </body>
                </html>
            `);
            printWindow.document.close();
            setTimeout(() => {
                printWindow.print();
            }, 250);
        }
    };
    
    // Initialize the first visible content if on home page
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        const firstButton = document.getElementById('inventory-status-btn');
        if (firstButton) {
            console.log('Automatically triggering first button click');
            // firstButton.click(); // Uncomment this to auto-load the first feature
        }
    }
    
    console.log('Event handlers initialized');
});