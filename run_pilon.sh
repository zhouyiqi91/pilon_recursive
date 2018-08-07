#! /bin/bash

config=`ls *.config`
bin_path=$(cd `dirname $0`;pwd)
nohup python -u ${bin_path}/pilon_run.py `pwd`/$config &
