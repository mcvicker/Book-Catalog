##############################################################################
### Book Catalog Set-up file                                               ###
### Written by Daniel McVicker                                             ###
### danielmcvicker@gmail.com                                               ###
### last update 11/22/2015                                                 ### 
### This simplifies and streamlines dependency checks, and runs the        ###
### database_setup.py and importer.py files in the proper sequence, then   ###
### automatically starts the web services for you.                         ###
##############################################################################


import os
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

print "Checking dependencies... "
print " "
dependencies = []
with open("requirements.txt") as f:
    for item in f:
        item = item.strip('\n')
        dependencies.append(item)
print dependencies 

pkg_resources.require(item)
# note that pip may see a package as being installed that the pkg_resources
# manager doesn't see. if a dependency is not met, a DistributionNotFound 
# or VersionConflict exception is thrown. Run (sudo) pip install $package 
# until dependency checking finishes without error.

print " "
print "All dependencies met."
print " "
print "Removing existing database."
print " "
database="bookcatalog.db"
if os.path.isfile(database):
    os.remove(database)
    print("Deleting %s database.") % database
else:
    print("%s database not found.") % database
print " "
print "Creating book database..."
print " "
os.system("python database_setup.py")
print " "
print "Book database created or recreated."
print " "
print "Importing data..."
print " "
os.system("python importer.py")
print "Data imported."
print " "
print "Starting web services. Press ctrl + c to terminate."
print "Point your browser to http://localhost:8000 to explore. "
print " "
os.system("python catalog.py")