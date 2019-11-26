import pandas as pd
from sqlalchemy import create_engine


def buildQuery(tableName):
    return "SELECT * from " + tableName


def queryTable(
    tableName,
    host_ip="192.168.1.223",
    database_name="sipiot",
    user="sip",
    password="jZSS7GX7",
    port=33060,
):
    db_string = (
        "mysql+pymysql://"
        + user
        + ":"
        + str(password)
        + "@"
        + str(host_ip)
        + ":"
        + str(port)
        + "/"
        + database_name
    )

    engine = create_engine(db_string)
    connection = engine.connect()

    object_df = pd.read_sql(buildQuery(tableName), connection)
    return object_df

