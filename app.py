import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="Rental Yield & ROI Optimizer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 Rental Yield & ROI Optimizer")
st.markdown("**Analyze and compare rental investment opportunities with interactive yield calculations**")

# --- Sidebar Inputs ---
st.sidebar.header("🏡 Property Investment Parameters")
st.sidebar.markdown("Enter your property details below to calculate potential returns:")

# Property price input
price = st.sidebar.number_input(
    "Property Purchase Price (€)", 
    min_value=50000, 
    max_value=2000000, 
    value=300000,
    step=10000,
    help="Total purchase price including fees and taxes"
)

# Rental income inputs
st.sidebar.subheader("📊 Rental Income")
rent_long = st.sidebar.number_input(
    "Monthly Long-Term Rent (€)", 
    min_value=300, 
    max_value=5000, 
    value=1200,
    step=50,
    help="Expected monthly rent for long-term tenants"
)

rent_short = st.sidebar.number_input(
    "Nightly Short-Term Rent (€)", 
    min_value=20, 
    max_value=500, 
    value=80,
    step=5,
    help="Expected nightly rate for short-term rentals (Airbnb, etc.)"
)

occupancy_rate = st.sidebar.slider(
    "Short-Term Occupancy Rate (%)", 
    min_value=10, 
    max_value=100, 
    value=65,
    step=5,
    help="Expected percentage of nights booked per month"
)

# Expenses input
st.sidebar.subheader("💰 Monthly Expenses")
expenses = st.sidebar.number_input(
    "Total Monthly Expenses (€)", 
    min_value=100, 
    max_value=2000, 
    value=400,
    step=25,
    help="Include maintenance, management fees, insurance, taxes, etc."
)

# Additional parameters for more detailed analysis
st.sidebar.subheader("📈 Advanced Parameters")
initial_investment = st.sidebar.number_input(
    "Initial Investment (€)",
    min_value=10000,
    max_value=500000,
    value=60000,
    step=5000,
    help="Down payment + renovation + other initial costs"
)

# Advanced Financial Parameters
st.sidebar.subheader("🏦 Financing & Tax Parameters")

# Mortgage details
mortgage_amount = st.sidebar.number_input(
    "Mortgage Amount (€)",
    min_value=0,
    max_value=1500000,
    value=max(0, price - initial_investment),
    step=10000,
    help="Loan amount for property purchase"
)

interest_rate = st.sidebar.slider(
    "Mortgage Interest Rate (%)",
    min_value=1.0,
    max_value=8.0,
    value=3.5,
    step=0.1,
    help="Annual mortgage interest rate"
)

mortgage_years = st.sidebar.selectbox(
    "Mortgage Term (years)",
    options=[15, 20, 25, 30],
    index=3,
    help="Length of mortgage in years"
)

# Tax parameters
income_tax_rate = st.sidebar.slider(
    "Income Tax Rate (%)",
    min_value=0.0,
    max_value=50.0,
    value=28.0,
    step=1.0,
    help="Tax rate on rental income"
)

property_tax_rate = st.sidebar.slider(
    "Property Tax Rate (% of value)",
    min_value=0.0,
    max_value=3.0,
    value=0.8,
    step=0.1,
    help="Annual property tax as percentage of property value"
)

# Additional costs
annual_maintenance_rate = st.sidebar.slider(
    "Annual Maintenance (% of value)",
    min_value=0.5,
    max_value=3.0,
    value=1.5,
    step=0.1,
    help="Annual maintenance costs as percentage of property value"
)

insurance_cost = st.sidebar.number_input(
    "Annual Insurance (€)",
    min_value=200,
    max_value=5000,
    value=800,
    step=50,
    help="Annual property insurance cost"
)

# --- Advanced Financial Calculations ---

# Mortgage calculations
if mortgage_amount > 0:
    monthly_rate = (interest_rate / 100) / 12
    num_payments = mortgage_years * 12
    if monthly_rate > 0:
        monthly_mortgage = mortgage_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    else:
        monthly_mortgage = mortgage_amount / num_payments
else:
    monthly_mortgage = 0

