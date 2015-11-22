#!bin/bash
# This is the setup file for project 3. 
# Run this before using the project. 
# this will wipe out your existing database. Be careful.
# 

echo "Verifying prerequisites"
echo " "
for fn in `cat prerequisites.txt`; do
    echo "the next prerequisite is $fn[0]"
    if pip list | grep ${fn[0]}; then
        echo "requirement found"
    else 
        echo "$fn not found, please install using pip."
    fi
done
