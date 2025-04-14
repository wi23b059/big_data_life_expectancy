# Life Expectancy Dashboard (Docker Deployment)

## Description
This dashboard visualizes key health factors affecting life expectancy including smoking, obesity, and GDP.

## How to Use

### 1. Build and Run with Docker
```bash
docker-compose up --build
```

### 2. Open in Browser
Navigate to: [http://localhost:8501](http://localhost:8501)

## Structure
- `life_expectancy_dashboard.py`: Streamlit dashboard script
- `quelldateien/`: Data sources
- `Dockerfile`, `docker-compose.yml`: Deployment setup
- `notebooks/`: Original and improved Jupyter analysis

for Streamlit dashboard
# streamlit run life_expectancy_dashboard.py