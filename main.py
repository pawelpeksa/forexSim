import csv
import numpy as np
from hyperopt import fmin, tpe, space_eval, hp




def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def is_close_zero(a):
    return is_close(a, 0.0)
    

class Simulation(object):
    def __init__(self, data_file, credit, buy_threshold, sell_threshold):
        self.data_file = data_file
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

        self.rates = None
        self.pln_credit = credit
        self.eur_credit = 0.0
        self.reference_rate = 0.0
        self.current_rate = 0.0

    def read_data(self):
        with open(self.data_file) as f:
            reader = csv.reader(f)
            data = list(reader)

        npdata = np.array(data)
        self.rates = (npdata[:,0]).astype(float)
        self.reference_rate = self.rates[0]

    def simulate(self):
        for rate in self.rates:
            self.do_step(rate)

    def do_step(self, rate):
        self.current_rate = rate

        if self.should_buy():
            self.buy()
        elif self.should_sell():
            self.sell()

    def buy(self):
        buy_rate = self.current_rate * 1.00354 # 1.00354 - buy spread
        self.reference_rate = self.current_rate

        self.get_provision()

        self.eur_credit = (self.pln_credit) * (1.0/buy_rate)
        self.pln_credit = 0.0

    def sell(self):
        sell_rate = self.current_rate * 0.996403 # 0.996403 - sell spread
        self.reference_rate = self.current_rate

        self.pln_credit = (self.eur_credit * sell_rate)
        self.eur_credit = 0.0

        self.get_provision()

    def get_provision(self):
        provision = 2.0
        if self.pln_credit < provision:
            raise RuntimeError("No plns to get provision")
            
        self.pln_credit -= provision

    def should_buy(self):
        diff = self.current_rate - self.reference_rate
        return is_close_zero(self.eur_credit) and diff/self.reference_rate < self.buy_threshold
        
    def should_sell(self):
        diff = self.current_rate - self.reference_rate
        return is_close_zero(self.pln_credit) and diff/self.reference_rate > self.sell_threshold

    def print_rates(self):
        print(self.rates)

    def print_result(self):
        if not is_close_zero(self.pln_credit):
            print("Left {0} PLN".format(self.pln_credit))
        else:
            print("Left {0} EUR which is {1} PLN with rate: {2}".format(self.eur_credit, self.eur_credit*self.current_rate, self.current_rate))

    def get_result(self):
        if not is_close_zero(self.pln_credit):
            return self.pln_credit
        else:
            return self.eur_credit*self.current_rate

BUY_THRESHOLD_KEY = "buy_threshold_key"
SELL_THRESOLD_KEY = "sell_threshold_key"

class Optimizer(object):
    def __init__(self):
        self._init_hyper_space()
        self._loss_number = 0
        self._win_number = 0

    def optimize(self):
        result = fmin(fn=self._objective, space=self._hyper_space, algo=tpe.suggest, max_evals=3000)
        print("Loss number:{0} win number:{1}".format(self._loss_number, self._win_number))
        return space_eval(self._hyper_space, result)

    def _objective(self, args):
        buy_threshold, sell_threshold = args

        sim = Simulation("gpw_d.csv.txt", 1000, buy_threshold, sell_threshold)
        sim.read_data()
        sim.simulate()
        result = sim.get_result()

        if result < 1000.0:
            self._loss_number += 1 
        else:
            self._win_number += 1

            print("Result:{0}".format(result))
        return 1.0/result

    def _init_hyper_space(self):
        self._hyper_space = [hp.uniform(BUY_THRESHOLD_KEY, -0.5, 0.0), hp.uniform(SELL_THRESOLD_KEY, 0.0, 0.5)]



def simulate(buy_threshold, sell_threshold):
    sim = Simulation("gpw_d.csv.txt", 1000, buy_threshold, sell_threshold)
    sim.read_data()
    sim.simulate()
    sim.print_result()
    print("Used parameters buy_threshold:{0} sell_threshold:{1}", buy_threshold, sell_threshold)


def main():
   optimizer = Optimizer()
   result = optimizer.optimize()

   simulate(result[0], result[1])


if __name__ == "__main__":
    main()
