from . import data_utils, time_utils
from sklearn.cluster import KMeans
import functools
import pandas as pd

from . import constant

def getClusterDataframe(start_time, end_time, dataframe):
    inRange_df = data_utils.getDataframe_inRange(
        dataframe=dataframe,
        start_time64=time_utils.fromString_toInt64(start_time),
        end_time64=time_utils.fromString_toInt64(end_time),
    )

    if not inRange_df.shape[0]:
        return

    canbeUsed_df = inRange_df[inRange_df["action"] == "updated"]
    canbeUsed_df = canbeUsed_df[
        ["time", "time64", constant.KW_DEVICE_TYPE, "data", constant.KW_MAC_ADDRESS, "value"]
    ]

    noOfCluster = (
        canbeUsed_df.groupby(by=[constant.KW_MAC_ADDRESS]).count().reset_index().mean()[any]
    )
    km = KMeans(
        n_clusters=int(noOfCluster),
        init="random",
        n_init=10,
        max_iter=2000,
        tol=1e-04,
        random_state=0,
    )

    canbeUsed_df["label"] = km.fit_predict(canbeUsed_df[["time64"]])

    uniqueMacs = canbeUsed_df[constant.KW_MAC_ADDRESS].unique()

    uniqueMacs_df_list = []

    for macAddr in uniqueMacs:
        uniqueMacs_df_list.append(
            canbeUsed_df[canbeUsed_df[constant.KW_MAC_ADDRESS] == macAddr][
                ["time64", "value", "label"]
            ]
            .rename(columns={"value": macAddr})
            .groupby(by="label")
            .max()
            .reset_index()
        )

    final_df = functools.reduce(
        lambda x, y: pd.merge(x, y, left_on="label", right_on="label", how="outer"),
        uniqueMacs_df_list,
    )

    final_df = final_df.groupby(by=final_df.columns, axis=1).mean()

    list_time64 = data_utils.getListOf_time64(final_df.columns)
    final_df["time64"] = final_df.apply(
        lambda row: data_utils.getTime64(row, list_time64), axis=1
    )
    final_df["date"] = pd.to_datetime(final_df["time64"], unit="s")
    # final_df = final_df.drop(columns=list_time64)
    final_df = final_df.sort_values(by=["time64"])

    return final_df
