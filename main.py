import sqlite3
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster

def loadData(dataFiles):

    """
    Load json files into sqlite database
    
    Parameters: 
        jsonFiles (list): list of file's name
    """

    for file in dataFiles:
        if file.split(".")[-1] == 'json':
            tableName = "trips{}".format(file.split('-')[4]) # "trips"+Year of file data
            data = [json.loads(line) for line in open(file, 'r')]
            df = pd.DataFrame(data)
        if file.split(".")[-1] == 'csv':
            tableName = file.split('-')[1]
            df = pd.read_csv(file)
                
        cursor.execute("DROP TABLE IF EXISTS {}".format(tableName))
        df.to_sql(tableName, conn)
        print("{} created succesfully".format(tableName))

def question1():

    query1 = '''
    SELECT * FROM 
    (SELECT * FROM trips2009
    UNION ALL
    SELECT * FROM trips2010
    UNION ALL
    SELECT * FROM trips2011
    UNION ALL
    SELECT * FROM trips2012
    ) WHERE trip_distance > 0
    '''

    cursor.execute(query1)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    df.to_csv('alltrips.csv', encoding='utf-8', index=False)

    df = pd.read_csv('alltrips.csv')
    df = df[(df.passenger_count<=2) & (df.passenger_count>0) & (df.trip_distance>0)]
    df['pickup_datetime'] = df['pickup_datetime'].astype('datetime64[ns]')
    df['pickup_year'] = df['pickup_datetime'].dt.year

    year2009 = df.trip_distance[df.pickup_year==2009]
    year2010 = df.trip_distance[df.pickup_year==2010]
    year2011 = df.trip_distance[df.pickup_year==2011]
    year2012 = df.trip_distance[df.pickup_year==2012]

    data = [year2009, year2010, year2011, year2012]
    label = ['2009', '2010', '2011', '2012']
 
    fig = plt.figure()
    plt.boxplot(data, showmeans=True, labels=label, whis=0.75)
    plt.ylabel('distância')
    plt.xlabel('ano')
    plt.show()

def question2():

    query2 = '''
    SELECT name AS Vendor, Total FROM (SELECT vendor_id, SUM(total_amount) AS Total FROM
    (SELECT vendor_id, total_amount, trip_distance, passenger_count FROM trips2009
    UNION ALL
    SELECT vendor_id, total_amount, trip_distance, passenger_count FROM trips2010
    UNION ALL
    SELECT vendor_id, total_amount, trip_distance, passenger_count FROM trips2011
    UNION ALL
    SELECT vendor_id, total_amount, trip_distance, passenger_count FROM trips2012) 
    GROUP BY vendor_id 
    ORDER BY Total DESC
    LIMIT 3) as temp_table
    INNER JOIN vendor_lookup 
    ON temp_table.vendor_id = vendor_lookup.vendor_id
    '''

    cursor.execute(query2)
    topVendors = cursor.fetchall()
    print(topVendors)

    def func(pct, allvalues):
        absolute = pct / 100.*np.sum(allvalues)
        return "{:.1f}%\n(U$ {:.2f})".format(pct, absolute)

    fig, ax = plt.subplots()
    vendors = [i[0] for i in topVendors]
    total = [i[1] for i in topVendors]
    wedges, texts, autotexts = ax.pie(total, labels=vendors, autopct=lambda pct: func(pct, total))
    plt.setp(autotexts, size = 8)
    ax.set_title("Top 3 Vendor's Revenue")
    plt.show()

def question3():

    query3 = '''
    SELECT pickup_datetime, total_amount FROM
    (SELECT pickup_datetime, payment_type, total_amount FROM trips2009
    UNION ALL
    SELECT pickup_datetime, payment_type, total_amount FROM trips2010
    UNION ALL
    SELECT pickup_datetime, payment_type, total_amount FROM trips2011
    UNION ALL
    SELECT pickup_datetime, payment_type, total_amount FROM trips2012) AS temp_table
    INNER JOIN payment_lookup
    ON temp_table.payment_type = payment_lookup.A
    WHERE B = 'Cash'
    '''

    cursor.execute(query3)
    data = cursor.fetchall()
    # Create DataFrame
    df = pd.DataFrame(data, columns=['pickup_datetime', 'total_amount'])
    # Transform column to datetime
    df['pickup_datetime'] = df['pickup_datetime'].astype('datetime64[ns]')
    # Create month column
    df['pickup_month'] = df['pickup_datetime'].dt.month
    # Create year column
    df['pickup_year'] = df['pickup_datetime'].dt.year
    new_df = df.pivot_table(index='pickup_month', columns='pickup_year', values='total_amount', aggfunc='count')

    new_df.plot(kind='bar')
    plt.legend(loc='upper right')
    plt.xlabel("Mês")
    plt.ylabel("Corridas")
    labels=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    plt.xticks(np.arange(0,12), labels, rotation ='horizontal')

    plt.show()

