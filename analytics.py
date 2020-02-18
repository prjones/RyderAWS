import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame, Series 
import psycopg2
conn = psycopg2.connect(host="ec2-174-129-214-193.compute-1.amazonaws.com",database="d245l8lq8fvt3k", user="jptsqrcgcolpzw", password="68ba5ad64cadf6d0b7f387da474436dfbd3dca326fd914db29d2b35a59690ef9", port="5432")
c = conn.cursor()

history = pd.read_sql_query("SELECT * FROM scooterhistory", conn)
df = DataFrame(history)
decision = input("Enter a number 1-3: ")
def lists(value):
    print(df.head(5))
    print(df[value].value_counts().head(50))
def bar(value):
    fig = plt.figure(figsize = (8,12))
    x =df[value].value_counts().head(50)
    x.transpose()
    x.plot.bar()
    plt.savefig("bar.png")
def scatter(value, value2):
    fig = plt.figure(figsize = (12,8))
    plt.scatter(df[value],df[value2])
    plt.savefig("scatter.png")
if int(decision) == 1: #table
    print(df.columns.values)
    want = input("Enter column heading: ")
    lists(want)
if int(decision) == 2: #bar chart
    print(df.columns.values)
    print(history)
    print(df)
    want = input("Enter column heading: ")
    bar(str(want))
if int(decision) == 3: #scatter chart
    print(df.columns.values)
    want = input("Enter column heading: ")
    want2 = input("Enter second column heading: ")
    scatter(str(want),str(want2))