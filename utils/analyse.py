from pandas import Series, read_csv, DatetimeIndex, DataFrame, concat, isna


def analyze_financial_statements(
        statement_fn,
        store_fn=None,
        updating=False,
        encoding="utf-8",
        smooth=1e-8
):
    """
    财务报表分析，统计营运资本、流动比率、资产负债率指标、产权比率，
    以及用于市盈率估计的预估全年净利润(动)、预估全年净利润(静)和预估全年净利润(TTM)

    Parameters
    ----------
    statement_fn: str, path object or file-like object or DataFrame
        财务报表文件路径或DataFrame.
    store_fn: str, default None
        分析后报表存储路径。None表示不存储。
    updating: bool, default False
        当updating为True时，只更新财务报表的第一个条目（最新的财务报表）。
    encoding: str, default "utf-8"
        财务报表文件编码格式。
    smooth: float, default 1e-8
        避免除零的平滑参数。

    Returns
    -------
    DataFrame
        分析后的财务报表。

    Notes
    -----
    分析后的Dataframe将包含营运资本、流动比率、资产负债率指标、产权比率
    以及预估全年净利润(动)、预估全年净利润(静)和预估全年净利润(TTM)列。

    """

    if type(statement_fn) is DataFrame:
        statement = statement_fn
    else:
        statement = read_csv(statement_fn, index_col=0, encoding=encoding)
        statement.index = DatetimeIndex(statement.index)

    start_date = statement.index[0]
    if updating:
        statement.loc[start_date, "营运资本(万元)"] = \
            statement["流动资产合计(万元)"][start_date] - statement["流动负债合计(万元)"][start_date]

        statement.loc[start_date, "流动比率"] = \
            (statement["流动资产合计(万元)"][start_date] + smooth) / (statement["流动负债合计(万元)"][start_date] + smooth)

        statement.loc[start_date, "资产负债率"] = \
            (statement["负债合计(万元)"][start_date] + smooth) / (statement["资产总计(万元)"][start_date] + smooth)

        statement.loc[start_date, "产权比率"] = \
            (statement["负债合计(万元)"][start_date] + smooth) / (statement["所有者权益(或股东权益)合计(万元)"][start_date] + smooth)
    else:
        statement["营运资本(万元)"] =\
            statement["流动资产合计(万元)"] - statement["流动负债合计(万元)"]
        
        statement["流动比率"] =\
            (statement["流动资产合计(万元)"] + smooth) / (statement["流动负债合计(万元)"] + smooth)
        
        statement["资产负债率"] =\
            (statement["负债合计(万元)"] + smooth) / (statement["资产总计(万元)"] + smooth)
        
        statement["产权比率"] =\
            (statement["负债合计(万元)"] + smooth) / (statement["所有者权益(或股东权益)合计(万元)"] + smooth)

    if "预估全年净利润(动)" not in statement:
        statement = concat([
            statement, Series(index=statement.index, name="预估全年净利润(动)")
        ], axis=1)
    profit = statement["净利润(万元)"].iloc[0]
    start_year = start_date.year
    season = 0
    for date in statement.index:
        if date.year == start_year:
            season += 1
        else:
            break
    p = profit * 4 / season
    if isna(p):
        p = 0
    statement.loc[start_date, "预估全年净利润(动)"] = p

    if "预估全年净利润(静)" not in statement:
        statement = concat([
            statement, Series(index=statement.index, name="预估全年净利润(静)")
        ], axis=1)
    p = 0
    for date in statement.index:
        if date.year == start_year-1:
            p = statement["净利润(万元)"][date]
            break
    if isna(p):
        p = 0
    statement.loc[start_date, "预估全年净利润(静)"] = p

    if "预估全年净利润(TTM)" not in statement:
        statement = concat([
            statement, Series(index=statement.index, name="预估全年净利润(TTM)")
        ], axis=1)
    p = profit
    count = 0
    for date in statement.index:
        if date.year == start_year:
            count += 1
        else:
            break
    if count < 4:
        end_of_last_year = None
        for date in statement.index:
            if date.year != start_year:
                if end_of_last_year is None:
                    end_of_last_year = statement["净利润(万元)"][date]
                if count == 4:
                    p += end_of_last_year - statement["净利润(万元)"][date]
                    break
                count += 1
    if isna(p):
        p = 0
    statement.loc[start_date, "预估全年净利润(TTM)"] = p
    
    if store_fn is not None:
        statement.to_csv(store_fn, encoding=encoding)

    return statement


def analyze_historical_trading_data(
        trading_fn,
        statement_fn,
        store_fn=None,
        encoding="utf-8",
        smooth=1e-8
):
    """
    分析历史交易数据，计算市盈率(动)、市盈率(静)和市盈率(TTM）

    Parameters
    ----------
    trading_fn: str, path object or file-like object or DataFrame
        历史交易数据文件路径或DataFrame.
    statement_fn: str, path object or file-like object or DataFrame
        财务报表文件路径或DataFrame.
    store_fn: str, default None
        分析后历史交易数据存储路径。None表示不存储。
    encoding: str, default "utf-8"
        财务报表文件编码格式。
    smooth: float, default 1e-8
        避免除零的平滑参数。

    Returns
    -------
    DataFrame
        分析后的历史交易数据。

    Notes
    -----
    分析后的Dataframe将包含市盈率(动)列、市盈率(静)列和市盈率(TTM）列。

    """

    if type(trading_fn) is DataFrame:
        trading = trading_fn
    else:
        trading = read_csv(trading_fn, index_col=0, encoding=encoding)
        trading.index = DatetimeIndex(trading.index)

    if type(statement_fn) is DataFrame:
        statement = statement_fn
    else:
        statement = read_csv(statement_fn, index_col=0, encoding=encoding)
        statement.index = DatetimeIndex(statement.index)

    value = trading["总市值"].iloc[0] / 1e4
    start_date = trading.index[0]
    
    if "市盈率(动)" not in trading:
        trading = concat([
            trading, Series(index=trading.index, name="市盈率(动)")
        ], axis=1)
    trading.loc[start_date, "市盈率(动)"] = (value + smooth) / (statement["预估全年净利润(动)"].iloc[0] + smooth)

    if "市盈率(静)" not in trading:
        trading = concat([
            trading, Series(index=trading.index, name="市盈率(静)")
        ], axis=1)
    trading.loc[start_date, "市盈率(静)"] = (value + smooth) / (statement["预估全年净利润(静)"].iloc[0] + smooth)

    if "市盈率(TTM)" not in trading:
        trading = concat([
            trading, Series(index=trading.index, name="市盈率(TTM)")
        ], axis=1)
    trading.loc[start_date, "市盈率(TTM)"] = (value + smooth) / (statement["预估全年净利润(TTM)"].iloc[0] + smooth)
    
    if store_fn is not None:
        trading.to_csv(store_fn, encoding=encoding)

    return trading
