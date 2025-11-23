# roi--optimizer

Rental Yield & ROI Optimizer — Streamlit app to compare long-term vs short-term rental returns and visualize neighborhood yields.

## Quick summary

Built with Streamlit, pandas, numpy, folium and streamlit-folium.
Main script: app.py
Streamlit config: .streamlit/config.toml (server settings)
Purpose: estimate yields, ROI, payback and show an interactive map for sample European cities.

## Requirements

Python 3.8+
Install dependencies: pip install -r requirements.txt

## Run locally

1. Create & activate virtual env:
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
2. Install dependencies:
   pip install -r requirements.txt
3. Run the app:
   streamlit run app.py
   or to bind to all interfaces / port:
   streamlit run app.py --server.address 0.0.0.0 --server.port 5000

## Structure

- app.py — main Streamlit application
- .streamlit/config.toml — Streamlit server config (headless, port, address)
- requirements.txt — Python packages
- README.md — this file

## Notes

The included config.toml must be located at .streamlit/config.toml for Streamlit to pick it up.
If deploying to a cloud (Streamlit Sharing/Render/Heroku) add a Procfile or platform-specific settings.

## Disclaimer

This tool provides estimates only. Consult professionals before investing.
