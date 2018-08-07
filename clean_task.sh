#!/bin/bash

ps -ef|grep `pwd`|grep -v "grep"|awk '{print $2}'|xargs kill -9
