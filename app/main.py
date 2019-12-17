from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse

import os
import pandas as pd
import traceback
import requests

from Utils import calculate, data_utils, database, service, time_utils, constant

BACKEND_DEVICELOG = "http://192.168.1.36:3000/api/v3/DeviceLogs/queryGeneral"


def getPhase_params(
    light_down_mac,
    photo_table_mac,
    photo_facedown_mac,
    photo_faceup_mac,
    phase0_startTime,
    phase0_endTime,
    phase1_startTime,
    phase1_endTime,
):
    selected_devices_mac = [
        light_down_mac,
        photo_table_mac,
        photo_faceup_mac,
        photo_facedown_mac,
    ]

    print("\n\nSELECTED DEVICES: ", selected_devices_mac)

    try:
        # Real Data using Backend API
        payload = {
            "arrayDevice": [selected_devices_mac],
            "[arrayTime][0]": [phase0_startTime, phase0_endTime],
            "[arrayTime][1]": [phase1_startTime, phase1_endTime],
        }

        response = requests.get(BACKEND_DEVICELOG, payload)
        deviceLog_df = pd.DataFrame.from_dict(response.json()["data"])

        print(
            "\n\n\nYAYYYYYYYY! GOT THE DATAFRAME FROM BACKEND, shape of it: ",
            deviceLog_df.shape,
        )
        print("DATAFRAME COLUMNS: ", deviceLog_df.columns)

        # Fake data
        deviceLog_df = pd.read_csv("./DeviceLog.csv")

    except Exception as e:
        print("Type Error: ", e)
        print(traceback.format_exc())
        return {"error": "Error when trying to load data", "errstr": e}

    # Validate deviceLog_df
    if not deviceLog_df.shape[0]:
        return {"error": "Device Log has length = 0"}

    # Choose Device
    selected_df = deviceLog_df[deviceLog_df[constant.KW_MAC_ADDRESS].isin(selected_devices_mac)]

    # Validate selected_df
    if not selected_df.shape[0]:
        return {"error": "No event for selected Device"}

    # Enrich data
    try:
        selected_df["time"] = pd.to_datetime(selected_df[constant.KW_CREATED_LOG_AT])
        selected_df["time64"] = selected_df["time"].apply(time_utils.time2Int)
        selected_df["value"] = selected_df.apply(
            lambda row: data_utils.extractValue(row), axis=1
        )
    except Exception as e:
        print("Type Error: ", e)
        print(traceback.format_exc())
        return {"error": "Error when trying to enrich data", "errstr": e}

    # Get Phase
    try:
        phase0_df = service.getClusterDataframe(
            start_time=phase0_startTime, end_time=phase0_endTime, dataframe=selected_df,
        )
    except Exception as e:
        print("Type Error: ", e)
        print(traceback.format_exc())
        return {"error": "Error when trying to load phase 0 data", "errstr": e}

    try:
        phase0_A, phase0_B = calculate.getAB_fromDevice(
            y_device_mac=photo_table_mac,
            x_device_mac=photo_faceup_mac,
            dataframe=phase0_df,
        )
    except Exception as e:
        print("Type Error: ", e)
        print(traceback.format_exc())
        return {
            "error": "Error when trying to load A B from phase 0 data",
            "errstr": e,
        }

    try:
        phase1_df = service.getClusterDataframe(
            start_time=phase1_startTime, end_time=phase1_endTime, dataframe=selected_df,
        )
    except Exception as e:
        print("Type Error: ", e)
        print(traceback.format_exc())
        return {"error": "Error when trying to load phase 1 data", "errstr": e}

    try:
        phase1_A, phase1_B = calculate.getAB_fromDevice(
            y_device_mac=photo_table_mac,
            x_device_mac=light_down_mac,
            dataframe=phase1_df,
        )
    except Exception as e:
        return {
            "error": "Error when trying to load A B from phase 1 data",
            "errstr": e,
        }

    return phase0_A, phase0_B, phase1_A, phase1_B


# App
app = Flask(__name__)
api = Api(app)


# API Class
calAB_parser = reqparse.RequestParser()
calAB_parser.add_argument("light_down_mac", type=str, required=True)
calAB_parser.add_argument("photo_table_mac", type=str, required=True)
calAB_parser.add_argument("photo_facedown_mac", type=str, required=True)
calAB_parser.add_argument("photo_faceup_mac", type=str, required=True)
calAB_parser.add_argument("phase0_startTime", type=str, required=True)
calAB_parser.add_argument("phase0_endTime", type=str, required=True)
calAB_parser.add_argument("phase1_startTime", type=str, required=True)
calAB_parser.add_argument("phase1_endTime", type=str, required=True)
calAB_parser.add_argument("setPoint", type=int, required=True)