def question4():

    query4 = '''
    SELECT * FROM trips2012
    WHERE tip_amount <> 0 AND passenger_count <> 0 AND pickup_datetime LIKE '2012-10%' OR
    pickup_datetime LIKE '2012-11%' OR pickup_datetime LIKE '2012-12%'
    '''

    cursor.execute(query4)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    df['pickup_datetime'] = df['pickup_datetime'].astype('datetime64[ns]')
    new_df = (pd.to_datetime(df['pickup_datetime'])
       .dt.floor('d')
       .value_counts()
       .rename_axis('data')
       .reset_index(name='gorjetas'))
    new_df.set_index('data', inplace=True)

    new_df.plot(legend=False)
    plt.xlabel('Data')
    plt.ylabel('Gorjetas')
    plt.show()

def question5():

    df = pd.read_csv('alltrips.csv')

    df['pickup_datetime'] = df['pickup_datetime'].astype('datetime64[ns]')
    df['dropoff_datetime'] = df['dropoff_datetime'].astype('datetime64[ns]')
    df['weekday'] = df['pickup_datetime'].dt.dayofweek
    df['Ano'] = df['pickup_datetime'].dt.year
    df['trip_time'] = df['dropoff_datetime']-df['pickup_datetime']
    # Convert from nanosecond to minute
    df["trip_time"] = pd.to_numeric(df["trip_time"], downcast="float")*1.6667*10**-11
    new_df = df.pivot_table(index='weekday', columns='Ano', values='trip_time', aggfunc=np.mean)
    
    new_df.plot()
    labels = ['Seg','Ter','Qua','Qui','Sex','Sab','Dom']
    plt.xticks(np.arange(0,7), labels, rotation ='horizontal')
    plt.xlabel('Dia da semana')
    plt.ylabel('Tempo médio de viagem [min]')
    plt.show()

def question6():

    query6 = '''
    SELECT pickup_latitude, pickup_longitude FROM
    trips2010
    '''

    query7 = '''
    SELECT dropoff_latitude , dropoff_longitude FROM
    trips2010
    '''

    columns=['lat','lon']

    cursor.execute(query6)
    data = cursor.fetchall()
    df_pickup = pd.DataFrame(data, columns=columns)
    new_df_pickup = df_pickup.drop_duplicates()
    
    cursor.execute(query7)
    data = cursor.fetchall()
    df_dropoff = pd.DataFrame(data, columns=columns)
    new_df_dropoff = df_dropoff.drop_duplicates()
    
    result = new_df_pickup.merge(new_df_dropoff, on=['lat','lon'])
    print(result.head())

    result.plot()
    plt.xlabel('conjunto de coordenadas')
    plt.ylabel('posição [°]')
    plt.show()

    m = folium.Map(location=[40.771651,-73.973134], tiles='OpenStreetMap')
    markerCluster = MarkerCluster().add_to(m)

    for i, row in result.iterrows():
        lat = result.at[i, 'lat']
        lon = result.at[i, 'lon']

        folium.Marker(location=[lat, lon]).add_to(markerCluster)

    m.save('index.html')

# ------------------------------------------------------- #
# Main Function
# ------------------------------------------------------- #

if __name__ == '__main__':

    plt.style.use('ggplot')

    conn = sqlite3.connect('nyctaxitrips.db') # Create database if it doesn't exist
    cursor = conn.cursor()

    # Load files into DataBase
    files = ["data-sample_data-nyctaxi-trips-2009-json_corrigido.json", 
    "data-sample_data-nyctaxi-trips-2010-json_corrigido.json",
    "data-sample_data-nyctaxi-trips-2011-json_corrigido.json",
    "data-sample_data-nyctaxi-trips-2012-json_corrigido.json",
    "data-payment_lookup-csv.csv", "data-vendor_lookup-csv.csv"]

    # ------------ Execução das rotinas ------------ #

    # Criação do banco de dados
    #loadData(files)

    # Módulo das respostas
    # question1()
    # question2()
    # question3()
    # question4()
    # question5()
    # question6()

    conn.close()