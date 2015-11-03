import unicodecsv as csv
# uses unicodecsv package because built-in csv package in python does not 
# support unicode, which is needed for the database
    
# we open up the .tsv file to get a selection of bindings.
# this also sets an allrows variable to get the length of the rows.

allrows = []
with open('My_Shelfari_Books.tsv','rb') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter=',')
    #print reader.fieldnames
    for row in reader:
        if row['Binding'] == '':
            allrows.append('Unknown Binding')
        else:
            allrows.append(row['Binding'])
    
      
bindings = set(allrows)

print bindings