#!/usr/bin/bash

# Simple shell script to start MariaDB from a container
# This uses the standard MySQL envars to configure key values
# 
# Specify your own values and pull from a secrets vault, if you choose to.

MYSQLROOTPASSWD="CHANGE-ME"
MYSQLUSER="farm"
MYSQLPASSWD="change_me"
MYSQLDB="FarmTasks"

docker run --name farm-mariadb -e MYSQL_ROOT_PASSWORD=$MYSQLROOTPASSWD -e MYSQL_USER=$MYSQLUSER -e MYSQL_PASSWORD=$MYSQLPASSWD -e MYSQL_DATABASE=$MYSQLDB -p 3306:3306 -d mariadb:latest