# Annual costs
annual_property_tax = (property_tax_rate / 100) * price
annual_maintenance = (annual_maintenance_rate / 100) * price
annual_mortgage_payments = monthly_mortgage * 12
annual_insurance = insurance_cost

# Total annual costs
total_annual_costs = expenses * 12 + annual_property_tax + annual_maintenance + annual_mortgage_payments + annual_insurance

# Long-term rental calculations (after tax and all costs)
annual_long_gross = rent_long * 12
annual_long_net_before_tax = annual_long_gross - total_annual_costs
income_tax_long = max(0, annual_long_net_before_tax * (income_tax_rate / 100))
annual_long_after_tax = annual_long_net_before_tax - income_tax_long
yield_long_gross = (annual_long_gross / price) * 100 if price > 0 else 0
yield_long_net = (annual_long_after_tax / price) * 100 if price > 0 else 0
roi_long = (annual_long_after_tax / initial_investment) * 100 if initial_investment > 0 else 0
cash_flow_long = annual_long_after_tax

# Short-term rental calculations (after tax and all costs)
days_per_month = 30
monthly_nights_booked = (occupancy_rate / 100) * days_per_month
annual_short_gross = rent_short * monthly_nights_booked * 12
annual_short_net_before_tax = annual_short_gross - total_annual_costs
income_tax_short = max(0, annual_short_net_before_tax * (income_tax_rate / 100))
annual_short_after_tax = annual_short_net_before_tax - income_tax_short
yield_short_gross = (annual_short_gross / price) * 100 if price > 0 else 0
yield_short_net = (annual_short_after_tax / price) * 100 if price > 0 else 0
roi_short = (annual_short_after_tax / initial_investment) * 100 if initial_investment > 0 else 0
cash_flow_short = annual_short_after_tax

# Payback period and break-even analysis
best_cash_flow = max(cash_flow_long, cash_flow_short)
breakeven_years = initial_investment / best_cash_flow if best_cash_flow > 0 else float('inf')

# Mortgage principal payment (equity building)
if mortgage_amount > 0 and monthly_rate > 0:
    # Calculate principal paid in first year
    annual_principal_payment = 0
    remaining_balance = mortgage_amount
    for month in range(12):
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_mortgage - interest_payment
        annual_principal_payment += principal_payment
        remaining_balance -= principal_payment
else:
    annual_principal_payment = min(annual_mortgage_payments, mortgage_amount)

# Total return including equity building
total_return_long = annual_long_after_tax + annual_principal_payment
total_return_short = annual_short_after_tax + annual_principal_payment
total_roi_long = (total_return_long / initial_investment) * 100 if initial_investment > 0 else 0
total_roi_short = (total_return_short / initial_investment) * 100 if initial_investment > 0 else 0

# --- Main Content Area ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Long-Term Rental Analysis")
    
    # Basic metrics
    st.metric(
        label="Gross Annual Income",
        value=f"€{annual_long_gross:,.0f}",
        help="Total rental income before expenses and taxes"
    )
    
    st.metric(
        label="Net Cash Flow (After Tax)",
        value=f"€{annual_long_after_tax:,.0f}",
        delta=f"€{annual_long_after_tax/12:,.0f}/month",
        help="Annual cash flow after all expenses and taxes"
    )
    
    # Yield metrics
    col1_sub1, col1_sub2 = st.columns(2)
    with col1_sub1:
        st.metric(
            label="Gross Yield",
            value=f"{yield_long_gross:.2f}%",
            help="Gross rental income as % of property price"
        )
    with col1_sub2:
        st.metric(
            label="Net Yield",
            value=f"{yield_long_net:.2f}%",
            help="Net income after all costs as % of property price"
        )
    
    st.metric(
        label="Cash-on-Cash Return",
        value=f"{roi_long:.2f}%",
        help="Annual cash flow as % of initial investment"
    )
    
    if mortgage_amount > 0:
        st.metric(
            label="Total Return (incl. Equity)",
            value=f"{total_roi_long:.2f}%",
            help="Cash flow + mortgage principal payment as % of initial investment"
        )

