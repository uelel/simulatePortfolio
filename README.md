# simulatePortfolio

simulatePortfolio is a Python class that upon instantiation simulates performance of portfolio with **_stock instruments_**.

The main goal of this project is to provide basic metrics of **_long(er)-term investments_** based on the historical data and investment strategy.

## Features

- the class was developed for tracking **_long(er)-term investments_** with the time horizon at least several months

- the class implements two kinds of instrument purchases:
  - **_initial purchase_**: of all instruments during the start date
  - **_regular purchases_**: of defined number of instruments at the defined monthly intervals. 
  

## Usage

```python
import datetime
from sp import simulatePortfolio

simulatePortfolio([[iSharesSP500EUR, 0.8, 2.0, 0.00038],
                   [XetraGoldEUR, 0.2, 2.0, 0.00038]],
                  currency = 'EUR',
                  tradingFeePerYear = 2.5,
                  startDate = datetime.date(2015, 2, 3),
                  endDate = datetime.date(2019, 12, 30),
                  startInvEur = 2500,
                  monthInvEur = 120,
                  monthsPerTrade = 4,
                  instrumentsPerTrade = 1,
                  preserveWeights = True)
```

### Historical data

Historical data are provided in a form of **_nested dictionaries_** with `name` and `data` keys. The actual data points consist of `datetime.date` objects coupled with instrument prices:

```python
instrA = {'name' : 'iShares SP500', 'data' : {datetime.date(2015, 1, 1): 158.93, datetime.date(2015, 2, 1): 160.48, datetime.date(2015, 3, 1): 163.74, datetime.date(2015, 4, 1): 167.06, datetime.date(2015, 5, 1): 166.15, datetime.date(2015, 6, 1): 163.35, datetime.date(2015, 7, 1): 163.69, datetime.date(2015, 8, 1): 161.68, datetime.date(2015, 9, 1): 162.54}}
instrB = {'name' : 'Xetra Gold', 'data' : {datetime.date(2015, 1, 20): 35.76, datetime.date(2015, 1, 21): 35.94, datetime.date(2015, 1, 22): 36.17, datetime.date(2015, 1, 23): 36.88, datetime.date(2015, 1, 26): 36.69, datetime.date(2015, 1, 27): 36.53, datetime.date(2015, 1, 28): 36.52, datetime.date(2015, 1, 29): 36.17, datetime.date(2015, 1, 30): 36.08}}
```

### Input parameters

#### 1. Portfolio

### Example

