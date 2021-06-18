from mock import MagicMock
import pandas as pd
import os
import numpy as np
np.corrcoef

RAD_ROOT = os.path.dirname(os.path.abspath(__file__))
RAD_ROOT = os.path.dirname(RAD_ROOT)
RAD_ROOT = os.path.dirname(RAD_ROOT)
RAD_ROOT = os.path.dirname(RAD_ROOT)
print(RAD_ROOT)

QUERY_MAP = {
    'SELECT * FROM stale_final_reports_upload WHERE RECORDDATE = \'2020-03-31\'': 'VIEW_STALE_FINAL_OUTPUT_2020-03-31_upload.csv',
}

def get_dataframe(table = 'current', chunksize = None):
    print(table)
    if table in QUERY_MAP:
        table = QUERY_MAP[table]
    table_file = RAD_ROOT + '/Data/' + table
    if chunksize:
        return [pd.read_csv(table_file)]
    if not os.path.exists(table_file):
        print(f"Need to add mock data for:|{table}|")
        return pd.DataFrame()
    return pd.read_csv(table_file)

def get_config_attribute(config_name):
    if config_name == 'BD_DYNAMIC_THRESHOLDING':
        config = {"FP_FACTOR": 0.1, "NO_VIOLATION_FACTOR": -0.02, "STALE_DAYS_FACTOR": 0.0, "FINAL_COLUMN_NAME": "RAD2RMS_THRESHOLD_FLOOR_ROUNDUP",
                  "CAP_FLOOR": {"BD_SDS": {"pair1": {"cap": 0.5, "floor": 0.05}}, "BD_CB": {"pair1": {"cap": 5.0, "floor": 0.5}, "pair2": {"cap": 0.5, "floor": 0.05}},
                                "BD_CORP": {"pair1": {"cap": 5.0, "floor": 0.5}, "pair2": {"cap": 0.5, "floor": 0.05}}, "BD_GOVT": {"pair1": {"cap": 2.0, "floor": 0.2}, "pair2": {"cap": 0.2, "floor": 0.02}}}}
    elif config_name =='BD_MARKET_CAP_FLOOR':
        config = {
            'ID1_CORP': {'cap': 1, 'floor': 0.5}
                                   }
    else:
        config = {"FP_FACTOR": 0.1, "NO_VIOLATION_FACTOR": -0.02, "STALE_DAYS_FACTOR": -0.1, "FINAL_COLUMN_NAME": "RAD2RMS_THRESHOLD_FLOOR_ROUNDUP", "ABS_RISK_LIMIT": 1000}

    class ConfigMock:
        CONFIG_VALUE = config

    return ConfigMock

def insert(report, table, if_exists='append'):
    table_file = RAD_ROOT + '/Data/' + table + '.csv'
    report.to_csv(table_file, index = False)

def check_existed_date_running(report_table, report_date):
    return False

def excute(sql):
    pass

def normalize_report_based_table(report, report_table, database_manager, ignored_columns):
    return report


# assign mock properties
database_manager = MagicMock()
database_manager.get_dataframe = get_dataframe
database_manager.insert = insert
database_manager.check_existed_date_running = check_existed_date_running
database_manager.excute = excute
database_manager.normalize_report_based_table = normalize_report_based_table

# print(database_manager.get_dataframe())
database_manager.get_config_attribute = get_config_attribute