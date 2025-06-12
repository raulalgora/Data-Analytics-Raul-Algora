# Interactive Real Estate Analysis Platform

<div align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" height="40" alt="python" />
  <img width="12" />
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original.svg" height="40" alt="postgresql" />
  <img width="12" />
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original.svg" height="40" alt="docker" />
</div>

## 📌 Project Description

An interactive platform with dynamic maps that integrates key data about Valencia's districts to support informed housing decisions. Developed after the recent floods in Valencia, it allows users to analyze how these events could impact the real estate market.

## 🎯 Problem and Solution

Following the recent events in Valencia, a redistribution in housing demand and rising prices are expected. This tool helps answer key questions such as:
- Where will prices increase the most?
- Which areas offer the best value for money?
- Which districts provide better access to essential services?

Our platform enables users to:
- Filter based on income and preferences
- Visualize districts with color-coded indicators
- See green space distribution
- Access detailed data for each district
- Compare indicators between zones

## 🛠️ Technical Architecture

The project is structured into four main components:

### 1. Data Ingestion
- **Sources**: Valencia City Council (API), INE (XLSX), Idealista (HTML)
- **Data collected**: Schools, hospitals, metro, green areas, rental prices, and their variations

### 2. Data Processing
- Python for data cleaning and transformation
- PostgreSQL for storage
- Shapely for geospatial analysis
- Equivalency table to unify district naming

### 3. Visualization
- Web interface built with Streamlit and Folium
- Interactive maps with district selection
- Filtering by monthly income
- Toggleable layers (districts, green spaces)

### 4. Containerization and Automation
- Docker containers for each component
- Luigi for task orchestration
- Automated data pipeline

## 📊 Business Value

The project targets two business models:

**B2B**: Subscription model for real estate agencies and professionals with detailed analytics.

**B2C**: Freemium model for individual users with a zone comparison tool.

## 🚀 Next Steps

Future versions may include:
- Crime data
- Supermarket and shopping center information
- Public transport data (EMT, Valenbisi)
- Future price predictions

<img width="755" alt="Screenshot 2025-03-31 at 10 26 35" src="https://github.com/user-attachments/assets/f45dae75-9ed6-45a1-8b48-b22ce25315b8" />

