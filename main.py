import csv
import numpy as np


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
        self.rates = (npdata[:,3]).astype(float)
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
        buy_rate = self.current_rate * 1.00354
        self.reference_rate = self.current_rate

        self.get_provision()

        self.eur_credit = (self.pln_credit) * 1.0/buy_rate
        self.pln_credit = 0.0

    def sell(self):
        sell_rate = self.current_rate * 0.996403
        self.reference_rate = self.current_rate

        self.pln_credit = (self.eur_credit * sell_rate)
        self.eur_credit = 0.0

        self.get_provision()

    def get_provision(self):
        self.pln_credit -= 2.0

    def should_buy(self):
        should = int(self.eur_credit) == 0 and self.current_rate - self.reference_rate < -0.1
        print(should)
        return should

    def should_sell(self):
        return int(self.pln_credit) == 0 and self.current_rate - self.reference_rate > 0.1

    def print_rates(self):
        print(self.rates)

    def print_result(self):
        if int(self.pln_credit) != 0:
            print("Left {0} PLN".format(self.pln_credit))
        else:
            print("Left {0} EUR which is {1} PLN with rate: {2}".format(self.eur_credit, self.eur_credit*self.current_rate, self.current_rate))


def main():
    print("forex sim 0.1")
    sim = Simulation("eur_pln.dat", 1000)
    sim.read_data()
    sim.simulate()
    sim.print_result()


if __name__ == "__main__":
    main()