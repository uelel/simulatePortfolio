import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dts
import matplotlib.ticker as tck
import matplotlib.gridspec as grd
from scipy.optimize import root as solver
from scipy.optimize import curve_fit

class simulatePortfolio():

    def dayIter(self, startDate):
        """Iterator returning date object of every next day from startDate"""
        cnt = 0
        while True:
            day = startDate + datetime.timedelta(cnt)
            cnt += 1
            yield day

    def getFirstValidDay(self, startDate):
        """Function returning the very next date from startDate
           for which all instruments in portfolio provide prices"""
        dayGen = self.dayIter(startDate)
        loaded = False
        while not loaded:
            day = next(dayGen)
            for instr in self.portfolio:
                try:
                    price = instr[0]['data'][day]
                    loaded = True
                except KeyError:
                    loaded = False
                    break
        return day
            
    def monthIter(self, startDate, endDate):
        """Iterator returning date object of first day of every month
           between startDate and endDate"""
        """For each returned date all instruments in portfolio provide prices"""
        prevMonth = startDate.month
        validDay = self.getFirstValidDay(startDate)
        for n in range(int((endDate - startDate).days)):
            day = startDate + datetime.timedelta(n)
            if day <= validDay:
                continue
            validDay = self.getFirstValidDay(day)
            if validDay.month != prevMonth:
                yield validDay
            prevMonth = validDay.month

    def getFirstInstPointer(self):
        """Returns pointer to instrument with lowest weight"""
        portSorted = sorted(self.portfolio,key=lambda l:l[1])
        return self.portfolio.index(portSorted[0])
    
    def portIter(self):
        """Infinite iterator returning pointers to portfolio instruments"""
        """Iterator starts with lowest-weight instrument and continues to
           highest-weight instruments"""
        """When pointer=highest-weight instrument, iterator continues from
           lowest-weight instrument again"""
        pos = 0
        stop = len(self.portfolio) - 1
        portSorted = sorted(self.portfolio,key=lambda l:l[1])
        while True:
            yield self.portfolio.index(portSorted[pos])
            if pos < stop:
                pos += 1
            else:
                pos = 0

    def applyPurchase(self, pointer, day, initialInv=False):
        """Apply purchase of given instrument in portfolio"""
        """Apply commission scheme during purchase"""
        """Return updated noShares, cash and feesTotal"""
        price = self.portfolio[pointer][0]['data'][day]
        if initialInv:
            # Calculate available volume considering available investment
            # for instrument, relative fee and absolute fee
            availVol = (self.invAvailable - self.portfolio[pointer][2])/(1+self.portfolio[pointer][3])
            # Determine integer number of purchased shares
            noShares = int(availVol/price)
            if noShares <= 0:
                self.updatePlotArrays(day)
                return
            # Calculate unused investment after purchase considering
            # rounded noShares, relative fee and absolute fee
            #self.remainInvAfterPurchase = self.invAvailable - price*noShares - self.portfolio[pointer][2] - price*noShares*self.portfolio[pointer][3]
        else:
            # Get integer noShares from weightSharesArray
            noShares = int(self.weightSharesArray[pointer])
            # Adjust number of shares in case remainInvAfterPurchase is negative
            while self.cash < price*noShares + self.portfolio[pointer][2] + price*noShares*self.portfolio[pointer][3]:
                noShares -= 1
            # If calculated noShares is zero/negative, don't buy anything
            if noShares <= 0:
                self.updatePlotArrays(day)
                return
        # Update total investment
        self.invTotal += price*noShares + self.portfolio[pointer][2] + price*noShares*self.portfolio[pointer][3]
        # Subtract purchased volume from cash
        self.cash -= price*noShares
        # Update number of purchased instrument shares
        self.sharesArray[pointer] += noShares
        # Apply relative fee
        self.cash -= price*noShares*self.portfolio[pointer][3]
        self.feesTotal += price*noShares*self.portfolio[pointer][3]
        # Apply absolute fee
        self.cash -= self.portfolio[pointer][2]
        self.feesTotal += self.portfolio[pointer][2]
        # Update remaining investment after purchase
        if not initialInv:
            self.remainInvAfterPurchase = self.cash
        self.updatePlotArrays(day)

    def updatePlotArrays(self, day, final=False):
        """Update arrays for plotting"""
        equity = 0.0
        for i in range(len(self.portfolio)):
            equity += self.sharesArray[i]*self.portfolio[i][0]['data'][day]
        weights = np.empty(0, float)
        for i in range(len(self.portfolio)):
            if equity > 0:
                weights = np.append(weights, self.sharesArray[i]*self.portfolio[i][0]['data'][day]/equity)
            else:
                weights = np.append(weights, 0.0)
        if dts.date2num(day) in self.timeArray:
            self.equityArray[-1] = equity
            self.invArray[-1] = self.invTotal
            self.remainInvArray[-1] = self.remainInvAfterPurchase
            if self.invTotal > 0:
                self.percArray[-1] = (equity-self.invTotal)*100/self.invTotal
                self.feePercArray[-1] = self.feesTotal*100/self.invTotal
            else:
                self.percArray[-1] = 0.0
                self.feePercArray[-1] = 0.0
            self.weightArray[-1] = weights
        else:
            self.timeArray = np.append(self.timeArray, dts.date2num(day))
            self.equityArray = np.append(self.equityArray, equity)
            self.invArray = np.append(self.invArray, self.invTotal)
            self.remainInvArray = np.append(self.remainInvArray, self.remainInvAfterPurchase)
            if self.invTotal > 0:
                self.percArray = np.append(self.percArray, (equity-self.invTotal)*100/self.invTotal)
                self.feePercArray = np.append(self.feePercArray, self.feesTotal*100/self.invTotal)
            else:
                self.percArray = np.append(self.percArray, 0.0)
                self.feePercArray = np.append(self.feePercArray, 0.0)
            if final:
                self.weightArray = np.append(self.weightArray, [[0.0 for _ in range(len(self.portfolio))]], axis=0)
            else:
                self.weightArray = np.append(self.weightArray, [weights], axis=0)

    def calcWeightShares(self, day):
        """Solve system of equations and get number of shares for each intrument
           so that if every instrument is purchased at current price,
           its weight in portfolio is equal to the definition"""
        """w_i = (no0_i+no_i)*price_i/sum((no0_j+no_j)*price_j)
           inv = sum(no_j*price_j*(1+relfee_j) + absfee_j)"""
        # If no shares were purchased yet, equations do not converge
        # In that case determine noShares same way like during initial investment
        if all([True if noShares<=0 else False for noShares in self.sharesArray]):
            pointerIter = self.portIter()
            for _ in range(len(self.portfolio)):
                pointer = next(pointerIter)
                availVol = (self.invAvailable*self.portfolio[pointer][1] - self.portfolio[pointer][2])/(1+self.portfolio[pointer][3])
                self.weightSharesArray[pointer] = int(availVol/self.portfolio[pointer][0]['data'][day])
            return
        # Solve SOE
        def fun(*args):
            nonlocal day
            vol = 0.0
            for i in range(len(self.portfolio)):
                vol += (self.sharesArray[i]+args[0][i])*self.portfolio[i][0]['data'][day]
            out = list()
            for i in range(len(self.portfolio)):
                out.append(((self.sharesArray[i]+args[0][i])*self.portfolio[i][0]['data'][day]/vol) - self.portfolio[i][1])
            fourth = 0.0
            for i in range(len(self.portfolio)):
                fourth += args[0][i]*self.portfolio[i][0]['data'][day]*(1+self.portfolio[i][3]) + self.portfolio[i][2]
            fourth -= (self.invAvailable + self.remainInvAfterPurchase)
            out.append(fourth)
            return tuple(out)
        solution = solver(fun, tuple(0 for _ in range(len(self.portfolio))), method='lm')
        # Print warning in case solver did not find solution
        if any(np.isnan(solution['x'])):
            print('%s: Solver could not determine noShares to preserve weights!' % day.strftime('%d. %m. %Y'))
            pointerIter = self.portIter()
            for _ in range(len(self.portfolio)):
                pointer = next(pointerIter)
                self.weightSharesArray[pointer] = 0
        self.weightSharesArray = solution['x']

    def applyInitialInv(self):
        """Apply initial investment"""
        self.cash = self.initCont
        startDate = self.getFirstValidDay(self.startDate)
        pointerIter = self.portIter()
        for i in range(len(self.portfolio)):
            pointer = next(pointerIter)
            # Calculate available investment for instrument
            self.invAvailable = self.initCont*self.portfolio[pointer][1] + self.remainInvAfterPurchase
            # Apply purchase
            self.applyPurchase(pointer, startDate, initialInv=True)

    def applyRegularInv(self):
        """Apply investments at regular intervals"""
        monthsWithoutTrade = 0
        monthsRemainInYear = 12
        pointerIter = self.portIter()
        firstInstPointer = self.getFirstInstPointer()
        for day in self.monthIter(self.startDate, self.endDate):
            monthsWithoutTrade += 1
            if monthsRemainInYear == 0:
                monthsRemainInYear = 12
            self.cashTotal += self.monthCont
            self.cash += self.monthCont
            # Apply annual entry fee for stock exchanges
            if monthsRemainInYear == 12:
                self.cash -= self.connectionFeePerYear
                self.feesTotal += self.connectionFeePerYear
            monthsRemainInYear -= 1
            # In case of nontrading month, continue
            if monthsWithoutTrade < self.monthsPerTrade:
                continue
            # In case of trading month, apply purchase
            elif monthsWithoutTrade == self.monthsPerTrade:
                for _ in range(self.instrumentsPerTrade):
                    pointer = next(pointerIter)
                    # In case of new investment round, calculate number of shares for each
                    # intrument so that if every instrument is purchased at current price,
                    # its weight in portfolio is nearly equal to the definition
                    if pointer == firstInstPointer:
                        self.invAvailable = self.monthCont*self.monthsPerTrade*len(self.portfolio)/self.instrumentsPerTrade
                        self.calcWeightShares(day)
                    # Apply purchase
                    self.applyPurchase(pointer, day)
                    # Apply purchase so that maximal fraction of investment+remainInvAfterPurchase is used
                    #else:
                    #    # Calculate available investment for given instrument
                    #    self.invAvailable = (self.monthCont*self.monthsPerTrade*len(self.portfolio)*self.portfolio[pointer][1]/self.instrumentsPerTrade)+self.remainInvAfterPurchase
                    #    # Apply purchase
                    #    self.applyPurchase(pointer, day)
                monthsWithoutTrade = 0

    def plotStats(self):
        fig = plt.figure(figsize=(11,28))
        plt.ioff()
        grid = grd.GridSpec(5, 1, height_ratios=[7, 3, 3, 3, 7], hspace=0.35)
        
        # Plot equity curves
        plt1 = plt.subplot(grid[0])
        plt1.plot(self.timeArray, self.equityArray, label='Equity')
        plt1.plot(self.timeArray, self.invArray, label='Investment')
        plt1.xaxis.set_major_locator(dts.YearLocator())
        plt1.xaxis.set_minor_locator(dts.MonthLocator())
        plt1.xaxis.set_major_formatter(dts.DateFormatter('%m.%Y'))
        plt1.set_xlabel('Time')
        plt1.set_ylabel(self.currency)
        plt1.grid(which='major', axis='x', linestyle='--')
        plt1.set_title('Equity and investment curves')
        plt1.legend(loc='lower right')
        plt1.text(0.18, 0.9, 
                 s = 'Total investment = %.0f %s\nTotal equity = %.0f %s\n Final ROI = %.2f%%' % (self.invArray[-1], self.currency, self.equityArray[-1], self.currency, self.percArray[-1]),
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform = plt1.transAxes,
                 fontsize=12,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt2 = plt.subplot(grid[1])
        plt2.plot(self.timeArray, self.percArray, label='Equity/Investment', color='g')
        plt2.set_title('Equity / investment percentage')
        plt2.xaxis.set_major_locator(dts.YearLocator())
        plt2.xaxis.set_minor_locator(dts.MonthLocator())
        plt2.xaxis.set_major_formatter(dts.DateFormatter('%m.%Y'))
        plt2.yaxis.set_major_locator(tck.MultipleLocator(10))
        vals = plt2.get_yticks()
        plt2.set_yticklabels(['%.0f%%' % (x) for x in vals])
        plt2.yaxis.set_minor_locator(tck.MultipleLocator(5))
        plt2.grid(which='major', axis='both', linestyle='--')
        plt2.text(0.15, 0.85, 
                 s = 'Mean ROI = %.2f%% p.a.' % (self.meanReturn),
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform = plt2.transAxes,
                 fontsize=12,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        plt2.set_xlabel('Time')

        # Plot remaining cash after purchase
        plt3 = plt.subplot(grid[2])
        plt3.plot(self.timeArray, self.remainInvArray, color='r')
        plt3.xaxis.set_major_locator(dts.YearLocator())
        plt3.xaxis.set_minor_locator(dts.MonthLocator())
        plt3.xaxis.set_major_formatter(dts.DateFormatter('%m.%Y'))
        plt3.grid(which='major', axis='x', linestyle='--')
        plt3.set_xlabel('Time')
        plt3.set_ylabel(self.currency)
        plt3.set_title('Remaining cash after each purchase')

        # Plot fees/investment percentage
        plt4 = plt.subplot(grid[3])
        plt4.plot(self.timeArray, self.feePercArray, color='r')
        plt4.xaxis.set_major_locator(dts.YearLocator())
        plt4.xaxis.set_minor_locator(dts.MonthLocator())
        plt4.xaxis.set_major_formatter(dts.DateFormatter('%m.%Y'))
        vals = plt4.get_yticks()
        plt4.set_yticklabels(['%.2f%%' % (x) for x in vals])
        plt4.grid(which='major', axis='x', linestyle='--')
        plt4.set_xlabel('Time')
        plt4.set_ylabel('')
        plt4.set_title('Total fees / investment percentage after each purchase')

        # Plot instrument weights
        plt5 = plt.subplot(grid[4])
        barBottom = np.zeros(len(self.timeArray))
        hline = 0.0
        for i in range(len(self.portfolio)):
            plt5.bar(self.timeArray, self.weightArray[:,i], width=100, bottom=barBottom, label=self.portfolio[i][0]['name'])
            hline += self.portfolio[i][1]
            plt5.axhline(y=hline, linestyle='--', color='purple')
            np.add(barBottom, self.weightArray[:,i], out=barBottom)
        plt5.xaxis.set_major_locator(dts.YearLocator())
        plt5.xaxis.set_minor_locator(dts.MonthLocator())
        plt5.xaxis.set_major_formatter(dts.DateFormatter('%m.%Y'))
        plt5.yaxis.set_major_formatter(tck.FormatStrFormatter('%.2f'))
        plt5.yaxis.set_major_locator(tck.MultipleLocator(0.2))
        plt5.yaxis.set_minor_locator(tck.MultipleLocator(0.1))
        plt5.set_ylabel('')
        plt5.set_xlabel('Time')
        plt5.set_ylim((0,1))
        plt5.set_title('Instrument weights after each purchase')
        plt5.legend(bbox_to_anchor=(1.01, 1.0))
        
        plt.show(block=True)
    
    def __init__(self,
                 portfolio,
                 currency=None,
                 connectionFeePerYear=None,
                 startDate=None,
                 endDate=None,
                 initCont=None,
                 monthCont=None,
                 monthsPerTrade=None,
                 instrumentsPerTrade=None):
        self.portfolio = portfolio
        self.currency = currency
        self.connectionFeePerYear = connectionFeePerYear
        self.startDate = startDate
        self.endDate = endDate
        self.initCont = initCont
        self.monthCont = monthCont
        self.monthsPerTrade = monthsPerTrade
        self.instrumentsPerTrade = instrumentsPerTrade
        self.invAvailable = 0.0
        self.weightSharesArray = np.zeros(len(self.portfolio))
        self.sharesArray = np.zeros(len(self.portfolio))
        self.cashTotal = self.initCont
        self.invTotal = 0.0
        self.feesTotal = 0.0
        self.remainInvAfterPurchase = 0.0
        self.timeArray = np.empty(0, float)
        self.equityArray = np.empty(0, float)
        self.invArray = np.empty(0, float)
        self.percArray = np.empty(0, float)
        self.remainInvArray = np.empty(0, float)
        self.feePercArray = np.empty(0, float)
        self.weightArray = np.empty((0, len(self.portfolio)), float)
        # Apply initial investment
        self.applyInitialInv()
        # Apply regular investment
        self.applyRegularInv()
        # Update stats with final state
        self.updatePlotArrays(self.endDate, final=True)
        # Calculate mean annual return
        self.meanReturn = self.percArray[-1]/(((self.endDate - self.startDate).days)/365)
        # Plot stats
        self.plotStats()
