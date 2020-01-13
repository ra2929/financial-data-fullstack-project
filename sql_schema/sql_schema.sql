CREATE TABLE Time_Info(
  curr_DATE DATE,
  curr_time TIME,

  PRIMARY KEY (curr_DATE, curr_time)
);

CREATE TABLE Sector(
  sec_name varchar(64),

  PRIMARY KEY (sec_name)
);

CREATE TABLE Indexes(
  type varchar(20),
  idx_name varchar(64),
  
  PRIMARY KEY (idx_name)
);

CREATE TABLE Ticker(                             
  ticker varchar(20) NOT NULL,
  co_name varchar(64),
  sec_name varchar(64),
  idx_name varchar(64),
  type varchar(20),

  UNIQUE (ticker),
  PRIMARY KEY (ticker),
  FOREIGN KEY (sec_name) REFERENCES Sector ON DELETE CASCADE,
  FOREIGN KEY (idx_name) REFERENCES Indexes ON DELETE CASCADE
  -- FOREIGN KEY (type) REFERENCES Indexes ON DELETE CASCADE   -- IN CURRENT IMPLEMENTATION, REMOVE FUTURE UPDATES
);

CREATE TABLE Includes(
  idx_name varchar(64),
  ticker varchar(20) NOT NULL,

  FOREIGN KEY (idx_name) REFERENCES Indexes ON DELETE CASCADE,
  FOREIGN KEY (ticker) REFERENCES Ticker ON DELETE CASCADE
);

CREATE TABLE Market_Data(
  ticker varchar(20) NOT NULL,
  curr_date DATE,
  curr_time TIME,


  FOREIGN KEY (ticker) REFERENCES Ticker,
  FOREIGN KEY (curr_date, curr_time) REFERENCES Time_Info
);

CREATE TABLE Options_Data(
  o_strike REAL NOT NULL,
  o_symbol varchar(20) NOT NULL,
  o_position varchar(20) NOT NULL,
  o_ask_price NUMERIC(10,2) NOT NULL,
  o_bid_price NUMERIC(10,2) NOT NULL,
  o_volume BIGINT NOT NULL,
  o_open_interest BIGINT NOT NULL,
  o_implied_volatility REAL NOT NULL,
  o_ask_size BIGINT NOT NULL,
  o_bid_size BIGINT NOT NULL,
  o_expiry DATE NOT NULL,
  ticker varchar(20) NOT NULL,
  curr_date DATE,
  curr_time TIME,

  PRIMARY KEY (o_symbol, o_strike, o_expiry, o_position),
  FOREIGN KEY (ticker) REFERENCES Ticker,
  FOREIGN KEY (curr_date, curr_time) REFERENCES Time_Info
);

CREATE TABLE Price(
  p_value NUMERIC(10,2) NOT NULL,
  p_ask_price NUMERIC(10,2) NOT NULL,
  p_bid_price NUMERIC(10,2) NOT NULL,
  p_volume BIGINT NOT NULL,
  p_implied_volatility REAL NOT NULL,
  p_ask_size BIGINT NOT NULL,
  p_bid_size BIGINT NOT NULL,
  ticker varchar(20) NOT NULL,
  curr_date DATE,
  curr_time TIME,

  FOREIGN KEY (ticker) REFERENCES Ticker ON DELETE CASCADE,
  FOREIGN KEY (curr_date, curr_time) REFERENCES Time_Info
);

CREATE TABLE ticker_news(
  curr_date DATE,
  curr_time TIME,
  ticker varchar(20) NOT NULL,
  news_title text,
  news text,

  FOREIGN KEY (ticker) REFERENCES Ticker,
  FOREIGN KEY (curr_date, curr_time) REFERENCES Time_Info
);
 

CREATE TRIGGER opt_data
  BEFORE INSERT ON "options_data"
  FOR EACH ROW
  EXECUTE PROCEDURE more_than();

CREATE OR REPLACE FUNCTION opt_data()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.o_volume > 5000 THEN
        INSERT INTO options_overflow(o_strike, o_symbol, o_position, o_ask_price, o_bid_price,
        o_volume, o_open_interest, o_implied_volatility,o_ask_size, o_bid_size, o_expiry, ticker, curr_date, curr_time)
        VALUES (new.o_strike, new.o_symbol, new.o_position, new.o_ask_price, new.o_bid_price,
        new.o_volume, new.o_open_interest, new.o_implied_volatility, new.o_ask_size, new.o_bid_size,
        new.o_expiry, new.ticker, new.curr_date, new.curr_time);
    END IF;
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;