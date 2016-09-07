#!/bin/bash

export JAVA_HOME=/usr/lib/java/jdk
export MASTER=spark://$masternode$:7077
export SPARK_HOME=/usr/lib/spark/spark
export HADOOP_HOME=/usr/lib/hadoop/hadoop
export HADOOP_CONF_DIR=/etc/hadoop
export ZEPPELIN_MEM=-Xmx4g

export PYTHONPATH=/usr/bin/python3
