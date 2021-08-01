#Individual dag tests

1.is_forex_rates_available
 `airflow tasks test forex_data_pipeline is_forex_rates_available 2021-07-01`

2. is_forex_currencies_file_available
 `airflow tasks test forex_data_pipeline is_forex_currencies_file_available 2021-07-01`

3. downloading_rates
 `airflow tasks test forex_data_pipeline downloading_rates 2021-07-01`

4. saving_rates
 `airflow tasks test forex_data_pipeline saving_rates 2021-07-01`

5. creating_forex_rates_table
 `airflow tasks test forex_data_pipeline creating_forex_rates_table 2021-07-01`

## IF this does not work it is memory and cpus running out! Increase them via docker -> Preferences and run ./restart.sh 
Note: Remember to create all connection ids
6. forex_processing
 `airflow tasks test forex_data_pipeline forex_processing 2021-07-01`

7. send_email_notification
 `airflow tasks test forex_data_pipeline send_email_notification 2021-07-01` 

8. send_slack_notification
 `airflow tasks test forex_data_pipeline send_slack_notification 2021-07-01` 

