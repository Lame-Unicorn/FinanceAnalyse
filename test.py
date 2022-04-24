from utils.analyse import analyze_financial_statements, analyze_historical_trading_data
from utils.visualization import draw_Kline, draw_financial_states

test_field = "test_file\\"
statement = analyze_financial_statements(test_field + "statements.csv", test_field + "statement.csv")
_ = analyze_financial_statements(test_field + "statements2.csv", test_field + "statement2.csv", updating=True)
_ = analyze_historical_trading_data(test_field + "history.csv", statement, test_field + "trading.csv")
draw_financial_states(statement, store_dict=dict([(i, test_field + f"{i}.png") for i in range(1, 8)]))
draw_Kline(
    test_field + "trading.csv",
    store_dict={
        "daily": test_field + "daily.png",
        "weekly": test_field + "weekly.png",
        "monthly": test_field + "monthly.png"
    }
)