class calculate_AB(Resource):
    def get(self):
        args = calAB_parser.parse_args()

        LIGHT_DOWN_MAC = args["light_down_mac"]
        PHOTO_TABLE_MAC = args["photo_table_mac"]
        PHOTO_FACEDOWN_MAC = args["photo_facedown_mac"]
        PHOTO_FACEUP_MAC = args["photo_faceup_mac"]

        phase0_startTime = args["phase0_startTime"]
        phase0_endTime = args["phase0_endTime"]
        phase1_startTime = args["phase1_startTime"]
        phase1_endTime = args["phase1_endTime"]

        setPoint = args["setPoint"]

        selected_devices_mac = [
            LIGHT_DOWN_MAC,
            PHOTO_TABLE_MAC,
            PHOTO_FACEUP_MAC,
            PHOTO_FACEDOWN_MAC,
        ]

        try:
            phase0_A, phase0_B, phase1_A, phase1_B = getPhase_params(
                LIGHT_DOWN_MAC,
                PHOTO_TABLE_MAC,
                PHOTO_FACEDOWN_MAC,
                PHOTO_FACEUP_MAC,
                phase0_startTime,
                phase0_endTime,
                phase1_startTime,
                phase1_endTime,
            )
        except Exception as e:
            print("Type Error: ", e)
            print(traceback.format_exc())
            return {
                "error": "Error when trying to load Params from 2 Phases",
                "errstr": e,
            }

        try:
            A, B = calculate.calAB_from2Phase(
                setPoint=setPoint,
                phase0_a=phase0_A,
                phase0_b=phase0_B,
                phase1_a=phase1_A,
                phase1_b=phase1_B,
            )
        except Exception as e:
            print("Type Error: ", e)
            print(traceback.format_exc())
            return {"error": "Error when trying to load calculate A B", "errstr": e}

        return {"A": A, "B": B}


calDim_parser = calAB_parser.copy()
calDim_parser.add_argument("upValue", type=int, required=True)


class calculate_dim(Resource):
    def get(self):
        args = calDim_parser.parse_args()

        LIGHT_DOWN_MAC = args["light_down_mac"]
        PHOTO_TABLE_MAC = args["photo_table_mac"]
        PHOTO_FACEDOWN_MAC = args["photo_facedown_mac"]
        PHOTO_FACEUP_MAC = args["photo_faceup_mac"]

        phase0_startTime = args["phase0_startTime"]
        phase0_endTime = args["phase0_endTime"]
        phase1_startTime = args["phase1_startTime"]
        phase1_endTime = args["phase1_endTime"]

        setPoint = args["setPoint"]
        upValue = args["upValue"]

        selected_devices_mac = [
            LIGHT_DOWN_MAC,
            PHOTO_TABLE_MAC,
            PHOTO_FACEUP_MAC,
            PHOTO_FACEDOWN_MAC,
        ]

        try:
            phase0_A, phase0_B, phase1_A, phase1_B = getPhase_params(
                LIGHT_DOWN_MAC,
                PHOTO_TABLE_MAC,
                PHOTO_FACEDOWN_MAC,
                PHOTO_FACEUP_MAC,
                phase0_startTime,
                phase0_endTime,
                phase1_startTime,
                phase1_endTime,
            )
        except Exception as e:
            print("Type Error: ", e)
            print(traceback.format_exc())
            return {
                "error": "Error when trying to load Params from 2 Phases",
                "errstr": e,
            }

        try:
            calDim = calculate.calDownDim_exp(
                setPoint=setPoint,
                upValue=upValue,
                phase0_a=phase0_A,
                phase0_b=phase0_B,
                phase1_a=phase1_A,
                phase1_b=phase1_B,
            )
        except Exception as e:
            print("Type Error: ", e)
            print(traceback.format_exc())
            return {"error": "Error when trying to load calculate A B", "errstr": e}

        return {"Dim": calDim, "percendDim": calDim * 100 / 255}


# Add endpoint
api.add_resource(calculate_AB, "/calAB")
api.add_resource(calculate_dim, "/calDim")


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
