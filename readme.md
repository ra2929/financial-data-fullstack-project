# financial-data-fullstack-project

## about

Goal: Develop a time-series database of stock and index prices with special attention to unusual options data.

Methods: This project showcases full-stack development using a PostGRESQL database, python simple-http server, and Flask web framework. To obtain historical minute-tick financial data, we used a hook for the TD Ameritrade REST API located in the `td-ameritrade_API_hook` folder.

Constraints: Could not use Object Relational Management (ORM) functionality of libraries such as SQLalchemy.

For the web front-end, we developed a website to display candle-stick charts for specific financial products listed in the `csv_data_for_db folder`. There was also a page to view unusual options activity.

The sql_schema folder contians the associated SQL schema with custom postgresql functions.


## installation

```
git clone
pip install -r requirements.txt
```

## run

```
python server.py
```
