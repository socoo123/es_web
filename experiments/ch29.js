/* ch29 · 固定教学端点；本章显式设置、受控数据与清理重做。 */
(function () {
  'use strict';
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function snapshot(n, lines) {
    var id = 'ch29-auth-step-' + n;
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg"><defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
    [[12,72],[100,76],[192,96]].forEach(function (box, i) {
      s += '<rect x="14" y="' + box[0] + '" width="732" height="' + box[1] + '" rx="9" class="' + (i===2?'fig-box-hot fp-pop':'fig-box') + '"/>';
    });
    [84,176].forEach(function (y) { s += '<line x1="380" y1="' + y + '" x2="380" y2="' + (y+16) + '" class="fig-arrow" marker-end="url(#' + id + ')"/>'; });
    var ys=[40,124,148,218,245];
    lines.forEach(function (line,i) { s += '<text x="380" y="' + ys[i] + '" text-anchor="middle" class="' + (i===0?'fig-name':'fig-sub') + '">' + esc(line) + '</text>'; });
    return s + '</svg>';
  }
  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS["ch29-auth-chain"] = {
  "version": 1,
  "id": "ch29-auth-chain",
  "title": "一次普通请求的认证与授权",
  "speed": 2400
,
  steps: [
    { svg: snapshot(1, ["普通请求先认证，再对 Action 授权", "HTTP 头层提取凭据，成功写入 Authentication", "认证前提：本课不配置匿名访问、run-as 或附加认证", "Action 过滤器读取身份，调用 AuthorizationService", "认证失败不会进入本课业务 Handler；授权也可能拒绝"]), note: "普通 HTTP 请求先在头层认证，Action 过滤器随后按动作授权。本课省略 OPTIONS/CORS、内部系统用户、run-as、附加认证和远程传输分支；这些分支不能从主路径自动推断。" },
    { svg: snapshot(2, ["认证器顺序由构造函数确定", "可选插件 → Service Account → OAuth2 → API Key → Realms", "前两类识别 Bearer，API Key 识别 ApiKey", "Basic 在前三类抽不到凭据，返回 CONTINUE", "CONTINUE 也可能表示未成功校验但允许继续"]), note: "Service Account 与 OAuth2 共用 Bearer 前缀，API Key 使用 ApiKey。对本课 Basic 请求，前三类返回 CONTINUE。CONTINUE 不只表示“不是我的凭据”，也可包含未成功的校验信息。" },
    { svg: snapshot(3, ["Realms 抽取并校验 Basic", "UsernamePasswordToken.extractToken 解析用户名密码", "各 Realm 仅处理自己支持的 token；首个成功即停", "默认列表 reserved → file → native", "上次成功 Realm 的缓存可将它提前；LDAP 可认 Basic"]), note: "Basic 属于 Realms 的凭据抽取。默认列表与实际校验顺序分开：成功缓存可重排；LDAP/AD 等用户名密码 Realm 也可支持 Basic。SAML/OIDC 使用自己的认证流程。" },
    { svg: snapshot(4, ["成功身份进入 RBAC", "认证 SUCCESS 后，后续认证器不再尝试", "本课无 run-as；随后 Role 检查 Action 与资源", "alice 的日志 read 允许 GET 文档与搜索", "GET / 需要 cluster:monitor/main，reader 没有该权限"]), note: "同一个 alice 身份：日志文档 GET/搜索返回 200，GET / 返回 403。索引名匹配还要具备对应动作权限；实际索引授权包含资源解析和访问控制，不能只看 checkIndicesAction 布尔值。" },
    { svg: snapshot(5, ["本课三种 401，原因不同", "缺凭据：handleNullToken → missing credentials", "错密码：Realms consumeNullUser → authenticationFailed", "伪造 ApiKey：失败信息累积后仍可走 handleNullToken", "无匿名回退时拒绝；不能把该方法等同于“没有抽过 token”"]), note: "缺头没有身份；错密码的 Basic 已抽出，Realms 关闭 null-token 回退并返回 unable to authenticate user。伪造 ApiKey 已抽出但校验失败，仍可能走 handleNullToken。方法名不能代替完整分支条件。" },
    { svg: snapshot(6, ["401、403 与自查授权", "本课 401 带 Basic + ApiKey 双挑战", "挑战集合取决于 Realm 与 token/API Key 配置", "alice 自查 _authenticate 200：同用户授权分支授予", "无凭据自查仍 401；不是跳过授权，也不授予其他安全 API"]), note: "本课 token service 关闭、API Key 开启，401 带双挑战。alice 的 403 没有挑战；同用户自查由 RBAC 分支授予，所以 GET / 403 与 _authenticate 200 可以同时成立。" },
    { svg: snapshot(7, ["端点与重做前提决定实验结果", "9200：安全关闭，GET / 匿名请求 200", "9201：安全开启，无凭据 GET / 为 401", "关闭安全不构造匿名 superuser；两座集群独立", "点名删除用户、角色、索引，核对后从准备组重做"]), note: "9200 的已测试 _security 路由不注册，具体两个请求返回 400 no handler；这不概括全部路径/方法。9201 保留教学节点供重做，清理仅点名本课资源；Docker down 保留数据卷。" },
  ]
  };
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch29-01-unauth-root"] = {
  "version": 1,
  "id": "ch29-01-unauth-root",
  "title": "实验 1 · 9201 无凭据 GET /:401",
  "method": "GET",
  "path": "/",
  "endpoint": "http://localhost:9201",
  "auth": null,
  "body": null,
  "predict": "先跑 bash docker/start-secure.sh。不带任何凭据,HTTP 状态是 401、403 还是 200?reason 会怎么说?",
  "expect": "401 security_exception，reason 为 missing authentication credentials for REST request [/]. 本课未启用匿名访问，链未得到身份，业务 Handler 未执行。curl -i 可看到 Basic + ApiKey 两个 WWW-Authenticate；这是本课 token service 关闭、API Key 开启的配置结果，其他配置可增加 Bearer 等挑战。"
};
  window.ESEXPERIMENTS["ch29-02-unauth-self"] = {
  "version": 1,
  "id": "ch29-02-unauth-self",
  "title": "实验 2 · 无凭据问「我是谁」:也是 401",
  "method": "GET",
  "path": "/_security/_authenticate",
  "endpoint": "http://localhost:9201",
  "auth": null,
  "body": null,
  "predict": "_authenticate 是「问自己是谁」,不认证也能问吗?",
  "expect": "401 missing authentication credentials。自查 API 也要先认证；认证成功后，RBACEngine.checkSameUserPermissions 可授予该动作，不要求 manage_security。它仍经过授权判断，不是跳过授权层。"
};
  window.ESEXPERIMENTS["ch29-03-auth-root"] = {
  "version": 1,
  "id": "ch29-03-auth-root",
  "title": "实验 3 · 带凭据 GET /:200",
  "method": "GET",
  "path": "/",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "curl -u 会被链上哪一环处理?这次状态码?",
  "expect": "200，version.number=9.4.0、version.lucene_version=10.4.0。Basic 请求在前三类抽不到凭据，交给 Realms；认证成功后 GET / 的 cluster:monitor/main 在授权层获准。"
};
  window.ESEXPERIMENTS["ch29-04-authenticate"] = {
  "version": 1,
  "id": "ch29-04-authenticate",
  "title": "实验 4 · 节点承认的身份:_authenticate",
  "method": "GET",
  "path": "/_security/_authenticate",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "username/roles/authentication_type/realm 各是什么?",
  "expect": "200；username=elastic、roles=[superuser]、authentication_type=realm、authentication_realm.name=reserved。这是用户来源的证据，不能据此推断每次 Realm 都按固定顺序遍历；成功缓存可调整校验顺序。"
};
  window.ESEXPERIMENTS["ch29-05-wrong-password"] = {
  "version": 1,
  "id": "ch29-05-wrong-password",
  "title": "实验 5 · 破坏:错密码——另一种 401",
  "method": "GET",
  "path": "/",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:wrong-password",
  "body": null,
  "predict": "状态码与实验 1 相同吗?reason 与实验 1 相同吗?",
  "expect": "401；reason 为 unable to authenticate user [elastic] for REST request [/]. Realms 已抽出 Basic，setHandleNullToken(false)；支持该 token 的 Realm 均未返回用户后，经 consumeNullUser → authenticationFailed 生成此错误。本例没有到 RBAC。"
};
  window.ESEXPERIMENTS["ch29-06-bogus-apikey"] = {
  "version": 1,
  "id": "ch29-06-bogus-apikey",
  "title": "实验 6 · 破坏:伪造 ApiKey 头,认领它的换了一环",
  "method": "GET",
  "path": "/",
  "endpoint": "http://localhost:9201",
  "auth": null,
  "headers": {
    "Authorization": "ApiKey eHh4Onl5eQ=="
  },
  "body": null,
  "predict": "直接点运行，显式 ApiKey 头会覆盖 Basic。哪个认证器认领？本卡的控制台深链不携带自定义头，等价请求请用正文 curl。",
  "expect": "401；reason 为 unable to authenticate with provided credentials and anonymous access is not allowed for this request。additional_unsuccessful_credentials 指明 API key 与缺失 id xxx。ApiKey 已被抽取但无有效 key，Realms 未抽出 Basic；handleNullToken 不只等于“从未抽过任何凭据”。"
};
  window.ESEXPERIMENTS["ch29-20-secure-usage"] = {
  "version": 1,
  "id": "ch29-20-secure-usage",
  "title": "准备 · 核对 9201 的安全服务开关",
  "method": "GET",
  "path": "/_xpack/usage?filter_path=security.enabled,security.anonymous,security.token_service,security.api_key_service,security.ssl",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "双挑战是不是所有安全节点的固定列表？",
  "expect": "200；security.enabled=true、anonymous.enabled=false、token_service.enabled=false、api_key_service.enabled=true、ssl.http.enabled=false。本课 HTTP 教学配置决定两种挑战。"
};
  window.ESEXPERIMENTS["ch29-21-create-data"] = {
  "version": 1,
  "id": "ch29-21-create-data",
  "title": "准备 · 显式建本课日志索引",
  "method": "PUT",
  "path": "/tut-l29-logs",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1"
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "msg": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "read 用户能自己完成这个创建步骤吗？",
  "expect": "200 acknowledged/shards_acknowledged=true。1 主片、0 副本；严格 keyword mapping、refresh_interval=-1。重复创建返回 400 resource_already_exists_exception；先清理本课索引再重做。"
};
  window.ESEXPERIMENTS["ch29-22-seed-data"] = {
  "version": 1,
  "id": "ch29-22-seed-data",
  "title": "准备 · 管理员写固定 ID 并刷新",
  "method": "PUT",
  "path": "/tut-l29-logs/_doc/1?refresh=true",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": {
    "msg": "security-demo"
  },
  "predict": "alice 的搜索成功是否需要等待默认 refresh 周期？",
  "expect": "首次 201 result=created；同 ID 重复 200 result=updated，文档数仍 1。显式 refresh=true 发布搜索视图，不依赖操作速度。"
};
  window.ESEXPERIMENTS["ch29-07-role"] = {
  "version": 1,
  "id": "ch29-07-role",
  "title": "实验 7 · 建最小角色:只读 tut-l29-*",
  "method": "PUT",
  "path": "/_security/role/tut-l29-reader",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": {
    "cluster": [],
    "indices": [
      {
        "names": [
          "tut-l29-*"
        ],
        "privileges": [
          "read"
        ]
      }
    ]
  },
  "predict": "这个角色能 GET /(cluster 动作)吗?",
  "expect": "200，role.created 首次 true、重复更新 false。仅对匹配名称授予 read；没有 cluster privilege，也没有 write、create_index 或监控权限。"
};
  window.ESEXPERIMENTS["ch29-08-user"] = {
  "version": 1,
  "id": "ch29-08-user",
  "title": "实验 8 · 建 alice,挂上这个角色",
  "method": "PUT",
  "path": "/_security/user/tut-l29-alice",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": {
    "password": "alice-password",
    "roles": [
      "tut-l29-reader"
    ]
  },
  "predict": "alice 的密码会走哪条认证路径?",
  "expect": "200；created 首次 true、重复 false（更新用户和密码）。本课 API 创建的用户属于 native Realm；后续 _authenticate 可核对 authentication_realm.type=native。"
};
  window.ESEXPERIMENTS["ch29-09-alice-403"] = {
  "version": 1,
  "id": "ch29-09-alice-403",
  "title": "实验 9 · alice GET /:403(与实验 1 终于不同码)",
  "method": "GET",
  "path": "/",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": null,
  "predict": "认证过了(密码对),GET / 会 200 吗?",
  "expect": "403 security_exception；reason 包含 action [cluster:monitor/main]、tut-l29-alice 和 effective roles [tut-l29-reader]。认证已成功，但 reader 没有该 cluster 权限。本课此响应不带 WWW-Authenticate。"
};
  window.ESEXPERIMENTS["ch29-10-alice-self"] = {
  "version": 1,
  "id": "ch29-10-alice-self",
  "title": "实验 10 · alice 问「我是谁」:200(checkSameUserPermissions)",
  "method": "GET",
  "path": "/_security/_authenticate",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": null,
  "predict": "alice 连 cluster:monitor/main 都没有,这个 API 会 403 吗?",
  "expect": "200；username=tut-l29-alice、roles=[tut-l29-reader]、authentication_realm.type=native。RBAC 的同用户自查分支授予该动作；不代表她能调用全部 _security API。"
};
  window.ESEXPERIMENTS["ch29-23-alice-get"] = {
  "version": 1,
  "id": "ch29-23-alice-get",
  "title": "对照 · alice 读取本课文档",
  "method": "GET",
  "path": "/tut-l29-logs/_doc/1",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": null,
  "predict": "GET / 是 403，这次文档 GET 呢？",
  "expect": "200 found=true、_source.msg=security-demo。同一用户在匹配资源上的 read 授予此动作；认证成功不等于所有请求都成功。"
};
  window.ESEXPERIMENTS["ch29-24-alice-search"] = {
  "version": 1,
  "id": "ch29-24-alice-search",
  "title": "对照 · alice 搜索本课索引",
  "method": "POST",
  "path": "/tut-l29-logs/_search",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": {
    "query": {
      "match_all": {}
    },
    "track_total_hits": true
  },
  "predict": "已经显式刷新，预计几篇命中？",
  "expect": "200；hits.total.value=1、_shards.failed=0、唯一 _id=1。与 GET / 的 cluster 动作 403 对照。"
};
  window.ESEXPERIMENTS["ch29-11-alice-cat"] = {
  "version": 1,
  "id": "ch29-11-alice-cat",
  "title": "实验 11 · alice 看 _cat/indices:403(index action)",
  "method": "GET",
  "path": "/_cat/indices/tut-l29-logs?h=index",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": null,
  "predict": "已准备的日志索引命中 names，read 是否还包括 CAT 所需的监控动作？",
  "expect": "403 security_exception；本课此请求涉及 indices:monitor/settings/get，read 不足。CAT 可展开成多个内部动作，错误显示哪一个拒绝点不应当作所有版本的固定顺序；只检查本课索引。"
};
  window.ESEXPERIMENTS["ch29-12-alice-put"] = {
  "version": 1,
  "id": "ch29-12-alice-put",
  "title": "实验 12 · alice 建自己的索引:也 403(只有 read)",
  "method": "PUT",
  "path": "/tut-l29-denied",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "predict": "索引名字命中角色的 names 模式 tut-l29-*,能建吗?",
  "expect": "403；reason 包含 indices:admin/create 与 tut-l29-denied。名字匹配 tut-l29-*，但 read 不授予建索引。管理员最后用单名称 HEAD 确认该索引未创建。"
};
  window.ESEXPERIMENTS["ch29-25-alice-write"] = {
  "version": 1,
  "id": "ch29-25-alice-write",
  "title": "破坏 · 名字匹配但 alice 无 write",
  "method": "PUT",
  "path": "/tut-l29-logs/_doc/2?refresh=true",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": {
    "msg": "must-not-write"
  },
  "predict": "names 命中，是否足以写入 ID 2？",
  "expect": "403；reason 含 indices:data/write/index。read 不授予 write；写入失败不应新增文档。API 验收另用管理员确认索引文档数仍为 1。"
};
  window.ESEXPERIMENTS["ch29-26-alice-privileges"] = {
  "version": 1,
  "id": "ch29-26-alice-privileges",
  "title": "对照 · alice 查询自己的权限",
  "method": "POST",
  "path": "/_security/user/_has_privileges",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": {
    "cluster": [
      "monitor"
    ],
    "index": [
      {
        "names": [
          "tut-l29-logs"
        ],
        "privileges": [
          "read",
          "write",
          "create_index"
        ]
      }
    ]
  },
  "predict": "查询自己是否有权限也需要 manage_security 吗？",
  "expect": "200；has_all_requested=false；cluster.monitor=false；index.tut-l29-logs.read=true、write=false、create_index=false。同用户检查可获准，返回 false 不表示查询请求失败。"
};
  window.ESEXPERIMENTS["ch29-27-outside-name"] = {
  "version": 1,
  "id": "ch29-27-outside-name",
  "title": "破坏 · read 不覆盖名称之外",
  "method": "GET",
  "path": "/outside-tut-l29/_search",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": null,
  "predict": "read 用户能搜索一个 names 未匹配的明确索引名吗？",
  "expect": "403；reason 含 indices:data/read/search 与 outside-tut-l29。不创建或删除该外部资源；这里明确名称不在角色范围，不能套用通配符过滤成空集合的行为。"
};
  window.ESEXPERIMENTS["ch29-13-usage"] = {
  "version": 1,
  "id": "ch29-13-usage",
  "title": "实验 13 · 对照 9200:security available 但未 enabled",
  "method": "GET",
  "path": "/_xpack/usage?filter_path=security",
  "endpoint": "http://localhost:9200",
  "body": null,
  "predict": "9200 上 security 是「不存在」还是「存在但关着」?",
  "expect": "200；security.available=true、enabled=false。availability 表示功能在当前许可下可用，enabled 表示配置开关；不能单从 available 判断认证器在运行。",
  "auth": null
};
  window.ESEXPERIMENTS["ch29-14-nohandler"] = {
  "version": 1,
  "id": "ch29-14-nohandler",
  "title": "实验 14 · 对照 9200:_security 路由整组 400",
  "method": "GET",
  "path": "/_security/_authenticate",
  "endpoint": "http://localhost:9200",
  "body": null,
  "predict": "安全关闭时这个请求是 401、403 还是 400?",
  "expect": "400；顶层 error 字符串含 no handler found for uri [/_security/_authenticate] and method [GET]。Security.getRestHandlers 在 enabled=false 时返回空列表；本例路由未注册。不能推广成任意 _security URL / 方法都返回 400。",
  "auth": null
};
  window.ESEXPERIMENTS["ch29-15-nohandler-key"] = {
  "version": 1,
  "id": "ch29-15-nohandler-key",
  "title": "实验 15 · 对照 9200:API key 体系不可用",
  "method": "POST",
  "path": "/_security/api_key",
  "endpoint": "http://localhost:9200",
  "body": {
    "name": "tut-l29-will-fail"
  },
  "predict": "这个 POST 在 9200 上会创建出 key 吗?",
  "expect": "400；顶层 error 字符串含 no handler found for uri [/_security/api_key] and method [POST]。本例不会创建 API Key；本课只测试伪造 key 的失败路径，不创建真实密钥。",
  "auth": null
};
  window.ESEXPERIMENTS["ch29-16-anon-root"] = {
  "version": 1,
  "id": "ch29-16-anon-root",
  "title": "实验 16 · 对照 9200:同一条 GET /,无凭据 200",
  "method": "GET",
  "path": "/",
  "endpoint": "http://localhost:9200",
  "body": null,
  "predict": "和实验 1 一字不差的请求,发到 9200 呢?",
  "expect": "200，返回另一座集群的版本/集群信息。9200 关闭认证授权，不会给匿名请求构造 superuser 身份；这也不等同于启用安全后的匿名用户功能。两座集群的数据和角色互不共享。",
  "auth": null
};
  window.ESEXPERIMENTS["ch29-17-del-user"] = {
  "version": 1,
  "id": "ch29-17-del-user",
  "title": "清理 · 删 alice",
  "method": "DELETE",
  "path": "/_security/user/tut-l29-alice",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "用管理员删除本课 native 用户；删除后同一用户名密码还会得到 403 吗？",
  "expect": "首次 200 found=true；重复删除 404 found=false。删除成功路径会清理相关 Realm 用户缓存；下一卡组核对新请求认证失败。本实验不推断已经在执行的请求或其他凭据的失效时刻。"
};
  window.ESEXPERIMENTS["ch29-18-del-role"] = {
  "version": 1,
  "id": "ch29-18-del-role",
  "title": "清理 · 删角色",
  "method": "DELETE",
  "path": "/_security/role/tut-l29-reader",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "先删用户再删 reader；如果角色已删，再运行这张卡呢？",
  "expect": "首次 200 found=true；重复 404 found=false。这里只清理本课角色；没有级联删除其它用户。重做从准备组重新创建本课数据、角色和用户。"
};
  window.ESEXPERIMENTS["ch29-19-alice-gone"] = {
  "version": 1,
  "id": "ch29-19-alice-gone",
  "title": "清理 · 用已删除的 alice 再试:401 回来了",
  "method": "GET",
  "path": "/",
  "endpoint": "http://localhost:9201",
  "auth": "tut-l29-alice:alice-password",
  "body": null,
  "predict": "密码本身没变(还是 alice-password),这次会 403 还是 401?reason 像实验 1 还是实验 5?",
  "expect": "401；reason 包含 unable to authenticate user [tut-l29-alice]。相同 Basic 仍可解析，用户已删除；所以不是 missing credentials，也没有进入授权。可继续清理数据并重新执行准备组。"
};
  window.ESEXPERIMENTS["ch29-28-delete-data"] = {
  "version": 1,
  "id": "ch29-28-delete-data",
  "title": "清理 · 点名删除本课日志索引",
  "method": "DELETE",
  "path": "/tut-l29-logs",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "已经删掉 alice 和角色，还需要删什么？",
  "expect": "200 acknowledged=true；只删除本课数据。重复清理索引已不存在时返回 404 index_not_found_exception；继续核对 HEAD。"
};
  window.ESEXPERIMENTS["ch29-29-data-gone"] = {
  "version": 1,
  "id": "ch29-29-data-gone",
  "title": "清理 · 单名称 HEAD 确认数据已删",
  "method": "HEAD",
  "path": "/tut-l29-logs",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "状态 404、空响应体，是否是失败？",
  "expect": "404、空 body 是本卡成功预期；只证明 tut-l29-logs 这个索引不存在。"
};
  window.ESEXPERIMENTS["ch29-30-user-gone"] = {
  "version": 1,
  "id": "ch29-30-user-gone",
  "title": "清理 · 管理员确认 native 用户不存在",
  "method": "GET",
  "path": "/_security/user/tut-l29-alice",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "删除后 GET 用户会返回空对象还是 404？",
  "expect": "404，响应 {}；单名称用户查询找不到该用户。这与已删用户凭据请求返回 401 是两种证据。"
};
  window.ESEXPERIMENTS["ch29-31-role-gone"] = {
  "version": 1,
  "id": "ch29-31-role-gone",
  "title": "清理 · 管理员确认 reader 不存在",
  "method": "GET",
  "path": "/_security/role/tut-l29-reader",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "角色不存在时的单名称查询状态？",
  "expect": "404，响应 {}；本课角色已删除。"
};
  window.ESEXPERIMENTS["ch29-32-denied-index-absent"] = {
  "version": 1,
  "id": "ch29-32-denied-index-absent",
  "title": "清理 · 确认拒绝建索引没有产物",
  "method": "HEAD",
  "path": "/tut-l29-denied",
  "endpoint": "http://localhost:9201",
  "auth": "elastic:elastic-password",
  "body": null,
  "predict": "403 的建索引请求是否留下了索引？",
  "expect": "404、空 body；管理员单名称核对 tut-l29-denied 未被创建。"
};
})();
