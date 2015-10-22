#!bin/bash
# this will wipe out your existing database. Be careful.
# not working 10/17. Will want to come back to this -- maybe rewrite in python.

echo "Verifying prerequisites"
echo " "
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