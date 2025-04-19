FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy files to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install streamlit \
    pandas \
    matplotlib \
    seaborn \
    plotly \
    pycountry \
    xlrd \
    openpyxl \
    protobuf \
    pymongo \
    scikit-learn \
    numpy

# Configure Streamlit for headless mode and reduce CORS warnings
RUN mkdir -p ~/.streamlit && echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = 8501\n\
" > ~/.streamlit/config.toml

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "life_expectancy_dashboard.py", "--server.port=8501", "--server.enableCORS=false"]