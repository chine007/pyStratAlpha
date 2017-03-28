## Note on FactorAnalyzer member functions

> FactorAnalyzer类中大量引用了alphalens的分析函数

### 获取股票分组后的组平均超额收益
<pre> alphalens/utils.deman_foward_retrun </pre>

必传参数
factor_data : pd.DataFrame -MultiIndex 
索引为日期('date')和股票代码('asset')，列为未来若干天的收益，一般为1，5,10

可选参数
grouper :  list
将索引分组，一般以行业划分。若无，则全市场作为一组，不划分。

返回
分组后相对所对应的组的平均超额收益。比如工商银行10天的收益为4%，银行行业为3%，则返回1%


### 获取股票未来若干天收益
<pre> alphalens/utils.get_clean_factor_and_forward_returns </pre>

必传参数
factor : pd.Series - MultiIndex
索引为日期('date')和股票代码('asset')，值为日期和股票代码确定的因子得分
prices : pd.DataFrame 
索引为日期('date')和股票代码('asset')，值为日期和股票代码确定的股票价格

可选参数
groupby : pd.Series - MultiIndex or dict
将股票分组的依据
by_group : bool
是否将股票分组，如果为True则对每组分别进行计算。
quantiles : int or sequence[float]
将因子得分从高到低分成N组或者根据数组里的分位数值进行划分，如[0, .10, .5, .90, 1.]，默认为5组
bins : int or sequence[float]
与quantiles一样是因子分组参数，两者仅需要一个
periods : sequence[int]
计算未来一段时间的收益，具体时间天数由periods决定
filter_zscore : int or float
设置阈值，对于那些股票收益超过X个标准方差的剔除
groupby_labels : dict
分组的标签

返回
merged_data : pd.DataFrame - MultiIndex
索引为日期和股票代码，值为未来一段时间收益，以及其因子得分的分位数

