#!/bin/bash
if [ -f ~/.bash_profile ];
then
  . ~/.bash_profile
fi

cp -f /home/ec2-user/flasky/app/SuperTendCRM.db /home/ec2-user/flasky/db_bak/SuperTendCRM.db_$(date +"%Y%m%d_%H:%M")
