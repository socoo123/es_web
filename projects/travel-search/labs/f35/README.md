# F35 · TLS、权限与 Java 安全连接

只操作独立 `travel-f35-lab`，ES 9.4.0；两个节点 HTTPS `127.0.0.1:19935/19936`，本机 Java `18085`。不操作已有 9200/9201。Pages 只承载教程；浏览器 → 本机 Java → HTTPS ES。应用 Boot 4.0.8 / JDK 25 / Java 与 Rest5 Client 9.4.8。

先看[正文](../../../../framework/f35.html)。本课复用景点观察窗；没有新增 Controller 或前端开发。

## 首次准备

在 `projects/travel-search` 执行；需要 Docker、Python 3 标准库、OpenSSL、完整 JDK 25。自行将 JAVA_HOME/PATH 指向 JDK 25。

```bash
python3 labs/f35/lab.py init --out /tmp/f35-reader-init
python3 labs/f35/lab.py start --out /tmp/f35-reader-setup
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f35-classpath.txt
cd ..
```

init 仅用于没有本课秘密文件和卷的全新环境；遇到已有资源拒绝覆盖。start 首次暂用 bootstrap，成团后移除；完整旧卷重启不重新引导；部分数据卷缺失拒绝重引导。不要在旧数据卷上改随机管理员密码。

`infra/f35/.local` 是 Git 忽略的 0700 目录，密码/key/私钥文件0600。证书卷只含公开 CA 与节点证书/私钥，不含 CA 签发私钥；节点读取卷为只读。不得提交 `.local` 或打印其内容。curl 的 Authorization 来自受限配置文件，秘密不出现在命令参数或 URL。实验不打印原始密钥响应，收据遮盖 password/api_key/encoded。

两节点同 Docker VM，各192MiB堆/640MiB上限，唯一master候选n1。网络 `172.30.35.0/24`，节点 `.11/.12`。证书SAN含节点DNS、固定IP、localhost、127.0.0.1；transport full校验会按发布IP验证。网段冲突时须同时调整 Compose 和 lab.py 中证书IP后在新环境生成。CA和节点证书30天有效，key一小时有效；到期不能关闭验证。HTTP/transport在本学习环境共用一个CA和每节点证书，跨机器部署应按安全边界拆分管理。

## 自动三案例，两轮

以下每个 `--out` 必须是不存在的新目录。`18085` 须空闲；run 自动启动/停止自己创建的 Java，途中不另开写入者。

```bash
python3 labs/f35/lab.py run --out /tmp/f35-reader-round1
python3 labs/f35/lab.py run --out /tmp/f35-reader-round2
```

- c01：错误CA/错误验证名在TLS失败、无HTTP状态；缺失/伪造key 401；管理员预建2主1副/strict/refresh=-1索引、导入固定六份、挂两个alias、创建受限用户和角色、分别发只读/写入key。
- c02：reader读read alias成功，直接物理名/写/健康管理/删索引/改角色403；writer在write alias改p01=6500、删p02成功，搜索/直接物理名写/refresh/设置/建索引403。管理员refresh。
- c03：错误CA→Java503，错误key与writer搜索→Java502；reader搜索只有p01/6500，修复后p01/6000和p02/0；撤销旧key→502，换文件仍502，重启后200。每次成功的Java esRequest都用reader REST重放，核对完整命中/价格。

每轮37教学REST＋8 Java接口HTTP、2 TLS失败调用；身份、guard、cleanup及作者可选浏览器附加另计。`summary.json` 按case计数；TLS不伪装成HTTP。作者 `--observer` 是额外Playwright证据，不是读者依赖。

## 手工路径（与自动路径二选一）

完整curl分阶段文件见 [requests.sh](requests.sh)。它会显示实际响应和HTTP码；手工检查不符预期时停止，先还原前提，不继续调用下个阶段。

```bash
bash labs/f35/requests.sh prepare /tmp/f35-manual-cleanup /tmp/f35-manual-credentials
bash labs/f35/requests.sh permissions
```

prepare先点名清理，然后建索引、等green、Bulk（逐条都应201且errors=false）、挂alias、发凭据。credentials动作由管理员创建原生角色/用户，用户用Basic申请只读key，管理员另发限制到write alias的key；原始响应秘密仅写入本机文件。read key的cluster为空，角色所有者的manage_own_api_key没有传给应用。

permissions：reader身份200、read alias搜索200/六份；物理名搜索、写、cluster health均403；writer改p01/删p02均200，writer搜索/refresh/改设置均403，admin refresh200。随后在另一个JDK25终端：

```bash
F35_LOCAL="$(cd infra/f35/.local && pwd)"
ES_URL=https://127.0.0.1:19935 ES_INDEX=tut-f35-attractions-read \
ES_CA_FILE="$F35_LOCAL/ca.crt" ES_API_KEY_FILE="$F35_LOCAL/reader-key.txt" \
APP_PORT=18085 java -jar backend/target/travel-search-0.7.0.jar
```

打开 `http://127.0.0.1:18085/`，默认“西湖/HZ/20000分/30.25,120.15/3km”。结果只有p01，6500分。esRequest是DSL，不是凭据；返回所有字段可与REST核对。

```bash
bash labs/f35/requests.sh repair
python3 labs/f35/lab.py revoke --out /tmp/f35-manual-revoke
python3 labs/f35/lab.py rotate --out /tmp/f35-manual-rotate
```

repair：writer恢复p01/200与p02/201，admin refresh；同Java变p01/6000与p02/0。revoke后Java502；rotate替换文件后旧Java仍502。原Java终端Ctrl+C，再用相同命令启动，恢复200。key在客户端创建时加载，不实现热更新；先撤销故意制造故障，不是生产无中断轮换步骤。生产应先发/加载并核对新key，再撤销旧key。

TLS与认证手工观察（不发送真实秘密到命令参数）：

```bash
F35_LOCAL="$(cd infra/f35/.local && pwd)"
curl -sS --cacert "$F35_LOCAL/wrong-ca.crt" https://127.0.0.1:19935/_security/_authenticate
curl -sS --cacert "$F35_LOCAL/ca.crt" https://127.0.0.1:19935/_security/_authenticate
curl -sS --config "$F35_LOCAL/admin.curl" https://127.0.0.1:19935/_security/_authenticate
```

依次证书错误（curl非零退出）、401、200。错误连接名用自动脚本的TLS socket在同一TCP地址单独改变验证名，排除DNS/端口不通。

## 清理、重做与限制

```bash
python3 labs/f35/lab.py cleanup --out /tmp/f35-reader-cleanup
python3 labs/f35/lab.py down --out /tmp/f35-reader-down
```

cleanup先核对身份/业务资源，撤销本课 `tut-f35-*` 有效key，删除唯一索引 `tut-f35-attractions-v001`（两个alias随之删除），删除本课用户/角色 `tut-f35-reader`；保留ES内部安全与日志索引。down只移除F35容器/网络，保留 `es-framework-f35-n1-data`、`es-framework-f35-n2-data`、`es-framework-f35-certs` 三卷与本机秘密；手工Java自行Ctrl+C。中断后start原卷，再新输出目录run。不要删除安全索引或把本课请求发往其他端点。

最终验收另在明确移除本课三卷、归档原`.local`后，用修正后的脚本重新init/start并走手工路径；不是第三轮自动通过。实际范围与失败尝试见[证据说明](../../review/f35/README.md)。未测跨机器部署、证书到期/热重载、自动轮换、DLS/FLS、租户隔离、HA与性能。
