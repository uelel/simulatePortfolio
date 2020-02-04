![](logo.png)

# simulatePortfolio

simulatePortfolio is a Python class that upon instantiation simulates performance of portfolio with **_stock instruments_**.

The main goal of this project is to provide basic metrics of **_long(er)-term investments_** based on the historical data and investment strategy.

___

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
The instrument weights are aimed to be preserved during simulation by solving of this SOE regularly:\
\
![](https://latex.codecogs.com/gif.latex?\mathrm{weight}_i&space;=&space;\frac{\left(\mathrm{noShares}_{i0}&space;&plus;&space;\mathrm{noShares}_i\right&space;)\cdot&space;\mathrm{price}_i}{\sum_{N}^{&space;}\left(\mathrm{noShares}_{j0}&space;&plus;&space;\mathrm{noShares}_j\right&space;)\cdot&space;\mathrm{price}_j},i=1,...,N)\
\
![](https://latex.codecogs.com/gif.latex?\mathrm{regularInv.}&space;=&space;\sum_N^{&space;}\mathrm{noShares}_j\cdot&space;\mathrm{price}_j\cdot&space;\left(1&plus;\mathrm{relFee}_j&space;\right&space;)&space;\&space;&plus;&space;\&space;\mathrm{absFee}_j,&space;j&space;=&space;1,...,N)

- resulting stats are plotted when the simulation finish:
  - _equity and investment curves, return over investment_
  - _remaining cash after each purchase_
  - _total fees / investment percentage_
  - _instrument weights in portfolio after each purchase_

___

## Usage

```python
import datetime
from sp import simulatePortfolio

inst1 = {'name':'iShares S&P500', 'data':{datetime.date(2019, 1, 1): 259.05, datetime.date(2019, 2, 1): 276.162, datetime.date(2019, 3, 1): 282.065, datetime.date(2019, 4, 1): 291.348, datetime.date(2019, 5, 1): 287.017, datetime.date(2019, 6, 1): 286.0, datetime.date(2019, 7, 1): 299.4, datetime.date(2019, 8, 1): 294.882, datetime.date(2019, 9, 1): 296.533, datetime.date(2019, 10, 1): 299.253, datetime.date(2019, 11, 1): 311.615, datetime.date(2019, 12, 1): 318.435, datetime.date(2020, 1, 1): 326.11, datetime.date(2020, 2, 1): 325.68}}
inst2 = {'name':'Xetra Gold', 'data': {datetime.date(2019, 1, 1): 36.24, datetime.date(2019, 2, 1): 36.99, datetime.date(2019, 3, 1): 36.92, datetime.date(2019, 4, 1): 36.99, datetime.date(2019, 5, 1): 36.49, datetime.date(2019, 6, 1): 37.8, datetime.date(2019, 7, 1): 39.44, datetime.date(2019, 8, 1): 41.02, datetime.date(2019, 9, 1): 44.66, datetime.date(2019, 10, 1): 43.42, datetime.date(2019, 11, 1): 43.55, datetime.date(2019, 12, 1): 42.53, datetime.date(2020, 1, 1):44.03, datetime.date(2020, 2, 1):45.85}}

simulatePortfolio([[inst1, 0.8, 2.0, 0.00038],
                   [inst2, 0.2, 2.0, 0.00038]],
                  currency = 'EUR',
                  connectionFeePerYear = 2.5,
                  startDate = datetime.date(2019, 1, 1),
                  endDate = datetime.date(2020, 1, 1),
                  initCont = 2500,
                  monthCont = 200,
                  monthsPerTrade = 2,
                  instrumentsPerTrade = 2)
```

#### 1. Historical data

```python
inst1 = {'name':'iShares S&P500', 'data':{datetime.date(2019, 1, 1): 259.05, datetime.date(2019, 2, 1): 276.162, datetime.date(2019, 3, 1): 282.065, datetime.date(2019, 4, 1): 291.348, datetime.date(2019, 5, 1): 287.017, datetime.date(2019, 6, 1): 286.0, datetime.date(2019, 7, 1): 299.4, datetime.date(2019, 8, 1): 294.882, datetime.date(2019, 9, 1): 296.533, datetime.date(2019, 10, 1): 299.253, datetime.date(2019, 11, 1): 311.615, datetime.date(2019, 12, 1): 318.435, datetime.date(2020, 1, 1): 326.11, datetime.date(2020, 2, 1): 325.68}}
inst2 = {'name':'Xetra Gold', 'data': {datetime.date(2019, 1, 1): 36.24, datetime.date(2019, 2, 1): 36.99, datetime.date(2019, 3, 1): 36.92, datetime.date(2019, 4, 1): 36.99, datetime.date(2019, 5, 1): 36.49, datetime.date(2019, 6, 1): 37.8, datetime.date(2019, 7, 1): 39.44, datetime.date(2019, 8, 1): 41.02, datetime.date(2019, 9, 1): 44.66, datetime.date(2019, 10, 1): 43.42, datetime.date(2019, 11, 1): 43.55, datetime.date(2019, 12, 1): 42.53, datetime.date(2020, 1, 1):44.03, datetime.date(2020, 2, 1):45.85}}
```

Historical data are nested `dict` with `name` and `data` keys.\
The actual data points consist of `datetime.date` objects coupled with instrument prices per share.
- It is possible to load **daily** or **monthly** prices
- Monthly prices should be coupled to the same day in month for all instruments (e.g. all prices are defined on the _1st day of month_)

#### 2. Portfolio

```python
[[inst1, 0.8, 2.0, 0.00038],
 [inst2, 0.2, 2.0, 0.00038]]
```

Portfolio is `list` of some instruments.\
Each instrument takes the form `[historical data, weight, absolute fee, relative fee]`

#### 3. Currency

```python
currency = 'EUR'
```

Currency symbol for informative purposes.

#### 4. Start, end date

```python
startDate = datetime.date(2019, 1, 1),
endDate = datetime.date(2020, 1, 1)
```

`datetime.date` objects defining simulation timespan.

#### 5. Connection fee

```python
connectionFeePerYear = 2.5
```

Absolute fee per calendar year.

#### 6. Initial and monhtly contributions

```python
initCont = 2500,
monthCont = 200
```

Contributed amount for initial and regular investments, respectively.

#### 7. Months per trade

```python
monthsPerTrade = 2
```

How many months should be between regular investments.

#### 8. Instruments per trade

```python
instrumentsPerTrade = 1
```

How many instruments should be traded during regular investments.

___

## Example

from the previous code:

![](plot.png)

___

## Known issues

- plots may be distrorted when plotted from terminal.\
  Use `jupyter notebook` or different `matplotlib` backend.
