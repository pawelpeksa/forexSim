import csv
import numpy as np

def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def is_close_zero(a):
    return is_close(a, 0.0)
    
class Simulation(object):
    def __init__(self, data_file, credit):
        self.data_file = data_file
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
        print("Steps numer:{0}".format(len(self.rates)))
        for rate in self.rates:
            self.do_step(rate)

    def do_step(self, rate):
        self.current_rate = rate

        if self.should_buy():
            self.buy()
        elif self.should_sell():
            self.sell()

    def buy(self):
        print("I buy, current_rate:{0} reference rate:{1}".format(self.current_rate, self.reference_rate))
        buy_rate = self.current_rate * 1.00354 # 1.00354 - buy spread
        self.reference_rate = self.current_rate

        self.get_provision()

        self.eur_credit = (self.pln_credit) * (1.0/buy_rate)
        self.pln_credit = 0.0

    def sell(self):
        print("I sell")
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
        return is_close_zero(self.eur_credit) and diff/self.reference_rate < -0.02
        
    def should_sell(self):
        diff = self.current_rate - self.reference_rate
        return is_close_zero(self.pln_credit) and diff/self.reference_rate > 0.002

    def print_rates(self):
        print(self.rates)

    def print_result(self):
        if not is_close_zero(self.pln_credit):
            print("Left {0} PLN".format(self.pln_credit))
        else:
            print("Left {0} EUR which is {1} PLN with rate: {2}".format(self.eur_credit, self.eur_credit*self.current_rate, self.current_rate))


def main():
    print("forex sim 0.1")
    #sim = Simulation("eur_pln.dat", 1000)
    sim = Simulation("gpw_d.csv.txt", 1000)
    sim.read_data()
    sim.simulate()
    sim.print_result()


if __name__ == "__main__":
    main()