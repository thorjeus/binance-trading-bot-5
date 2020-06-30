import  backtrader as bt
import datetime
from backtrader.indicators import ExponentialMovingAverage, CrossOver, BBands

class GoldenCross(bt.Strategy):

    params = dict (
        ema = ExponentialMovingAverage,
        cross = CrossOver,
        period1 = 7,
        period2 = 30,
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), txt))

    def __init__(self):
        self.ema1 = self.p.ema(period=self.p.period1)
        self.ema2 = self.p.ema(period=self.p.period2)
        self.cross = self.p.cross(self.ema1, self.ema2)

        self.startcash = self.broker.getvalue()
        self.long = False
        self.order = None
        self.first_position = True

        self.num_long_trades = 0
        self.num_short_trades = 0
    '''
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
    '''
    def next(self):
        position_size = (self.env.broker.getcash()*0.8)/self.data.close
        if self.cross > 0:
            self.close()
            self.buy(size=position_size)
            # self.log('BUY CREATE, %.2f' % self.data.close[0])
            self.num_long_trades += 1
        elif self.cross < 0:
            self.close()
            self.sell(size=position_size)
            self.num_short_trades += 1
            # self.log('SELL CREATE, %.2f' % self.data.close[0])

    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash,2)
        print(f'EMA Period: [{self.p.period1}, {self.p.period2}] Final PnL: {pnl} Long/Short trades: [{self.num_long_trades}, {self.num_short_trades}]')

class TrailCross(bt.Strategy):

    params = dict (
        ema = ExponentialMovingAverage,
        cross = bt.indicators.CrossOver,

        period1 = 7,
        period2 = 30,
        
        stop_type = bt.Order.StopTrail,
        
        is_percent = False,
        
        tp_percent = 0.03,
        sl_percent = 0.01,
        
        tp_amount = 4.0,
        sl_amount = 1.5,
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.strftime('%Y-%m-%d %H:%M:%S'), txt))

    def __init__(self):
        self.ema1 = self.p.ema(period=self.p.period1)
        self.ema2 = self.p.ema(period=self.p.period2)
        self.cross = self.p.cross(self.ema1, self.ema2)

        self.startcash = self.broker.getvalue()
        self.order = None

        self.position_price = 0.0
        self.position_is_buy = True
    '''
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
    '''
    def next(self):
        position_size = (self.env.broker.getcash()*0.5)/self.data.close
        
        if not self.position:
            if self.cross > 0:
                self.buy(size=position_size)

                self.position_price = self.data.close[0]
                self.position_is_buy = True
                # self.log('BUY CREATE, %.2f' % self.data.close[0])
            elif self.cross < 0:
                self.sell(size=position_size)

                self.position_price = self.data.close[0]
                self.position_is_buy = False
                # self.log('SELL CREATE, %.2f' % self.data.close[0])
        else:
            if self.p.is_percent:
                if self.position_is_buy:
                    if self.data.close[0] >= self.position_price + self.position_price * self.p.tp_percent or self.data.close[0] <= self.position_price - self.position_price * self.p.sl_percent:
                        self.close()
                else:
                    if self.data.close[0] <= self.position_price - self.position_price * self.p.tp_percent or self.data.close[0] >= self.position_price + self.position_price * self.p.sl_percent:
                        self.close()
            else:
                if self.position_is_buy:
                    if self.data.close[0] >= self.position_price + self.p.tp_amount or self.data.close[0] <= self.position_price - self.p.sl_amount:
                        self.close()
                else:
                    if self.data.close[0] <= self.position_price - self.p.tp_amount or self.data.close[0] >= self.position_price +  self.p.sl_amount:
                        self.close()


    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash,2)
        print(f'EMA Period: [{self.p.period1}, {self.p.period2}] Final PnL: {pnl}')

class BollingerBandsStrategy(bt.Strategy):

    params = dict(
        period = 20,
        devfactor = 2.0,
        distance = 2,
        stoploss = 2,
        cross = CrossOver
    )

    def __init__(self):
        self.bbands = BBands(period=self.p.period, devfactor=self.p.devfactor)
        self.startcash = self.broker.getvalue()

        self.cross = bt.indicators.CrossOver
        self.ema = bt.indicators.MovingAverageSimple(period=200)

        self.order = None

        self.crossup = self.p.cross(self.data.close, self.bbands.lines.bot)
        self.crossdown = self.p.cross(self.data.close, self.bbands.lines.top)
        self.crossema = self.p.cross(self.data.close, self.ema)

        self.close_to_top = False
        self.close_to_bottom = False

        self.num_long_trades = 0
        self.num_short_trades = 0
    '''
    def next(self):
        position_size = (self.env.broker.getcash()*0.8)/self.data.close
        distance = self.data.close[0]*self.p.distance

        if abs(self.data.close[0] - self.bbands.lines.top[0]) < self.p.distance and not self.close_to_top:
            self.close_to_top = True
            self.close_to_bottom = False
            if self.order is None and self.data.close[0] < self.ema[0]:
                self.order = self.sell(size=position_size)
                self.num_short_trades += 1
            elif self.order is not None:
                if self.order.isbuy():
                    self.close()
                    self.order = None
        elif abs(self.data.close[0] - self.bbands.lines.bot[0]) < self.p.distance and not self.close_to_bottom:
            self.close_to_bottom = True
            self.close_to_top = False
            if self.order is None and self.data.close[0] > self.ema[0]:
                self.order = self.buy(size=position_size)
                self.num_long_trades += 1
            elif self.order is not None:
                if self.order.issell():
                    self.close()
                    self.order = None
        
        if abs(self.data.close[0] - self.bbands.lines.mid[0]) < self.p.distance:
            self.close_to_bottom = False
            self.close_to_top = False

        if self.order is not None:
            if self.order.isbuy() and self.data.close[0] < (self.bbands.lines.bot[0]*(1+self.p.stoploss*0.01)):
                self.close()
                self.order = None
            elif self.order.issell() and self.data.close[0] > (self.bbands.lines.top[0]*(1-self.p.stoploss*0.01)):
                self.close()
                self.order = None
    '''
    def next(self):
        # Crossover with ema trend check
        position_size = (self.env.broker.getcash() * 0.9)/self.data.close

        if self.crossdown < 0:
            if self.order is None and self.data.close[0] < self.ema[0]*(1-self.p.distance*0.01):
                self.order = self.sell(size=position_size)
                self.num_short_trades += 1
            elif self.order is not None:
                if self.order.isbuy():
                    self.close()
                    self.order = None
        elif self.crossup > 0:
            if self.order is None and self.data.close[0] > self.ema[0]*(1+self.p.distance*0.01):
                self.order = self.buy(size=position_size)
                self.num_long_trades += 1
            elif self.order is not None:
                if self.order.issell():
                    self.close()
                    self.order = None
        elif self.order is not None:
            if self.order.isbuy() and (self.data.close[0] < (self.bbands.lines.bot[0]*(1-self.p.stoploss*0.01)) or self.crossema < 0):
                self.close()
                self.order = None
            elif self.order.issell() and (self.data.close[0] > (self.bbands.lines.top[0]*(1+self.p.stoploss*0.01)) or self.crossema > 0):
                self.close()
                self.order = None
    
    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash,2)
        print(f'BBands Period: {self.p.period} PnL: {pnl} Long/Short: [{self.num_long_trades}, {self.num_short_trades}]')

        