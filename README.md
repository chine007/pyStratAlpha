
## pyStratAlpha

Alpha Research and Strategies Lib in Python

本项目试图以python实现一些算法公开的Alpha策略和相关分析

##### 依赖:

<pre><br />- Finance-Python, version 0.5.3<br />  * link: <a href="https://github.com/wegamekinglc/Finance-Python" target="_blank">https://github.com/wegamekinglc/Finance-Python</a><br />  * 安装此package需要有C++编译器，细节请见上面的链接<br />- numpy, version 1.11.1<br />- pandas, version 0.18.1<br />- empyrical, version 0.2.2<br />- pyfolio, version 0.6.0<br />- alphalens, version 0.0.0<br />- windpy, 使用时需要打开wind终端<br />- tushare, version 0.5.8<br /> * windpy和tushare均可作为数据源的package， 使用时二选一即可
</pre>

##### 如何使用:

###### 因子数据的加载
将本主页的另一个项目pyStratData下的数据文件 
<pre> pyStratData/AlphaData/data.zip </pre>
拷贝至本项目如下目录即可 
<pre> pyStratAlpha/data/</pre>

###### 策略模块的运行
主要在下面文件夹中
<pre>pyStratAlpha/analyzer/
pyStratAlpha/strat/</pre>