with col2:
    st.subheader("🏖️ Short-Term Rental Analysis")
    
    # Basic metrics
    st.metric(
        label="Gross Annual Income",
        value=f"€{annual_short_gross:,.0f}",
        help="Total rental income before expenses and taxes"
    )
    
    st.metric(
        label="Net Cash Flow (After Tax)",
        value=f"€{annual_short_after_tax:,.0f}",
        delta=f"€{annual_short_after_tax/12:,.0f}/month",
        help="Annual cash flow after all expenses and taxes"
    )
    
    # Yield metrics
    col2_sub1, col2_sub2 = st.columns(2)
    with col2_sub1:
        st.metric(
            label="Gross Yield",
            value=f"{yield_short_gross:.2f}%",
            help="Gross rental income as % of property price"
        )
    with col2_sub2:
        st.metric(
            label="Net Yield",
            value=f"{yield_short_net:.2f}%",
            help="Net income after all costs as % of property price"
        )
    
    st.metric(
        label="Cash-on-Cash Return",
        value=f"{roi_short:.2f}%",
        help="Annual cash flow as % of initial investment"
    )
    
    if mortgage_amount > 0:
        st.metric(
            label="Total Return (incl. Equity)",
            value=f"{total_roi_short:.2f}%",
            help="Cash flow + mortgage principal payment as % of initial investment"
        )

# --- Comparison and Recommendations ---
st.subheader("🎯 Investment Recommendation")

col3, col4 = st.columns(2)

with col3:
    yield_difference = abs(yield_short_net - yield_long_net)
    income_difference = abs(annual_short_after_tax - annual_long_after_tax)
    
    if yield_short_net > yield_long_net:
        st.success(f"✅ **Short-Term Rental** is more profitable!")
        st.write(f"• **{yield_difference:.2f}%** higher net yield")
        st.write(f"• **€{income_difference:,.0f}** more annual net income")
        st.write(f"• Higher cash flow: €{cash_flow_short:,.0f}/year")
        st.write(f"• Requires active management and marketing")
    elif yield_long_net > yield_short_net:
        st.info(f"ℹ️ **Long-Term Rental** is more profitable!")
        st.write(f"• **{yield_difference:.2f}%** higher net yield")
        st.write(f"• **€{income_difference:,.0f}** more annual net income")
        st.write(f"• Higher cash flow: €{cash_flow_long:,.0f}/year")
        st.write(f"• More stable and predictable income")
    else:
        st.warning("⚖️ Both strategies show similar profitability")
        st.write(f"• Long-term: €{cash_flow_long:,.0f}/year")
        st.write(f"• Short-term: €{cash_flow_short:,.0f}/year")

with col4:
    st.subheader("📋 Investment Summary")
    
    best_strategy = 'Short-term' if yield_short_net > yield_long_net else 'Long-term'
    best_cash_flow = max(cash_flow_long, cash_flow_short)
    best_roi = max(roi_long, roi_short)
    
    st.write(f"**Property Price:** €{price:,.0f}")
    st.write(f"**Total Investment:** €{price:,.0f}")
    st.write(f"**Down Payment:** €{initial_investment:,.0f}")
    if mortgage_amount > 0:
        st.write(f"**Mortgage:** €{mortgage_amount:,.0f}")
        ltv_ratio = (mortgage_amount / price) * 100
        st.write(f"**LTV Ratio:** {ltv_ratio:.1f}%")
    
    st.write(f"**Best Strategy:** {best_strategy}")
    st.write(f"**Best Cash Flow:** €{best_cash_flow:,.0f}/year")
    st.write(f"**Best ROI:** {best_roi:.2f}%")
    st.write(f"**Payback Period:** {breakeven_years:.1f} years")
    
    # Investment grade assessment
    if best_roi >= 15:
        grade = "🏆 Excellent"
        grade_color = "green"
    elif best_roi >= 10:
        grade = "👍 Good"
        grade_color = "blue"
    elif best_roi >= 5:
        grade = "⚠️ Moderate"
        grade_color = "orange"
    else:
        grade = "❌ Poor"
        grade_color = "red"
    
    st.markdown(f"**Investment Grade:** :{grade_color}[{grade}]")

