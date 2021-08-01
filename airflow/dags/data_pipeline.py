from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.email import EmailOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

from datetime import datetime, timedelta
import csv
import requests
import json

# Specify common attributes of the tasks
# Owner of the dag
# Email someone on failure of task
# Email someone when a task is retried
# Someone's email
# How many times to retry a task
# After when to retry the task?
default_args = {
	"owner": "airflow",
	"email_on_failure": False,
	"email_on_retry": False,
	"email": "dartion@gmail.com",
	"retry": 1,
	"retry_delay": timedelta(minutes=5)
}

# Download corresponding currencies based on USD
# USD;EUR USD;GBY 
# Write the dict to forex_rates.json
def download_rates():
    BASE_URL = "https://gist.githubusercontent.com/dartion/4c96ec6349aa747f2b8fce09ff9c4d83/raw/"
    ENDPOINTS = {
        'USD': 'api_forex_exchange_usd.json',
        'EUR': 'api_forex_exchange_eur.json'
    }
    with open('/opt/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for idx, row in enumerate(reader):
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get(f"{BASE_URL}{ENDPOINTS[base]}").json()
            outdata = {'base': base, 'rates': {}, 'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/opt/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')

def _get_message() -> str:
    return "Hi from forex_data_pipeline"

# dag_id=forex_data_pipeline
# starts at 1st of July 2021
# schedule interval every day
# Do not run all triggered dags between today and dag start date!
with DAG(
	dag_id 				= "forex_data_pipeline", 
	start_date 			= datetime(2021,7,1), 
 	schedule_interval	= "@daily", 
 	default_args		= default_args,
 	catchup				= False ) as dag:
	
	# Check if FOREX data is available or not using a HTTPSensor
	# poke_interval is the interval to poke and check if url is working as expected and end after timeout=20
	# Add a connection on UI - Admin->Connection-> forex_api -> HTTP -> https://gist.github.com	
	is_forex_rates_available = HttpSensor(
		task_id 		= "is_forex_rates_available",
		http_conn_id	= "forex_api",
		endpoint 		= "/dartion/4c96ec6349aa747f2b8fce09ff9c4d83",
		response_check 	= lambda response: "rates" in response.text,
		poke_interval 	= 5,
		timeout 		= 20
	)

	# Check if currencies file exist in the system
	# Add another connection file path
	# Airflow UI -> Connections -> Add -> 'forex_path' -> Extras-> {"file_path": "{"path":"/opt/airflow/dags/files"}
	# 
	is_forex_currencies_file_available = FileSensor(
		task_id		 	= "is_forex_currencies_file_available",
		fs_conn_id 		= "forex_path",
		filepath		= "forex_currencies.csv",
		poke_interval	= 5,
		timeout			= 20
	)

    #PythonOperator dag to call the python function downloading_rates
	downloading_rates = PythonOperator(
		task_id 		= "downloading_rates",
		python_callable = download_rates
	)


	# Saving the rates to HDFS using BashOperator
	# Use HUE to visualise HDFS
	# http://localhost:32762/
	# root and root for username and password
	saving_rates = BashOperator(
		task_id 		= "saving_rates",
		bash_command	= """
            hdfs dfs -mkdir -p /forex && \
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
        """
    )

	# Use Hive operator to execute HQL query
	# Create table for following columns similar to forex.json
	# Create hive_conn in Airflow UI -> Admin -> Connections
	# Add -> hive_conn -> Hive Server 2 Thrift -> Host= hive-server -> Login= hive and hive
	# Port 10000
	creating_forex_rates_table = HiveOperator(
    	task_id 		 = "creating_forex_rates_table",
    	hive_cli_conn_id = "hive_conn",
    	hql				 = """
        CREATE EXTERNAL TABLE IF NOT EXISTS forex_rates(
            base STRING,
            last_update DATE,
            eur DOUBLE,
            usd DOUBLE,
            nzd DOUBLE,
            gbp DOUBLE,
            jpy DOUBLE,
            cad DOUBLE
            )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
    """
    )

	# Execute script at /opt/airflow/dags/scripts/forex_processing.py
	# Do the large processing part in Spark
	# Add a connection on Airflow UI
	# UI -> Admin -> Connections -> Add -> spark_conn ->
	forex_processing = SparkSubmitOperator(
		task_id 	= "forex_processing",
		application = "/opt/airflow/dags/scripts/forex_processing.py",
		conn_id 	= "spark_conn",
		verbose		= False
	)

	# Sample Email notication
	send_email_notification = EmailOperator (
		task_id 	 = "send_email_notification",
		to 			 = "dartion@gmail.com",
		subject 	 = "forex_data_pipeline",
		html_content = "<h2> forex_data_pipeline</h2>"
	)
    
	# Sample Slack notification
	send_slack_notification = SlackWebhookOperator(
        task_id="send_slack_notification",
        http_conn_id="slack_conn",
        message=_get_message(),
        channel="#monitoring"
    )

	is_forex_rates_available >> is_forex_currencies_file_available >> downloading_rates >> saving_rates
	saving_rates >> creating_forex_rates_table >> forex_processing 
	forex_processing >> send_email_notification >> send_slack_notification
 

    
	
