# README

## Project Goals
- Reinforcement learning model to exploit intra-day volatility in crypto markets


## Current TODOs

### TE
- [ ]

### SBH
- [ ] set up a sqlite database.
    - Single klines table
    - Ideally, we'd follow something like [this](https://jiripik.com/2017/02/04/optimal-database-architecture-super-fast-access-historical-currency-market-data-mysql/). But since we're initially only dealing w/ BTC x ETH, we'll be scrappy and have a single table.
    **One values table per currency pair** – For each currency pair, we have one table with the Date being the primary key -> choosing the currency pair leads to the choice of the right table (we have about 40k tables!), and Date being the primary key making searches ultra-fast
    **Prepopulation of the tables with null values for every single day since Jan 1, 1999 till Jan 1, 2018** – Each table is pre-populated with blank rows with null value for every single day since Jan 1, 1999 till Jan 1, 2018 (a year from now) which eliminates the time and resources expensive index rebuilds and when a new value arrives, the corresponding row is simply updated (without triggering an index rebuild)
- [ ] query `python -m indicators.BinanceIndicators`
