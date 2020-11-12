# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3
import sys
import argparse

DEFAULT_STRING_LENGTH = 400
GLUE_TO_DMS = {
                "string": "STRING",
                "double": "REAL8",
                "timestamp": "TIMESTAMP",
                "decimal": "NUMERIC",
                "bigint": "INT8",
                "int": "INT4",
                "smallint": "INT2",
                "date": "DATE"
            }

def parse_type(data_type):
    if data_type.startswith("decimal"):
        return data_type.split("(")[0]
    else:
        return data_type



if __name__ == "__main__":

    try:

        # Read in command-line parameters
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--AWS Glue database", required=True, dest="gluedb", help="Name of the AWS Glue database")
        parser.add_argument("-f", "--Output file name ", required=True, dest="output", help="Name of the output .json document")

        # If no options are set, print help and exit, otherwise parse args
        if len(sys.argv) <= 1:
            parser.print_help()
            sys.exit(1)

        args = parser.parse_args()
        glue_database = args.gluedb
        json_file = args.output

        client = boto3.client('glue')
        tables = client.get_tables(DatabaseName=glue_database)
        tbl_path, tbl, prev_tbl, tbl_count = None, None, None, 0
        cols, tbls = [], []
        for glue_table_dict in tables["TableList"]:
            tbl = glue_table_dict["Name"]
            if prev_tbl is None:
                prev_tbl = tbl
            elif prev_tbl != tbl:
                tbl_owner = glue_table_dict["StorageDescriptor"]["Location"].split("/")[-3]
                tbl_path = tbl_owner + "/" + prev_tbl
                tbl_dict = {
                            "TableName": prev_tbl, 
                            "TablePath": tbl_path,
                            "TableOwner": tbl_owner,
                            "TableColumns": cols
                            }
                tbls.append(tbl_dict)
                tbl_count, cols, prev_tbl = tbl_count+1, [], tbl

            for col in glue_table_dict["StorageDescriptor"]["Columns"]:
                data_type = parse_type(col["Type"])
                col_dict = {
                            "ColumnName": col["Name"], 
                            "ColumnType": GLUE_TO_DMS[data_type],
                            "ColumnNullable":  "true",
                            "ColumnIsPk": "false"
                            }
                #Derive length of column
                if data_type == "string":
                    col_dict["ColumnLength"] = DEFAULT_STRING_LENGTH
                if data_type == "decimal":
                    col_dict["ColumnPrecision"], col_dict["ColumnScale"] = col["Type"].split("(")[1][0] \
                        , col["Type"].split("(")[1][2]
                cols.append(col_dict)

        parent_dict = {"TableCount": tbl_count, "Tables": tbls}
        with open(json_file, "w") as f:
          f.write(json.dumps(parent_dict))

        print("Completed...")

    except Exception as error:
        print(f"An exception occurred {error}")


