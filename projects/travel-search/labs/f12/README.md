# F12 · 更新、可见性与基础结业

先读[正文](../../../../framework/f12.html)。ES9.4.0/Lucene10.4.0，Boot4.0.8/JDK25（作者Temurin25.0.4.1+1）、官方Java与Rest5 Client9.4.8、Wrapper3.3.4/Maven3.9.11；应用JDK与ES bundled JVM分开。JAVA_HOME/PATH先选择JDK25。脚本仅Bash/curl/Python3标准库；Pages只承载教程，读者本机启动工程。

仓库根目录，终端一：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d es
bash infra/single-node/wait.sh
bash labs/f12/01-prepare.sh
bash labs/f12/02-crud.sh
bash labs/f12/03-conflict.sh
```

只创建tut-f12-attractions；一主零副本、strict、显式refresh_interval=-1。准备6请求检查版本/创建/green未超时/Bulk4项created且errors=false/refresh零失败/count4。CRUD36请求，冲突17请求；首尾重导原四份并refresh。被删除的文档恢复可为created，其余updated；结果取自本轮，不硬编码版本号。call打印完整请求/响应；预期错误不被curl的退出码误当失败。单独重复创建会报已存在，应点名清理后重做。

终端二（仍在projects/travel-search，JDK25）：

```bash
./backend/mvnw -f backend/pom.xml clean package
java -jar backend/target/travel-search-0.7.0.jar
```

终端一继续：

```bash
bash labs/f12/04-java.sh
```

Java27请求，覆盖创建/重复创建/完整替换/带版本局部更新及删除/404/刷新前后分页；Java实际DSL同PIT重放REST。打开 http://127.0.0.1:18080/f12.html ，先搜索再读取d-hz-garden、改价、GET、搜索、refresh、重新搜索。两个窗口先读同一ID再各自保存可复现409；重读覆盖草稿，需自己核对。UI不自动refresh，也不自动重试冲突。演示中的可见性必须在没有其他工具refresh的条件下观察。

基础结业先独立作答：只读[新样本](../../data/f12/graduation.json)，设计mapping、导入、查询“星湾”/HZ/CNY/open/0–6000分（含边界），价格/ID升序、PIT每页2份、Java与REST逐项比较，改价/下架/冲突、关闭与清理重做；保留自己的预测和解释。参考解不能替代独立作答。

完成尝试后，终端三启动同一个jar但固定结业索引：

```bash
APP_PORT=18081 TRAVEL_F12_INDEX=tut-f12-graduation java -jar backend/target/travel-search-0.7.0.jar
```

终端一运行事后参考解（28请求，含结业准备6条）：

```bash
bash labs/f12/05-graduation.sh
```

若自己已创建结业索引，应先关闭自己的分页、保存作答，再确认只删除tut-f12-graduation后运行参考解。不要把已存在错误忽略后继续导入。18081/f12.html的默认输入仍是演示条件，需要自己改“星湾”/60元/g-hz-garden。

初始free0/garden4500/museum6000，2/1，共3；garden7000分并refresh后free/museum，原PIT保留原三份；museum closed并refresh后只剩free，count仍8。其他五份分别超预算、closed、城市错、关键词错、USD。两位编辑者旧版本409与重读需要补自己的证据；作者在两轮验收中另以结业资料实际执行。

主流程114HTTP=准备6+CRUD36+冲突17+Java27+结业28，清理/探活/作者附加断言/浏览器重复另计。真实运行与限制见[验收](../../review/f12/README.md)，阅读与观察窗见[记录](../../../../docs/framework-review/20261021-f12-crud/README.md)。

先在两个观察窗关闭已知分页，再清理重做：

```bash
bash labs/f12/cleanup.sh
bash labs/f12/01-prepare.sh
bash labs/f12/02-crud.sh
bash labs/f12/03-conflict.sh
bash labs/f12/04-java.sh
bash labs/f12/05-graduation.sh
```

只删除tut-f12-attractions和tut-f12-graduation，404可继续，其他故障停下；不删卷/旧课索引。结束关闭自己启动的两个Java进程；框架ES原来停止则同compose stop es恢复，不动源码篇节点。