# --- Risk Analysis ---
st.subheader("⚠️ Risk Considerations")

risk_col1, risk_col2 = st.columns(2)

with risk_col1:
    st.markdown("**Long-Term Rental Risks:**")
    st.write("• Tenant vacancy periods")
    st.write("• Rent control regulations")
    st.write("• Property damage by tenants")
    st.write("• Market rent fluctuations")

with risk_col2:
    st.markdown("**Short-Term Rental Risks:**")
    st.write("• Seasonal demand variations")
    st.write("• Platform dependency (Airbnb, etc.)")
    st.write("• Regulatory changes and restrictions")
    st.write("• Higher management time requirement")


# --- Interactive Heatmap ---
st.subheader("📍 Rental Yield Heatmap - European Cities")
st.markdown("Explore average rental yields across different neighborhoods in major European cities")

# City selection
city_data = {
    "Lisbon": {
        "center": [38.7169, -9.139],
        "zoom": 11,
        "neighborhoods": {
            "neighborhood": [
                "Alfama", "Graça", "Baixa", "Chiado", "Parque das Nações",
                "Cascais", "Sintra", "Belém", "Santos", "Príncipe Real",
                "Campo de Ourique", "Estrela", "Lapa", "Avenidas Novas", "Benfica"
            ],
            "lat": [
                38.7112, 38.7203, 38.7101, 38.7084, 38.7687,
                38.6966, 38.7995, 38.6979, 38.7058, 38.7155,
                38.7217, 38.7094, 38.7064, 38.7436, 38.7499
            ],
            "lon": [
                -9.1304, -9.1324, -9.1393, -9.1414, -9.0934,
                -9.4226, -9.3773, -9.2028, -9.1528, -9.1463,
                -9.1663, -9.1604, -9.1683, -9.1476, -9.2170
            ],
            "yield": [5.2, 6.1, 4.8, 5.6, 7.3, 4.2, 3.8, 5.9, 6.4, 5.1, 5.7, 4.9, 4.5, 6.8, 7.1],
            "avg_price": [4500, 3800, 6200, 5800, 3200, 7500, 2900, 4800, 5200, 6800, 4200, 5500, 7200, 3600, 2800]
        }
    },
    "Madrid": {
        "center": [40.4168, -3.7038],
        "zoom": 11,
        "neighborhoods": {
            "neighborhood": [
                "Malasaña", "Chueca", "La Latina", "Sol", "Retiro",
                "Salamanca", "Chamberí", "Lavapiés", "Moncloa", "Argüelles",
                "Conde Duque", "Justicia", "Cortes", "Universidad", "Embajadores"
            ],
            "lat": [
                40.4267, 40.4235, 40.4139, 40.4165, 40.4130,
                40.4318, 40.4378, 40.4088, 40.4351, 40.4274,
                40.4289, 40.4210, 40.4145, 40.4198, 40.4067
            ],
            "lon": [
                -3.7012, -3.6958, -3.7081, -3.7026, -3.6844,
                -3.6823, -3.7033, -3.7004, -3.7180, -3.7181,
                -3.7113, -3.6976, -3.7003, -3.7081, -3.7035
            ],
            "yield": [6.8, 7.2, 6.1, 5.4, 5.9, 4.8, 6.3, 7.5, 5.7, 6.0, 6.4, 6.9, 5.8, 6.2, 7.3],
            "avg_price": [3800, 4200, 3200, 5500, 4800, 6800, 4500, 2900, 4000, 3900, 4100, 4300, 4600, 3700, 2800]
        }
    },
    "Paris": {
        "center": [48.8566, 2.3522],
        "zoom": 11,
        "neighborhoods": {
            "neighborhood": [
                "Le Marais", "Saint-Germain", "Montmartre", "Bastille", "République",
                "Belleville", "Oberkampf", "Canal Saint-Martin", "Pigalle", "Châtelet",
                "Latin Quarter", "Trocadéro", "Opéra", "Louvre", "Nation"
            ],
            "lat": [
                48.8566, 48.8540, 48.8867, 48.8532, 48.8676,
                48.8720, 48.8665, 48.8708, 48.8823, 48.8584,
                48.8503, 48.8635, 48.8708, 48.8606, 48.8473
            ],
            "lon": [
                2.3522, 2.3347, 2.3431, 2.3695, 2.3637,
                2.3808, 2.3712, 2.3658, 2.3370, 2.3470,
                2.3447, 2.2851, 2.3322, 2.3376, 2.3964
            ],
            "yield": [4.2, 3.8, 5.1, 4.9, 5.3, 6.2, 5.8, 5.5, 4.7, 3.9, 4.1, 3.2, 3.6, 3.4, 5.7],
            "avg_price": [9800, 11200, 7800, 8200, 7500, 6800, 7200, 7600, 8500, 10500, 9200, 12800, 10900, 11800, 6900]
        }
    },
    "Berlin": {
        "center": [52.5200, 13.4050],
        "zoom": 11,
        "neighborhoods": {
            "neighborhood": [
                "Mitte", "Prenzlauer Berg", "Kreuzberg", "Friedrichshain", "Charlottenburg",
                "Neukölln", "Schöneberg", "Wedding", "Moabit", "Tempelhof",
                "Wilmersdorf", "Steglitz", "Zehlendorf", "Spandau", "Reinickendorf"
            ],
            "lat": [
                52.5200, 52.5403, 52.4987, 52.5095, 52.5045,
                52.4814, 52.4862, 52.5504, 52.5194, 52.4730,
                52.4864, 52.4569, 52.4333, 52.5370, 52.5755
            ],
            "lon": [
                13.4050, 13.4104, 13.4034, 13.4531, 13.3096,
                13.4370, 13.3500, 13.3669, 13.3441, 13.3846,
                13.3089, 13.3171, 13.2619, 13.1956, 13.3249
            ],
            "yield": [5.8, 6.4, 7.1, 6.9, 5.2, 7.8, 6.2, 7.5, 6.7, 6.0, 5.6, 5.9, 4.8, 6.3, 6.8],
            "avg_price": [4800, 4200, 3600, 3800, 5200, 3200, 4000, 2900, 3700, 3900, 4600, 4100, 5800, 3300, 3400]
        }
    }
}

