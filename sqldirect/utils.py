import os

def find_connection():
    if "SQLDIRECT_CONN_STR" in os.environ:
        conn = os.environ["SQLDIRECT_CONN_STR"]
    else:
        conn = ":memory:"

    return conn