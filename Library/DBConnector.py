import psycopg2 as pg
from sshtunnel import SSHTunnelForwarder
import os
from Library.Config import dumplogger

def connect_postgresql(dbname='uat'):
    try:
        dumplogger.info('Connecting to the PostgreSQL Database...')
        ssh_tunnel = SSHTunnelForwarder(
                ("bastion.dev.k8s-cluster.pickupp-devops.net",22),
                ssh_username="ubuntu",
                ssh_pkey= os.path.abspath(os.getcwd())+'/Tools/k8s-dbeaver',
                remote_bind_address=('pickupp-dev-12-aurora.cluster-c4tut00agkr8.ap-southeast-1.rds.amazonaws.com', 5432)
            )
        ssh_tunnel.start()  
        
        conn = pg.connect(
               host='127.0.0.1',
               port=ssh_tunnel.local_bind_port,
               user='pickupp',
               password= 'QcgALyevFSKDRXaUw4MGhL4UptY3QmCJ',
               database=dbname
            )
    except:
        dumplogger.exception('Connection Has Failed...')
    return conn

def execute_postgresql(conn, query):
    dumplogger.info('Executing SQL Query...')
    dumplogger.info("SQL Query String : %s" % str(query))
    db_cursor = conn.cursor()
    db_cursor.execute(query)
    conn.commit()

def execute_postgresql_fetchone(conn, query):
    dumplogger.info('Executing SQL Query And Fetch Data...')
    dumplogger.info("SQL Query String : %s" % str(query))
    db_cursor = conn.cursor()
    db_cursor.execute(query)
    conn.commit()
    return db_cursor.fetchone()

def execute_postgresql_fetchmany(conn, query, fetch_amount):
    dumplogger.info('Executing SQL Query And Fetch Many Data...')
    dumplogger.info("SQL Query String : %s" % str(query))
    db_cursor = conn.cursor()
    db_cursor.execute(query)
    conn.commit()
    return db_cursor.fetchmany(fetch_amount)

def execute_postgresql_fetchall(conn, query):
    dumplogger.info('Executing SQL Query And Fetch All Data...')
    dumplogger.info("SQL Query String : %s" % str(query))
    db_cursor = conn.cursor()
    db_cursor.execute(query)
    conn.commit()
    return db_cursor.fetchall()
