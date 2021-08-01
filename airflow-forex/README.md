# Airflow - Forex
A project to understand airflow datapipe line using docker on development environment.
The main focus of this project is Airflow (not docker, spark, postgresql or hive)


## Dev environment Requirements
Note:IVD (Installed via Docker) 

| Requirement | Version  
| :---: | :---: | 
| Airflow  | 2.1.2 |
| Docker  | 20.10.7 |
| PostgreSQL (IvD)  | 11.4 |
| Hadoop (IvD)  | 3.1.1 |
| Adminer (IvD)  | 4.8 |
| Hive (IvD)  | 3.1.2 |
| Hue (IvD)  | 4.4.0 |
| Spark (IvD)  | 2.4.5 |

To run this project on your local environment, it is recommended(was developed with) the hardware specifications.

| Hardware Requirements | Version
| :---: | :---: | 
| Cores  | Minimum 2 |
| RAM  | Minimum 4 GB |

## Architecture 
A high level architecture of FOREX pipeline on docker
![Alt text](screenshots/forex_architecture.png?raw=true "Forex Architecture")

Components

####Airflow:

The datapipe line to interact with all below components

####Hadoop

Namenode: 
Datanode:

####Spark

Process FOREX currencies at scale.

####Hive

Interact with files in HDFS using SQL syntax using (HQL)

####Adminer

Tool to interact with Posgres database.

####Hue

Dashboard to view data from hive and HDFS

## The pipeline

1) The pipeline includes tasks for checking if rates are available on github gist via URL.
![Alt text](screenshots/forex_pipeline.png?raw=true "Forex Pipeline")

2) Check if the FOREX currency file is available at `mnt/airflow/dags/files/forex_currencies.csv`
3) Download rates from Github Gist (https://gist.github.com/dartion/4c96ec6349aa747f2b8fce09ff9c4d83)
4) Saving the rates on HDFS (can be viewed using HUE at http://localhost:32762/)
![Alt text](screenshots/hue_files.png?raw=true "View files on HUE")
5) Create tables on using Hive Operator
6) Do large processing on Spark using the python script to remove duplicated rows based on the base and last_update columns
![Alt text](screenshots/hue_files.png?raw=true "HUE_query")
7) Send email or Slack notification as required when a DAG/Task fail. In this project is it used only to send sample message.

Email ![Alt text](screenshots/slack_message.png?raw=true "Slack Example")
Slack ![Alt text](screenshots/email_gmail.png?raw=true "Email Example")

## Running
To start the pipeline, on the root directory of this project run
```./start.sh```

To restart the pipeline, on the root directory of this project run
```./start.sh```

To restart the pipeline, on the root directory of this project run
```./stop.sh```

*WARNING!*
To prune all docker images and containers run this
```./reset.sh```

Connections to setup on Airflow UI
1. **forex_api**
Conn Id: forex_api
Conn Type: HTTP
Host: https://gist.github.com/

2. **forex_path**
Conn Id: forex_path
Conn Type: File(path)
Extra: {"path":"/opt/airflow/dags/files"}

3. **hive_conn**
Conn Id: hive_conn
Conn Type: Hive Server 2 Thrift
Login: hive
Password: hive
Port: 10000

4. **spark_conn**
Conn Id: spark_conn
Conn Type: Spark
Host: spark://spark-master
Port: 7077

5. **Set email configuration in mnt/airflow/airflow.cfg**

6**slack_conn**
*Prerequisites:*
*On slack.com create a workspace, say airflow notifications*
*Create a channel "monitoring"*
Conn Id: slack_conn
Conn Type: HTTP
Host: https://hooks.slack.com/services/
Password: secret token generated from api.slack.com -> Apps -> Incoming Webhooks -> Webhook URL


## Individual DAG tests
Note: Before running in individual DAG tests on `airflow-forex_airflow` remember to create all connections!
1) is_forex_rates_available
 `airflow tasks test forex_data_pipeline is_forex_rates_available 2021-07-01`

2)is_forex_currencies_file_available

 `airflow tasks test forex_data_pipeline is_forex_currencies_file_available 2021-07-01`

3)downloading_rates

 `airflow tasks test forex_data_pipeline downloading_rates 2021-07-01`

4) saving_rates

 `airflow tasks test forex_data_pipeline saving_rates 2021-07-01`

5) creating_forex_rates_table

 `airflow tasks test forex_data_pipeline creating_forex_rates_table 2021-07-01`

###### If this does not work it is because of memory and/or CPUs running out! Increase them via docker -> Preferences and run ./restart.sh
6) forex_processing

 `airflow tasks test forex_data_pipeline forex_processing 2021-07-01`

7) send_email_notification

 `airflow tasks test forex_data_pipeline send_email_notification 2021-07-01` 

8) send_slack_notification

 `airflow tasks test forex_data_pipeline send_slack_notification 2021-07-01` 
