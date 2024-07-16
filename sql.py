import sqlite3

## Connect to sqlite
connection=sqlite3.connect("EMPLOYEE.db")

## create a cursor object to insert record,create table,retrieve
cursor=connection.cursor()

## create the table
table_info="""
Create table EMPLOYEE(NAME VARCHAR(25),CLASS VARCHAR(25),
SECTION VARCHAR(25),MARKS INT);

"""

cursor.execute(table_info)

## Insert Some more records
cursor.execute('''Insert Into EMPLOYEE values('Krish','Data Science','A',90)''')
cursor.execute('''Insert Into EMPLOYEE values('Sudhanshu','Data Science','B',100)''')
cursor.execute('''Insert Into EMPLOYEE values('Darius','Data Science','A',86)''')
cursor.execute('''Insert Into EMPLOYEE values('Vikash','DEVOPS','A',50)''')
cursor.execute('''Insert Into EMPLOYEE values('Dipesh','DEVOPS','A',35)''')

## Disspaly ALl the records

print("The isnerted records are")
data=cursor.execute('''Select * from EMPLOYEE''')
for row in data:
    print(row)


connection.commit()
connection.close()