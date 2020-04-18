import pandas as pd
import matplotlib.pyplot as plt

btc_usd = pd.read_csv("/Users/ramborghini/Documents/GitHub/CryptocurrencyTrading/data_output/BTC-USD.csv")
btc_eur = pd.read_csv("/Users/ramborghini/Documents/GitHub/CryptocurrencyTrading/data_output/BTC-EUR.csv")
bch_usd = pd.read_csv("/Users/ramborghini/Documents/GitHub/CryptocurrencyTrading/data_output/BCH-USD.csv")
bch_eur = pd.read_csv("/Users/ramborghini/Documents/GitHub/CryptocurrencyTrading/data_output/BCH-EUR.csv")
bch_btc = pd.read_csv("/Users/ramborghini/Documents/GitHub/CryptocurrencyTrading/data_output/BCH-BTC.csv")

# plot 1 min volatility
plt.figure()
fig, axs = plt.subplots(2, 2, constrained_layout=True)
fig.set_size_inches(9.5, 6.5)

axs[0, 0].plot(btc_usd["time_period"], btc_usd["volatility_mid_1min"], label = "mid_vol")
axs[0, 0].plot(btc_usd["time_period"], btc_usd["volatility_last_1min"], label = "last_vol")
axs[0, 0].legend()
axs[0, 0].set(ylabel='BTC-USD 1 min Volatility')

axs[0, 1].plot(btc_eur["time_period"], btc_eur["volatility_mid_1min"], label = "mid_vol")
axs[0, 1].plot(btc_eur["time_period"], btc_eur["volatility_last_1min"], label = "last_vol")
axs[0, 1].legend()
axs[0, 1].set(ylabel='BTC-EUR 1 min Volatility')

axs[1, 0].plot(bch_eur["time_period"], bch_eur["volatility_mid_1min"], label = "mid_vol")
axs[1, 0].plot(bch_eur["time_period"], bch_eur["volatility_last_1min"], label = "last_vol")
axs[1, 0].legend()
axs[1, 0].set(xlabel='period', ylabel='BCH-EUR 1 min Volatility')

axs[1, 1].plot(bch_btc["time_period"], bch_btc["volatility_mid_1min"], label = "mid_vol")
axs[1, 1].plot(bch_btc["time_period"], bch_btc["volatility_last_1min"], label = "last_vol")
axs[1, 1].legend()
axs[1, 1].set(xlabel='period', ylabel='BCH-BTC 1 min Volatility')

plt.savefig('./figure_output/1min_vol.png', dpi=fig.dpi)
plt.show()

# plot 3 min volatility
plt.figure()
fig, axs = plt.subplots(2, 2, constrained_layout=True)
fig.set_size_inches(9.5, 6.5)

axs[0, 0].plot(btc_usd["time_period"], btc_usd["volatility_mid_3min"], label = "mid_vol")
axs[0, 0].plot(btc_usd["time_period"], btc_usd["volatility_last_3min"], label = "last_vol")
axs[0, 0].legend()
axs[0, 0].set(ylabel='BTC-USD 3 min Volatility')

axs[0, 1].plot(btc_eur["time_period"], btc_eur["volatility_mid_3min"], label = "mid_vol")
axs[0, 1].plot(btc_eur["time_period"], btc_eur["volatility_last_3min"], label = "last_vol")
axs[0, 1].legend()
axs[0, 1].set(ylabel='BTC-EUR 3 min Volatility')

axs[1, 0].plot(bch_eur["time_period"], bch_eur["volatility_mid_3min"], label = "mid_vol")
axs[1, 0].plot(bch_eur["time_period"], bch_eur["volatility_last_3min"], label = "last_vol")
axs[1, 0].legend()
axs[1, 0].set(xlabel='period', ylabel='BCH-EUR 3 min Volatility')

axs[1, 1].plot(bch_btc["time_period"], bch_btc["volatility_mid_3min"], label = "mid_vol")
axs[1, 1].plot(bch_btc["time_period"], bch_btc["volatility_last_3min"], label = "last_vol")
axs[1, 1].legend()
axs[1, 1].set(xlabel='period', ylabel='BCH-BTC 3 min Volatility')

plt.savefig('./figure_output/3min_vol.png', dpi=fig.dpi)
plt.show()
