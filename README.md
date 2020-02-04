# simulatePortfolio

simulatePortfolio is a Python class that upon instantiation simulates performance of portfolio with **_stock instruments_**.

The main goal of this project is to provide basic metrics of **_long(er)-term investments_** based on the historical data and investment strategy.

## Features

- the simulator was developed for tracking **_long(er)-term investments_** with the time horizon of at least several months

- the simulator implements **_initial_** and **_monthly contributions_** and two kinds of instrument purchases:
  - **_initial purchase_**: of all instruments during the start date
  - **_regular purchases_**: of defined number of instruments at defined monthly intervals.
 
- the simulator acknowledges commission scheme typical for brokerage services:
  - **_absolute fee_**: absolute fee during purchase of one instrument
  - **_relative fee_**: fraction of purchased volume during purchase of one instrument
  - **_connection fee_**: absolute fee per calendar year
 
- it is necessary to define **_instrument weights_** in portfolio.\
The instrument weights are aimed to be preserved during simulation by regular solving of this SOE:\
\
![](https://latex.codecogs.com/gif.latex?\mathrm{weight}_i&space;=&space;\frac{\left(\mathrm{noShares}_{i0}&space;&plus;&space;\mathrm{noShares}_i\right&space;)\cdot&space;\mathrm{price}_i}{\sum_{N}^{&space;}\left(\mathrm{noShares}_{j0}&space;&plus;&space;\mathrm{noShares}_j\right&space;)\cdot&space;\mathrm{price}_j},i=1,...,N)\
\
![](https://latex.codecogs.com/gif.latex?\mathrm{regularInv.}&space;=&space;\sum_N^{&space;}\mathrm{noShares}_j\cdot&space;\mathrm{price}_j\cdot&space;\left(1&plus;\mathrm{relFee}_j&space;\right&space;)&space;\&space;&plus;&space;\&space;\mathrm{absFee}_j,&space;j&space;=&space;1,...,N)

- resulting stats are plotted when the simulation finish:
  - _equity and investment curves, return over investment_
  - _remaining cash after each purchase_
  - _total fees / investment percentage_
  - _instrument weights in portfolio after each purchase_

## Usage

```python
import datetime
from sp import simulatePortfolio

iSharesSP500 = {'name' : 'iShares SP500', 'data' : {datetime.date(2015, 1, 1): 158.93, datetime.date(2015, 2, 1): 160.48, datetime.date(2015, 3, 1): 163.74, datetime.date(2015, 4, 1): 167.06, datetime.date(2015, 5, 1): 166.15, datetime.date(2015, 6, 1): 163.35, datetime.date(2015, 7, 1): 163.69, datetime.date(2015, 8, 1): 161.68, datetime.date(2015, 9, 1): 162.54}}
XetraGold = {'name' : 'Xetra Gold', 'data' : {datetime.date(2015, 1, 20): 35.76, datetime.date(2015, 1, 21): 35.94, datetime.date(2015, 1, 22): 36.17, datetime.date(2015, 1, 23): 36.88, datetime.date(2015, 1, 26): 36.69, datetime.date(2015, 1, 27): 36.53, datetime.date(2015, 1, 28): 36.52, datetime.date(2015, 1, 29): 36.17, datetime.date(2015, 1, 30): 36.08}}

simulatePortfolio([[iSharesSP500, 0.7, 2.0, 0.00038],
                   [XetraGold, 0.3, 2.0, 0.00038]],
                  currency = 'EUR',
                  startDate = datetime.date(2015, 2, 3),
                  endDate = datetime.date(2019, 12, 30),
                  connectionFeePerYear = 2.5,
                  initCont = 2500,
                  monthCont = 120,
                  monthsPerTrade = 4,
                  instrumentsPerTrade = 1)
```

#### 1. Portfolio

```python
[[iSharesSP500, 0.7, 2.0, 0.00038],
 [XetraGold, 0.3, 2.0, 0.00038]]
```

Portfolio is `list` of some instruments.\
Each instrument takes the form `[historical data, weight, absolute fee, relative fee]`

#### 2. Historical data

```python
instrA = {'name' : 'iShares SP500', 'data' : {datetime.date(2015, 1, 1): 158.93, datetime.date(2015, 2, 1): 160.48, datetime.date(2015, 3, 1): 163.74, datetime.date(2015, 4, 1): 167.06, datetime.date(2015, 5, 1): 166.15, datetime.date(2015, 6, 1): 163.35, datetime.date(2015, 7, 1): 163.69, datetime.date(2015, 8, 1): 161.68, datetime.date(2015, 9, 1): 162.54}}
instrB = {'name' : 'Xetra Gold', 'data' : {datetime.date(2015, 1, 20): 35.76, datetime.date(2015, 1, 21): 35.94, datetime.date(2015, 1, 22): 36.17, datetime.date(2015, 1, 23): 36.88, datetime.date(2015, 1, 26): 36.69, datetime.date(2015, 1, 27): 36.53, datetime.date(2015, 1, 28): 36.52, datetime.date(2015, 1, 29): 36.17, datetime.date(2015, 1, 30): 36.08}}
```

Historical data are nested `dict` with `name` and `data` keys.\
The actual data points consist of `datetime.date` objects coupled with instrument prices per share.
- It is possible to load **daily** or **monthly** prices
- Monthly prices should be coupled to the same day in month for all instruments (e.g. all prices are defined on the _1st day of month_)

#### 3. Currency

Currency symbol for informative purposes.

#### 4. Start, end date

`datetime.date` objects defining simulation timespan.

#### 5. Connection fee

Absolute fee per calendar year.

#### 6. Initial and monhtly contributions

Contributed amount for initial and regular investments, respectively.

#### 7. Months per trade

How many months should be between regular investments.

#### 8. Instrument per trade

How many instruments should be traded during regular investments.

## Example

