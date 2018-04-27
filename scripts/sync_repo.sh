#!/bin/bash

project_dir="/home/pi/projects/email_controlled_pi"
master_app_dir="$project_dir/master"
stable_app_dir="$project_dir/stable"

# Update current directory
cd $project_dir
git pull origin master

# Update submodules
git submodule update --init --recursive

# Checkout master branch in the master directory
cd $master_app_dir
git checkout master
git pull

# Checkout stable branch in the stable directory
cd $stable_app_dir
git checkout stable
git pull
