from ib_async import *
import pandas as pd
import plotly.express as px

price_list = [] 
contract_list = []
# Create an IB object and connect to TWS or Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

vix_index = Contract()
vix_index.secType = 'IND'
vix_index.symbol = 'VIX'
vix_index.currency = 'USD'
vix_index.exchange = 'CBOE'
eredmeny = ib.qualifyContracts(vix_index)
print(eredmeny)

data = ib.reqHistoricalData(
    vix_index,
    endDateTime='',
    durationStr='1 D',
    barSizeSetting='1 day',
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1
)
print(data)

# Convert the data to a Pandas DataFrame
data_df = pd.DataFrame(data)
# Get the last row of data using the tail() method
last_row = data_df.tail(1)

# Access the close field from the last row to get the last price
last_price_vix = last_row['close']
last_price_vix_value = last_price_vix.values
print('VIX')
print(type(int(last_price_vix_value)))
print(last_price_vix_value[0])

# Define a list of expiry dates for the next 12 months
expiry_dates = ['202301', '202302', '202303', '202304', '202305', '202306',
                '202307', '202308']

# Loop over the expiry dates and add them to the contract
for expiry_date in expiry_dates:
    fut_contract = Contract()
    fut_contract.secType = 'FUT'
    fut_contract.exchange = 'CFE'
    fut_contract.currency = 'USD'
    fut_contract.symbol = 'VIX'
    fut_contract.tradingClass = 'VX'
    fut_contract.lastTradeDateOrContractMonth = expiry_date
    ib.qualifyContracts(fut_contract)
    print(expiry_date, fut_contract.localSymbol)
    contract_list.append(fut_contract.localSymbol)

    ## Request real-time market data for the contract
    ib.reqMktData(fut_contract, '', False, False)
    # Print the last price for the contract
    print(expiry_date, ib.ticker(fut_contract).last)
   
    # Request historical data for the contract
    data = ib.reqHistoricalData(
        fut_contract,
        endDateTime='',
        durationStr='1 D',
        barSizeSetting='1 day',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1
    )
    # Convert the data to a Pandas DataFrame
    data_df = pd.DataFrame(data)
    # Get the last row of data using the tail() method
    last_row = data_df.tail(1)

    # Access the close field from the last row to get the last price
    last_price = last_row['close']
    last_price_value = last_price.values
    price_list.append(last_price_value[0])
    print(last_price_value)

i=0

for list in contract_list:
    print(f'Contract Symbol: {contract_list[i]}')
    print(f'Price: {price_list[i]}')
    i = i + 1 


# Create the chart using the px.line() function
fig = px.line(x=contract_list, y=price_list)

# Add a horizontal line at the value of the VIX index
fig.add_shape(
    type='line',
    x0=0,
    x1=1,
    y0=int(last_price_vix_value[0]),
    y1=int(last_price_vix_value[0]),
    xref='paper',
    yref='y',
    line=dict(color='red', dash='dash')
)

# Add a label to the horizontal line
fig.add_annotation(
    x=0.5,
    y=last_price_vix_value,
    xref='paper',
    yref='y',
    text="VIX Index: {}".format(last_price_vix_value[0]),
    font=dict(color='red'),
    showarrow=False
)
# Set the y-axis limits to include the value of the VIX index
fig.update_yaxes(range=[int(last_price_vix_value[0]) - 1, max(price_list)+1])

# Update the layout to add labels and a title
fig.update_layout(
    title="VIX Futures",
    xaxis_title="Symbol",
    yaxis_title="Volatility"
)

# Show the chart
fig.show()
