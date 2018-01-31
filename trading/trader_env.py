import pandas as pd
import numpy as np
from collections import Counter
import tensorflow as tf
from box import Box
from tensorforce.environments import Environment
from tensorforce.execution import Runner

class TradingEnv(Environment):
    def __init__(self, name='ppo_agent', train_data_path):

        self.agent_name = name
        self.train_data = pd.read_csv(data_path)

        self.all_prices = {
            'eth': 1200,
            'btc': 12000
        }
        self.update_all_usd_prices()

        self.all_coins = {
            'eth': 10.0,
            'btc': 1.0
        }

        # Accumulator used to track progress 
        self.acc = Box(
            episode=dict(
                i=0,
                total_steps=0,
                advantages=[],
                uniques=[]
            ),
            step=dict(i=0)
        )

        max_trade = min_trade * 5  # limit trade size to ~ $1000 (0.1 BTC)

        self.action_space = dict(
                action=dict(type='int', shape=(), num_actions=3), #buy BTC/sell BTC/hold (do nothing)
                amount=dict(type='float', shape=(), min_value=self.min_trade, max_value=max_trade)) #trade size

        self.signal_dict = {
            0: -1,  # make amount negative
            1: 0,  # hold
            2: 1  # make amount positive
        }

        # Observation space
        self.state_space = dict(
            timeseries=dict(type='float', shape=self.train_data),  # time dependent features
            stationary=dict(type='float', shape=2)  # btc/eth holdings
        )

    def __str__(self): return 'TradingEnv'

    @property
    def states(self): return self.state_space

    @property
    def actions(self): return self.action_space

    # Setup fixed random seed
    def seed(self, seed=None):
        random.seed(seed)
        np.random.seed(seed)
        tf.set_random_seed(seed)

    # Convert all coin values
    def update_all_usd_prices(self):
        for key in self.all_prices:
            try:
                self.all_prices[key] = int(requests.get("https://api.cryptowat.ch/markets/gdax/{}usd/price".format(key)).json()['result']['price'])
            except:
                self.all_prices[key] = self.all_prices[key]


    def get_next_state(self, i, cash, repeats):
        series = self.observations[i]
        stationary = [cash, repeats]

        return dict(series=series, stationary=stationary)


    def execute(self, actions):
        signal = self.signal_dict[actions['action']] * actions['amount']
        if not signal: signal = 0  

        step_acc, ep_acc = self.acc.step, self.acc.episode

        step_acc.signals.append(float(signal))

        fee = 0.001
        reward = 0

        abs_sig = abs(signal)
        before = Box(cash=step_acc.cash, value=step_acc.value, total=step_acc.cash+step_acc.value)
        if signal > 0 and not (abs_sig > step_acc.cash):
            step_acc.value += abs_sig - abs_sig*fee
            step_acc.cash -= abs_sig
        elif signal < 0 and not (abs_sig > step_acc.value):
            step_acc.cash += abs_sig - abs_sig*fee
            step_acc.value -= abs_sig

    def episode_finished(self, runner):
        step_acc, ep_acc = self.acc.step, self.acc.episode
        time_ = round(time.time() - self.time)
        signals = step_acc.signals

        advantage = ((step_acc.cash + step_acc.value) - (self.start_cash + self.start_value)) - \
                    ((step_acc.hold.value + step_acc.hold.cash) - (self.start_cash + self.start_value))
        self.acc.episode.advantages.append(advantage)
        n_uniques = float(len(np.unique(signals)))
        self.acc.episode.uniques.append(n_uniques)

        # Print (limit to note-worthy)
        common = dict((round(k,2), v) for k, v in Counter(signals).most_common(5))
        completion = f"|{int(ep_acc.total_steps / TIMESTEPS * 100)}%"
        print(f"{ep_acc.i}|:{step_acc.i}{completion}\tA:{'%.3f'%advantage}\t{common}({n_uniques}uniq)")
        return True

    def run_deterministic(self, runner, print_results=True):
        next_state, terminal = self.reset(), False
        while not terminal:
            next_state, terminal, reward = self.execute(runner.agent.act(next_state, deterministic=True))
        if print_results: self.episode_finished(None)

    def train_and_test(self, agent, early_stop=-1, n_tests=15):
        n_train = TIMESTEPS // n_tests
        i = 0
        runner = Runner(agent=agent, environment=self)

        try:
            while i <= n_tests:
                self.use_dataset(Mode.TRAIN)
                runner.run(timesteps=n_train, max_episode_timesteps=n_train)
                self.use_dataset(Mode.TEST)
                self.run_deterministic(runner, print_results=True)
                i += 1
        except KeyboardInterrupt:
            # Lets us kill training with Ctrl-C and skip straight to the final test. This is useful in case you're
            # keeping an eye on terminal and see "there! right there, stop you found it!" (where early_stop & n_tests
            # are the more methodical approaches)
            pass

        # On last "how would it have done IRL?" run, without getting in the way (no killing on repeats, 0-balance)
        print('Running no-kill test-set')
        self.use_dataset(Mode.TEST, no_kill=True)
        self.run_deterministic(runner, print_results=True)
