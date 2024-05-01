FROM apache/airflow:2.9.0

# Cài đặt thư viện yfinance
RUN pip install apache-airflow==${AIRFLOW_VERSION} pymongo==4.3.3
RUN pip install yfinance
