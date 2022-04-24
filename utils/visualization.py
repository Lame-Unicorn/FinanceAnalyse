from pandas import read_csv, DatetimeIndex, DataFrame
from matplotlib.pyplot import subplots, legend, savefig, rcParams
from matplotlib import style
from mplfinance import plot as mplot, make_marketcolors, make_mpf_style


def draw_Kline(
        source_fn,
        store_fn=None,
        store_dict=None,
        n_display=40,
        mav=(5, 10, 20),
        encoding="utf-8",
):
    """
    根据历史交易数据绘制K线图。

    Parameters
    ----------
    source_fn: str, path object or file-like object or DataFrame
        历史交易数据文件或DataFrame。
    store_fn: str, default None
        K线图存储路径。
    store_dict: dict, default None
        {"daily": ..., "weekly": ..., "monthly": ...}
        日K线图、周K线图和月K线图存储路径，None表示不存储。
    n_display: int, default 40
        展示多少条数据的K线图，默认72.
    mav: tuple of int, default (5, 10, 20)
        平均K线图窗口大小。
    encoding: str, default "utf-8"
        历史交易数据文件编码格式。

    """
    mc = make_marketcolors(up='darkred', down='g', inherit=True)
    s = make_mpf_style(base_mpf_style="default", marketcolors=mc)

    if type(source_fn) is DataFrame:
        source = source_fn
    else:
        source = read_csv(source_fn, encoding=encoding, index_col=0)
    hist_df = source[["开盘价", "最高价", "最低价", "收盘价", "成交量"]]
    hist_df.columns = ["Open", "High", "Low", "Close", "Volume"]
    hist_df.index = DatetimeIndex(hist_df.index)
    hist_df.index.name = "Date"

    if store_fn is not None:
        mplot(
            hist_df.iloc[:n_display].sort_index(),
            type="candle", mav=mav,
            volume=True, savefig=store_fn,
            style=s
        )
        return
    else:
        aggregations = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum"
        }
        if "daily" in store_dict and store_dict["daily"] is not None:
            mplot(
                hist_df.iloc[:n_display].sort_index(),
                type="candle", mav=mav,
                volume=True, savefig=store_dict["daily"],
                style=s
            )
        if "weekly" in store_dict and store_dict["weekly"] is not None:
            weekly = hist_df[:5 * n_display].resample("1W").agg(aggregations)
            mplot(
                weekly,
                type="candle", mav=mav,
                volume=True, savefig=store_dict["weekly"],
                style=s
            )
        if "monthly" in store_dict and store_dict["monthly"] is not None:
            monthly = hist_df[:int(n_display * 150 / 7)].resample("1M").agg(aggregations)
            mplot(
                monthly,
                type="candle", mav=mav,
                volume=True, savefig=store_dict["monthly"],
                style=s
            )


def draw_financial_states(
        source_fn,
        store_fn=None,
        preset=None,
        n_display=8,
        store_dict=None,
        encoding="utf-8",
        logy=False,
):
    """
    绘制财务报表折线图。

    Parameters
    ----------
    source_fn: str, path object or file-like object or DataFrame
        历史财务报表文件或DataFrame。
    store_fn: str, default None
        绘制单个财务报表统计图时，统计图的存储位置，None表示不选择绘制单张图表。
    preset: int, default None
        绘制单个财务报表统计图时，选择的预设模式：
        1. 投资总额分析：资产总计、流动资产总计和非流动资产总计的折线图
        2. 筹资总额分析：负债合计、流动负债合计、非流动负债合计和股东权益合计的折线图
        3. 现金流量分析：经营活动现金流量净额、投资活动现金流量净额和筹资活动现金流量净额的折线图
        4. 营运资本指标分析：营运资本（流动资产-流动负债）的柱状图
        5. 流动比率指标分析：流动比率（流动资产/流动负债）的折线图
        6. 资产负债率指标分析：资产负债率（负债合计/资产合计）的折线图
        7. 产权比率指标分析：产权比率（负债合计/股东权益合计）的折线图
    n_display: int, default 8
        展示的数据量。
    store_dict：dict, default None
        {preset_id: filename}
        绘制多张统计图时，传入需要绘制的统计图内容，以及对应的存储位置。
    encoding: str, default "utf-8"
        历史财务报表文件编码格式。
    logy: bool, default False
        展示多条数据时，量级差别过大，是否使用log(y)作图。


    """
    style.use("bmh")
    rcParams['font.sans-serif'] = ['SimHei']
    rcParams['axes.unicode_minus'] = False

    if type(source_fn) is DataFrame:
        report = source_fn
    else:
        report = read_csv(source_fn, encoding=encoding, index_col=0)
        report.index = DatetimeIndex(report.index)
    report = report.iloc[:n_display]
    report = report.sort_index()
    report.index = report.index.strftime("%Y-%m")

    if store_fn is not None:
        _draw_financial_state(report, store_fn, preset)
        return
    elif store_dict is not None:
        for preset in store_dict:
            _draw_financial_state(report, store_dict[preset], preset, logy)


def _draw_financial_state(data_df, store_fn, preset, logy):
    # 投资总额分析：资产总计、流动资产总计和非流动资产总计的折线图
    if preset == 1:
        labels = ["资产总计(万元)", "流动资产合计(万元)", "非流动资产合计(万元)"]
        data = data_df[labels[:-1]]
        data[labels[-1]] = data[labels[0]] - data[labels[1]]
        _, ax = subplots()
        data.plot(ax=ax, logy=logy)
        legend()
        savefig(store_fn)
        return
    # 筹资总额分析：负债合计、流动负债合计、非流动负债合计和股东权益合计的折线图
    elif preset == 2:
        labels = ["流动负债合计(万元)", "非流动负债合计(万元)", "所有者权益(或股东权益)合计(万元)"]
        data = data_df[labels]
        _, ax = subplots()
        data.plot(ax=ax, logy=logy)
        legend()
        savefig(store_fn)
        return
    # 现金流量分析：经营活动现金流量净额、投资活动现金流量净额和筹资活动现金流量净额的折线图
    elif preset == 3:
        labels = ["经营活动产生的现金流量净额(万元)", "投资活动产生的现金流量净额(万元)", "筹资活动产生的现金流量净额(万元)"]
        data = data_df[labels]
        _, ax = subplots()
        data.plot(ax=ax, logy=logy)
        legend()
        savefig(store_fn)
        return
    # 营运资本指标分析：营运资本（流动资产-流动负债）的柱状图
    elif preset == 4:
        label = "营运资本(万元)"
        data = data_df[label]
        _, ax = subplots()
        data.plot(kind="bar", label=label, ax=ax)
        legend()
        savefig(store_fn)
        return
    # 流动比率指标分析：流动比率（流动资产 / 流动负债）的折线图
    elif preset == 5:
        label = "流动比率"
        data = data_df[label]
        _, ax = subplots()
        data.plot(label=label, ax=ax)
        legend()
        savefig(store_fn)
        return
    # 资产负债率指标分析：资产负债率（负债合计/资产合计）的折线图
    elif preset == 6:
        label = "资产负债率"
        data = data_df[label]
        _, ax = subplots()
        data.plot(label=label, ax=ax)
        legend()
        savefig(store_fn)
        return
    # 产权比率指标分析：产权比率（负债合计/股东权益合计）的折线图
    elif preset == 7:
        label = "产权比率"
        data = data_df[label]
        _, ax = subplots()
        data.plot(label=label, ax=ax)
        legend()
        savefig(store_fn)
        return

    raise AssertionError(f"Unknown perset: {preset}")
