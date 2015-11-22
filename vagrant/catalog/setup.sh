#!bin/bash
# This is the setup file for project 3. 
# Run this before using the project. 
# this will wipe out your existing database. Be careful.
# 

echo "Verifying prerequisites"
echo " "
for fn in `cat prerequisites.txt`; do
    echo "the next prerequisite is $fn"
    cat $fn
done


if pip list | grep unicodecsv; then
    echo "requirement found"
else 
    echo "unicodecsv not found, please install using pip."
    exit 1
fi
if pip list | grep Flask-SeaSurf; then
    echo "requirement found"
else
    echo "Flask-SeaSurf not found, please install using pip."
    exit 1
fi
if pip list | grep Flask; then
    echo "requirement found"
else
    echo "Flask not found, please install using pip."
    exit 1
fi
echo "Creating or recreating book database..."
echo " "
rm bookcatalog.db
python database_setup.py
echo " "
echo "Book database created or recreated."
echo " "
echo "Importing data..."
echo " "
python importer.py
echo "Data imported."
echo " "
exit