selected_city = st.selectbox(
    "🌍 Select City for Market Analysis",
    options=list(city_data.keys()),
    index=0,
    help="Choose a city to explore neighborhood rental yields"
)

# Get selected city data
current_city = city_data[selected_city]
neighborhood_data = pd.DataFrame(current_city["neighborhoods"])

# Create the map centered on selected city
m = folium.Map(location=current_city["center"], zoom_start=current_city["zoom"])

# Add markers for each neighborhood
for i, row in neighborhood_data.iterrows():
    # Color code based on yield performance
    if row["yield"] >= 6.5:
        color = "green"
        fill_color = "lightgreen"
    elif row["yield"] >= 5.5:
        color = "orange"  
        fill_color = "yellow"
    else:
        color = "red"
        fill_color = "lightcoral"
    
    # Create popup with detailed information
    popup_text = f"""
    <b>{row['neighborhood']}</b><br>
    Rental Yield: {row['yield']:.1f}%<br>
    Avg Price/m²: €{row['avg_price']:,}
    """
    
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=12,
        popup=folium.Popup(popup_text, max_width=200),
        tooltip=f"{row['neighborhood']}: {row['yield']:.1f}%",
        color=color,
        weight=2,
        fill=True,
        fill_color=fill_color,
        fill_opacity=0.7
    ).add_to(m)

