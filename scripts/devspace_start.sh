#!/bin/bash
set +e  # Continue on errors

echo "api devspace-farm.${NAMESPACE}.svc.cluster.local" > /etc/host.aliases
echo "export HOSTALIASES=/etc/host.aliases" >> /etc/profile
. /etc/profile
COLOR_CYAN="\033[0;36m"
COLOR_RESET="\033[0m"
echo -e "${COLOR_CYAN}
 ######     ##     #####    ##   ## 
 ##        ####    ##  ##   ### ### 
 ##       ##  ##   ##  ##   ####### 
 ####     ######   #####    ## # ## 
 ##       ##  ##   ####     ##   ## 
 ##       ##  ##   ## ##    ##   ## 
 ##       ##  ##   ##  ##   ##   ## 

 ${COLOR_RESET}
Welcome to your development container!
- Run \`${COLOR_CYAN}make start svc=$@ ${COLOR_RESET}\` to run the application"      

bash