# Add a legend
legend_html = '''
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 90px; 
     background-color: white; border:2px solid grey; z-index:9999; 
     font-size:14px; padding: 10px">
<p><b>Rental Yield Legend</b></p>
<p><i class="fa fa-circle" style="color:green"></i> High (≥6.5%)</p>
<p><i class="fa fa-circle" style="color:orange"></i> Medium (5.5-6.4%)</p>
<p><i class="fa fa-circle" style="color:red"></i> Low (<5.5%)</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Display the map
map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])

# Show details when a marker is clicked
if map_data["last_clicked"]:
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lon = map_data["last_clicked"]["lng"]
    
    # Find the closest neighborhood
    distances = np.sqrt((neighborhood_data["lat"] - clicked_lat)**2 + 
                       (neighborhood_data["lon"] - clicked_lon)**2)
    closest_idx = distances.idxmin()
    selected_neighborhood = neighborhood_data.iloc[closest_idx]
    
    st.info(f"**Selected:** {selected_neighborhood['neighborhood']} ({selected_city}) | "
            f"**Yield:** {selected_neighborhood['yield']:.1f}% | "
            f"**Avg Price/m²:** €{selected_neighborhood['avg_price']:,}")

# City comparison metrics
st.subheader(f"📊 {selected_city} Market Overview")
col_city1, col_city2, col_city3, col_city4 = st.columns(4)

with col_city1:
    avg_yield = neighborhood_data['yield'].mean()
    st.metric("Average Yield", f"{avg_yield:.1f}%")

with col_city2:
    avg_price = neighborhood_data['avg_price'].mean()
    st.metric("Avg Price/m²", f"€{avg_price:,.0f}")

with col_city3:
    max_yield = neighborhood_data['yield'].max()
    best_neighborhood = neighborhood_data[neighborhood_data['yield'] == max_yield]['neighborhood'].values[0]
    st.metric("Best Yield", f"{max_yield:.1f}%", delta=f"{best_neighborhood}")

with col_city4:
    min_price = neighborhood_data['avg_price'].min()
    cheapest_neighborhood = neighborhood_data[neighborhood_data['avg_price'] == min_price]['neighborhood'].values[0]
    st.metric("Lowest Price", f"€{min_price:,.0f}", delta=f"{cheapest_neighborhood}")

# --- City-specific regulatory information ---
st.markdown("---")
st.subheader(f"⚠️ {selected_city} Specific Risks & Regulations")

city_regulations = {
    "Lisbon": "AL license required for short-term rentals",
    "Madrid": "Registration required, max 90 days/year in some areas", 
    "Paris": "Primary residence rule, 120 days/year limit",
    "Berlin": "Zweckentfremdungsverbot - strict regulations apply"
}

st.write(f"**Local regulation:** {city_regulations.get(selected_city, 'Check local laws and regulations')}")

# --- City Comparison Quick Facts ---
st.markdown("---")
st.subheader("🏙️ City Comparison Quick Facts")
comparison_col1, comparison_col2 = st.columns(2)

with comparison_col1:
    all_cities_avg = {city: round(pd.DataFrame(data["neighborhoods"])["yield"].mean(), 1) for city, data in city_data.items()}
    st.markdown("**Average Rental Yields by City:**")
    for city, avg in sorted(all_cities_avg.items(), key=lambda x: x[1], reverse=True):
        emoji = "🟢" if avg >= 6.0 else "🟡" if avg >= 5.0 else "🔴"
        highlight = "**" if city == selected_city else ""
        st.write(f"{emoji} {highlight}{city}{highlight}: {avg}%")
        
with comparison_col2:
    all_cities_price = {city: round(pd.DataFrame(data["neighborhoods"])["avg_price"].mean(), 0) for city, data in city_data.items()}
    st.markdown("**Average Property Prices by City (€/m²):**")
    for city, avg in sorted(all_cities_price.items(), key=lambda x: x[1]):
        emoji = "💰" if avg >= 8000 else "💵" if avg >= 5000 else "💸"
        highlight = "**" if city == selected_city else ""
        st.write(f"{emoji} {highlight}{city}{highlight}: €{avg:,.0f}")

# --- Footer ---
st.markdown("---")
st.markdown("""
**Disclaimer:** This tool provides estimated calculations based on input parameters. 
Actual investment returns may vary due to market conditions, regulatory changes, and other factors. 
Always consult with financial and legal professionals before making investment decisions.
""")