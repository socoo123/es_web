/* experiments/ch29.js — 第 29 课:安全机制实验 + 认证链 first-match 动画
 * 本课实验固定指明 endpoint:9201 是 docker/start-secure.sh 起的「开安全」节点
 * (elastic / elastic-password),9200 是一直用的「无安全」学习节点——两座集群同屏对照。
 */
(function () {
  'use strict';
  var SECURE = 'http://localhost:9201';
  var PLAIN = 'http://localhost:9200';

  /* ===== 动画:一次 GET / 的两道闸 ===== */
  function rect(x, y, w, h, cls, anim) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="9" class="' + cls + (anim ? ' ' + anim : '') + '"/>';
  }
  function txt(x, y, s, cls, warn, anim) {
    var st = warn ? ' style="fill: rgb(var(--warn))"' : '';
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + (anim ? ' ' + anim : '') + '"' + st + '>' + s + '</text>';
  }
  function defs(id) {
    return '<defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
  }
  function arrow(id, x1, y1, x2, y2) {
    return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" class="fig-arrow" marker-end="url(#' + id + ')"/>';
  }
  function bottom(title, sub) {
    var s = rect(15, 240, 730, 48, 'fig-box-hot', 'fp-pop');
    s += txt(380, 261, title, 'fig-name');
    s += txt(380, 281, sub, 'fig-sub');
    return s;
  }

  /* 步骤 1:两道闸 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('s1');
    s += rect(15, 15, 730, 56, 'fig-box-hot');
    s += txt(380, 38, '安全开启的节点(9201):请求先过认证,再过授权', 'fig-name');
    s += txt(380, 60, '认证问「你是谁」,授权问「你能不能」——两次机会拒绝,状态码不同', 'fig-sub');
    s += rect(15, 88, 355, 76, 'fig-box');
    s += txt(192, 112, '闸 1:认证 authentication', 'fig-name');
    s += txt(192, 136, '从 Authorization 头抽凭据', 'fig-sub');
    s += txt(192, 156, '按固定名单依次尝试', 'fig-sub');
    s += txt(192, 176, '失败 → 401', 'fig-sub', true);
    s += rect(390, 88, 355, 76, 'fig-box');
    s += txt(567, 112, '闸 2:授权 authorization', 'fig-name');
    s += txt(567, 136, '已有 Authentication(是谁)', 'fig-sub');
    s += txt(567, 156, '用角色(RBAC)查这个 action', 'fig-sub');
    s += txt(567, 176, '不过 → 403', 'fig-sub', true);
    s += rect(15, 180, 730, 44, 'fig-box');
    s += txt(380, 200, '认证发生在 handler 跑起来之前(Security.java:先填 ThreadContext,再 authenticate)', 'fig-sub');
    s += txt(380, 217, '认证失败,请求进不了 RestMainAction——body 里连 cluster_name 都没有', 'fig-sub');
    s += bottom('两道闸不是一堵墙:401 = 我还不承认你是谁;403 = 认识你,但你不能做这个', '把 401 当「没权限」用,会完全误读故障');
    return s + '</svg>';
  }

  /* 步骤 2:链的前两环 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('s2');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, 'AuthenticationService 构造函数写死链的成员顺序', 'fig-name');
    s += txt(380, 56, '(可选 Pluggable)→ Service Account → OAuth2 token → API Key → Realms', 'fig-sub');
    s += rect(15, 80, 355, 76, 'fig-box');
    s += txt(192, 104, 'Service Account', 'fig-name');
    s += txt(192, 128, '看 Bearer 前缀,且要能', 'fig-sub');
    s += txt(192, 148, '解析成 service account token', 'fig-sub');
    s += txt(192, 168, 'curl -u 时:抽不到 → CONTINUE', 'fig-sub');
    s += rect(390, 80, 355, 76, 'fig-box');
    s += txt(567, 104, 'OAuth2 token', 'fig-name');
    s += txt(567, 128, '同样看 Bearer(access token)', 'fig-sub');
    s += txt(567, 148, '与上一环共用同一种头', 'fig-sub');
    s += txt(567, 168, '仍抽不到 → CONTINUE', 'fig-sub');
    s += rect(15, 172, 730, 54, 'fig-box');
    s += txt(380, 193, 'CONTINUE 不是失败,是「这不是我的凭据,让下一家」', 'fig-key');
    s += txt(380, 215, '三种状态:SUCCESS 停 / CONTINUE 试下一个 / TERMINATE 整链停', 'fig-sub');
    s += bottom('抽不到凭据返回 null → notHandled()(CONTINUE),不是 401', '所以 curl -u 能安全地跳过前几环');
    return s + '</svg>';
  }

  /* 步骤 3:API Key 与 Realms */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('s3');
    s += rect(15, 15, 355, 76, 'fig-box');
    s += txt(192, 39, 'API Key', 'fig-name');
    s += txt(192, 63, 'Authorization: ApiKey <id:key>', 'fig-sub');
    s += txt(192, 83, '独立前缀,不与 Basic 抢', 'fig-sub');
    s += txt(192, 103, '前缀不对 → CONTINUE', 'fig-sub');
    s += rect(390, 15, 355, 76, 'fig-box-hot', 'fp-pop');
    s += txt(567, 39, 'Realms(链上最后一环)', 'fig-name');
    s += txt(567, 63, '各 Realm 的 token() 抽凭据', 'fig-sub');
    s += txt(567, 83, 'Basic 在这里被抽出来', 'fig-sub');
    s += txt(567, 103, 'UsernamePasswordToken.extractToken', 'fig-sub');
    s += rect(15, 104, 730, 110, 'fig-box');
    s += txt(380, 127, 'Realms 内部再 first-match 一次', 'fig-key');
    s += txt(380, 151, 'realm 顺序:reserved 永远第一(实测 elastic 走 reserved)', 'fig-sub');
    s += txt(380, 171, '然后 file、native;LDAP/SAML/OIDC 也是 Realm,只是认的凭据不是 Basic', 'fig-sub');
    s += txt(380, 191, '同时塞 ApiKey 和 Basic:API Key 在前,Basic 根本不会被问到', 'fig-sub', true);
    s += txt(380, 211, 'first-match 不变量:一次请求只有一个身份', 'fig-sub');
    s += bottom('Basic 不是链上第五个兄弟,是 Realms 里的一种 token()', '旧课 Token→APIKey→LDAP→SAML 海报:漏 Service Account,层级也画错了');
    return s + '</svg>';
  }

  /* 步骤 4:SUCCESS 停链 → RBAC */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('s4');
    s += rect(15, 15, 355, 96, 'fig-box');
    s += txt(192, 39, 'Realms 命中 elastic', 'fig-name');
    s += txt(192, 63, '校验通过 → SUCCESS', 'fig-sub');
    s += txt(192, 83, '迭代停:后面的环不再跑', 'fig-sub');
    s += txt(192, 103, 'Authentication 写进 ThreadContext', 'fig-sub');
    s += rect(390, 15, 355, 96, 'fig-box');
    s += txt(567, 39, '授权是另一次调用', 'fig-name');
    s += txt(567, 63, 'AuthorizationService.authorize', 'fig-sub');
    s += txt(567, 83, '不再看 Authorization 头', 'fig-sub');
    s += txt(567, 103, '看「角色允不允许这个 action」', 'fig-sub');
    s += rect(15, 128, 730, 92, 'fig-box');
    s += txt(380, 152, 'GET / 对应 cluster:monitor/main', 'fig-key');
    s += txt(380, 176, 'superuser 的 checkClusterAction 过 → 200(实测 9201)', 'fig-sub');
    s += txt(380, 196, 'alice 只有 tut-l29-* 的 read → cluster 动作不过 → 403', 'fig-sub', true);
    s += txt(380, 216, 'checkSameUserPermissions 例外:_authenticate 只要认证过就 200', 'fig-sub');
    s += bottom('授权侧多角色是并集;认证侧身份唯一——两个方向的规则相反', 'RBAC 的加法叠在同一个「谁」之上');
    return s + '</svg>';
  }

  /* 步骤 5:401 两兄弟 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('s5');
    s += rect(15, 15, 355, 120, 'fig-box');
    s += txt(192, 39, '无凭据(实验 1)', 'fig-name');
    s += txt(192, 63, '每环都抽不到 token', 'fig-sub');
    s += txt(192, 83, '全 CONTINUE,从未抽出过', 'fig-sub');
    s += txt(192, 103, 'shouldHandleNullToken 仍 true', 'fig-sub');
    s += txt(192, 123, '→ handleNullToken → missingToken', 'fig-sub');
    s += rect(390, 15, 355, 120, 'fig-box');
    s += txt(567, 39, '错密码(实验 5)', 'fig-name');
    s += txt(567, 63, 'Basic 头在,token 已抽出', 'fig-sub');
    s += txt(567, 83, 'Realms 校验失败 → CONTINUE', 'fig-sub');
    s += txt(567, 103, '但 setHandleNullToken(false)', 'fig-sub');
    s += txt(567, 123, '→ authenticationError(failed to…)', 'fig-sub');
    s += rect(15, 152, 730, 72, 'fig-box-hot');
    s += txt(380, 175, '都是 401,文案不同(实测):', 'fig-key');
    s += txt(380, 198, 'missing authentication credentials for REST request [/] vs unable to authenticate user [elastic]…', 'fig-sub');
    s += txt(380, 218, '都带 WWW-Authenticate:Basic realm="security", charset="UTF-8" + ApiKey(双挑战)', 'fig-sub');
    s += bottom('缺头走 handleNullToken,错密码走 authenticationError——同码不同因', '响应文案就是链走到哪一步的指纹');
    return s + '</svg>';
  }

  /* 步骤 6:401 vs 403 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('s6');
    s += rect(15, 15, 355, 120, 'fig-box');
    s += txt(192, 39, '401 认证失败', 'fig-name');
    s += txt(192, 63, '链还没交出 Authentication', 'fig-sub');
    s += txt(192, 83, 'rest status UNAUTHORIZED', 'fig-sub');
    s += txt(192, 103, '带 WWW-Authenticate 挑战', 'fig-sub');
    s += txt(192, 123, '「请给凭据」', 'fig-sub');
    s += rect(390, 15, 355, 120, 'fig-box');
    s += txt(567, 39, '403 授权失败', 'fig-name');
    s += txt(567, 63, '身份就位,角色不过', 'fig-sub');
    s += txt(567, 83, 'rest status FORBIDDEN', 'fig-sub');
    s += txt(567, 103, '通常不挑战(已表明身份)', 'fig-sub');
    s += txt(567, 123, '「认识你,但你不能」', 'fig-sub');
    s += rect(15, 152, 730, 72, 'fig-box');
    s += txt(380, 175, '实测 alice(实验 9):403', 'fig-key');
    s += txt(380, 198, 'action [cluster:monitor/main] is unauthorized for user [tut-l29-alice]', 'fig-sub');
    s += txt(380, 218, 'with effective roles [tut-l29-reader] —— 分清这两条,排障少走一半弯路', 'fig-sub');
    s += bottom('两个异常工厂:Exceptions.authenticationError → 401;authorizationError → 403', 'alice 的 403 文案还带着 effective roles——授权看的是角色');
    return s + '</svg>';
  }

  /* 步骤 7:两座集群 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('s7');
    s += rect(15, 15, 355, 120, 'fig-box');
    s += txt(192, 39, '9200:安全关闭(本站默认)', 'fig-name');
    s += txt(192, 63, 'GET / 无凭据 → 200', 'fig-sub');
    s += txt(192, 83, '两道闸整个不存在', 'fig-sub');
    s += txt(192, 103, '_security/* → 400 no handler', 'fig-sub');
    s += txt(192, 123, '路由根本没注册', 'fig-sub');
    s += rect(390, 15, 355, 120, 'fig-box-hot');
    s += txt(567, 39, '9201:安全开启(第 29 课)', 'fig-name');
    s += txt(567, 63, 'GET / 无凭据 → 401', 'fig-sub');
    s += txt(567, 83, '_security/_authenticate → 身份/角色', 'fig-sub');
    s += txt(567, 103, '角色/用户/API key 全套可用', 'fig-sub');
    s += txt(567, 123, 'elastic / elastic-password', 'fig-sub');
    s += rect(15, 152, 730, 72, 'fig-box');
    s += txt(380, 175, '同一份 9.4.0 镜像,一个开关两种世界', 'fig-key');
    s += txt(380, 198, '对照实验 13-16:_xpack/usage 里 security.available=true 而 enabled=false(9200)', 'fig-sub');
    s += txt(380, 218, '别忘了 9200 上还有 destructive_requires_name=true 那道第 28 课的默认闸', 'fig-sub');
    s += bottom('安全不是插件海报,是一组可指认的开关与状态码', '实验全部跑完后:docker compose -f docker/docker-compose-secure.yml down 收起 9201');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch29-auth-chain'] = {
    version: 1,
    id: 'ch29-auth-chain',
    title: '一次 GET / 的两道闸',
    speed: 2400,
    steps: [
      { svg: step1(), note: '两道闸:认证问「你是谁」(Authorization 头 → 固定名单依次尝试),授权问「你能不能」(角色查 action)。认证在 handler 之前——失败时连 RestMainAction 都没跑,body 里没有 cluster_name。' },
      { svg: step2(), note: '链顺序写死在 AuthenticationService 构造函数:(可选 Pluggable)→ Service Account → OAuth2 → API Key → Realms。CONTINUE 不是失败,是「不是我的凭据」;抽不到返回 notHandled(),所以 curl -u 能安全跳过前几环。' },
      { svg: step3(), note: 'API Key 认独立前缀;Basic 藏在最后一环 Realms 的 UsernamePasswordToken.extractToken 里——头不是 Basic 前缀就返回 null。Realms 内部再 first-match:reserved 永远第一(实测 elastic 走 reserved)。' },
      { svg: step4(), note: 'Realms 命中 → SUCCESS 停链,Authentication 写进 ThreadContext;授权是另一次调用:GET / 是 cluster:monitor/main,superuser 过 → 200;alice 只有 read → 403;_authenticate 靠 checkSameUserPermissions 例外,认证过就 200。' },
      { svg: step5(), note: '401 两兄弟:无凭据(从未抽出 token)走 handleNullToken → missing authentication credentials;错密码(token 已抽出、setHandleNullToken(false))走 authenticationError → unable to authenticate user。同码不同因,都带双 WWW-Authenticate 挑战。' },
      { svg: step6(), note: '401 vs 403:两个异常工厂——authenticationError(UNAUTHORIZED,带挑战)与 authorizationError(FORBIDDEN,不挑战)。实测 alice 的 403 文案还带着 effective roles,授权看的是角色。' },
      { svg: step7(), note: '两座集群对照:9200 安全关闭,GET / 无凭据 200、_security 整组 400 no handler;9201 安全开启,全套身份体系可用。同一个镜像、一个开关两种世界——安全关闭不等于路由还在但放行。' }
    ]
  };

  /* ===== 实验(全部显式指明 endpoint,不随全局端点漂移) ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch29-01-unauth-root'] = {
    version: 1, id: 'ch29-01-unauth-root',
    title: '实验 1 · 9201 无凭据 GET /:401',
    method: 'GET', path: '/',
    endpoint: SECURE, auth: null,
    body: null,
    predict: '先跑 bash docker/start-secure.sh。不带任何凭据,HTTP 状态是 401、403 还是 200?reason 会怎么说?',
    expect: '401 + missing authentication credentials for REST request [/]——四环全 CONTINUE 且从未抽出 token,handleNullToken → DefaultAuthenticationFailureHandler.missingToken。响应头还有两个挑战 WWW-Authenticate: Basic realm="security", charset="UTF-8" 和 ApiKey(runner 只显示 body,curl -i 可见头)。body 里没有 cluster_name:认证在 RestMainAction 之前就停了。'
  };

  window.ESEXPERIMENTS['ch29-02-unauth-self'] = {
    version: 1, id: 'ch29-02-unauth-self',
    title: '实验 2 · 无凭据问「我是谁」:也是 401',
    method: 'GET', path: '/_security/_authenticate',
    endpoint: SECURE, auth: null,
    body: null,
    predict: '_authenticate 是「问自己是谁」,不认证也能问吗?',
    expect: '仍 401、仍是 missing credentials。它免的是<strong>授权</strong>(checkSameUserPermissions:认证过即可),不免<strong>认证</strong>——节点还不知道你是谁,就不存在「自己」。两道闸的顺序没有例外入口。'
  };

  window.ESEXPERIMENTS['ch29-03-auth-root'] = {
    version: 1, id: 'ch29-03-auth-root',
    title: '实验 3 · 带凭据 GET /:200',
    method: 'GET', path: '/',
    endpoint: SECURE, auth: 'elastic:elastic-password',
    body: null,
    predict: 'curl -u 会被链上哪一环处理?这次状态码?',
    expect: '200,带回 name/cluster_name/tagline。前三环(Service Account/OAuth2/API Key)见不到 Bearer / ApiKey 前缀全 CONTINUE,Realms 的 UsernamePasswordToken 抽出 Basic → 校验 SUCCESS;随后 RBAC:GET / 是 cluster:monitor/main,superuser 过。预测 403 的是把认证授权混成一件事。'
  };

  window.ESEXPERIMENTS['ch29-04-authenticate'] = {
    version: 1, id: 'ch29-04-authenticate',
    title: '实验 4 · 节点承认的身份:_authenticate',
    method: 'GET', path: '/_security/_authenticate',
    endpoint: SECURE, auth: 'elastic:elastic-password',
    body: null,
    predict: 'username/roles/authentication_type/realm 各是什么?',
    expect: 'username=elastic、roles=[superuser]、authentication_type=realm、authentication_realm.name=reserved——内置用户走 reserved realm(Realm 列表里永远第一),不是 file/native。这就是图 1 从「Realms 命中」到「RBAC 允许」之后,节点承认的那份 Authentication。'
  };

  window.ESEXPERIMENTS['ch29-05-wrong-password'] = {
    version: 1, id: 'ch29-05-wrong-password',
    title: '实验 5 · 破坏:错密码——另一种 401',
    method: 'GET', path: '/',
    endpoint: SECURE, auth: 'elastic:wrong-password',
    body: null,
    predict: '状态码与实验 1 相同吗?reason 与实验 1 相同吗?',
    expect: '仍 401,但 reason 变成 unable to authenticate user [elastic] for REST request [/]——Basic 头在,UsernamePasswordToken.extractToken 已抽出 user:pass(所以走过了 extractToken),Realms 校验失败 CONTINUE 且 setHandleNullToken(false),于是走 authenticationError 而非 missingToken。同码不同因:文案就是链走到哪一步的指纹。'
  };

  window.ESEXPERIMENTS['ch29-06-bogus-apikey'] = {
    version: 1, id: 'ch29-06-bogus-apikey',
    title: '实验 6 · 破坏:伪造 ApiKey 头,认领它的换了一环',
    method: 'GET', path: '/',
    endpoint: SECURE, auth: null,
    headers: { Authorization: 'ApiKey eHh4Onl5eQ==' },
    body: null,
    predict: 'ApiKey 前缀会被哪一环认领?错误文案与实验 5 一样吗?',
    expect: '401 security_exception:unable to authenticate with provided credentials and anonymous access is not allowed——这次认领头的是 ApiKeyAuthenticator(第 4 环),id 查无此 key;与实验 5 的 unable to authenticate user 不同,这条没到用户名层面。真实 API key 流程:用 elastic 创建 _security/api_key,把返回的 encoded 填进 ApiKey 头(_authenticate 会显示 authentication_type: api_key)。'
  };

  window.ESEXPERIMENTS['ch29-07-role'] = {
    version: 1, id: 'ch29-07-role',
    title: '实验 7 · 建最小角色:只读 tut-l29-*',
    method: 'PUT', path: '/_security/role/tut-l29-reader',
    endpoint: SECURE, auth: 'elastic:elastic-password',
    body: { indices: [{ names: ['tut-l29-*'], privileges: ['read'] }] },
    predict: '这个角色能 GET /(cluster 动作)吗?',
    expect: '{role:{created:true}}。不能:indices 权限只覆盖名字匹配的索引上的 read;没有任何 cluster privilege——下一个实验的 403 就来自这里。RBAC 的单位是 privilege,不是「能不能连」。'
  };

  window.ESEXPERIMENTS['ch29-08-user'] = {
    version: 1, id: 'ch29-08-user',
    title: '实验 8 · 建 alice,挂上这个角色',
    method: 'PUT', path: '/_security/user/tut-l29-alice',
    endpoint: SECURE, auth: 'elastic:elastic-password',
    body: { password: 'alice-password', roles: ['tut-l29-reader'] },
    predict: 'alice 的密码会走哪条认证路径?',
    expect: '{created:true}。和 elastic 一样走 Basic → Realms,只是用户存在 native realm(而非 reserved);认证链对「哪个用户」无感——它只管「这一环认不认这种凭据」。用户-角色绑定是授权侧的输入。'
  };

  window.ESEXPERIMENTS['ch29-09-alice-403'] = {
    version: 1, id: 'ch29-09-alice-403',
    title: '实验 9 · alice GET /:403(与实验 1 终于不同码)',
    method: 'GET', path: '/',
    endpoint: SECURE, auth: 'tut-l29-alice:alice-password',
    body: null,
    predict: '认证过了(密码对),GET / 会 200 吗?',
    expect: '403:action [cluster:monitor/main] is unauthorized for user [tut-l29-alice] with effective roles [tut-l29-reader]——认证成功、身份就位,是 RBAC 说不。对照实验 1 的 401:那边节点还不知道你是谁;这边认识你,但你不能。文案里的 effective roles 就是授权侧的输入。'
  };

  window.ESEXPERIMENTS['ch29-10-alice-self'] = {
    version: 1, id: 'ch29-10-alice-self',
    title: '实验 10 · alice 问「我是谁」:200(checkSameUserPermissions)',
    method: 'GET', path: '/_security/_authenticate?filter_path=username,roles',
    endpoint: SECURE, auth: 'tut-l29-alice:alice-password',
    body: null,
    predict: 'alice 连 cluster:monitor/main 都没有,这个 API 会 403 吗?',
    expect: '200:{username: tut-l29-alice, roles: [tut-l29-reader]}——checkSameUserPermissions 例外:「问自己是谁」这类动作只要认证过就授予,不必 manage_security。它免授权不免认证(对照实验 2 的 401)。'
  };

  window.ESEXPERIMENTS['ch29-11-alice-cat'] = {
    version: 1, id: 'ch29-11-alice-cat',
    title: '实验 11 · alice 看 _cat/indices:403(index action)',
    method: 'GET', path: '/_cat/indices?h=index',
    endpoint: SECURE, auth: 'tut-l29-alice:alice-password',
    body: null,
    predict: '这是 index 侧动作,文案里的 action 名会是什么?',
    expect: '403:action [indices:monitor/settings/get] is unauthorized…——授权按 action 名分叉:cluster 动作走 checkClusterAction,index 动作走 checkIndicesAction(_cat/indices 展开成多个 index 级 action)。同一角色在两类 action 上的命运可以不同。'
  };

  window.ESEXPERIMENTS['ch29-12-alice-put'] = {
    version: 1, id: 'ch29-12-alice-put',
    title: '实验 12 · alice 建自己的索引:也 403(只有 read)',
    method: 'PUT', path: '/tut-l29-logs',
    endpoint: SECURE, auth: 'tut-l29-alice:alice-password',
    body: null,
    predict: '索引名字命中角色的 names 模式 tut-l29-*,能建吗?',
    expect: '403:action [indices:admin/create] is unauthorized … on indices [tut-l29-logs]——名字命中只是「进门资格」,能不能做还要看 privileges 列表里有没有 create。role = names × privileges 的组合,缺一不可。'
  };

  window.ESEXPERIMENTS['ch29-13-usage'] = {
    version: 1, id: 'ch29-13-usage',
    title: '实验 13 · 对照 9200:security available 但未 enabled',
    method: 'GET', path: '/_xpack/usage?filter_path=security',
    endpoint: PLAIN,
    body: null,
    predict: '9200 上 security 是「不存在」还是「存在但关着」?',
    expect: '{security:{available:true, enabled:false}}——功能在发行版里(x-pack 默认带),开关没打开。一座集群的安全状态可以用这个 API 一句话确认,比猜端口行为可靠。'
  };

  window.ESEXPERIMENTS['ch29-14-nohandler'] = {
    version: 1, id: 'ch29-14-nohandler',
    title: '实验 14 · 对照 9200:_security 路由整组 400',
    method: 'GET', path: '/_security/_authenticate',
    endpoint: PLAIN,
    body: null,
    predict: '安全关闭时这个请求是 401、403 还是 400?',
    expect: '400:no handler found for uri [/_security/_authenticate] and method [GET]——安全关闭时整组 _security handler 不注册(第 7 课的未知路口径,与 ch26 实验里 GET 不存在的管道同款)。「关着」不是「路由还在但放行」。'
  };

  window.ESEXPERIMENTS['ch29-15-nohandler-key'] = {
    version: 1, id: 'ch29-15-nohandler-key',
    title: '实验 15 · 对照 9200:API key 体系不可用',
    method: 'POST', path: '/_security/api_key',
    endpoint: PLAIN,
    body: { name: 'tut-l29-will-fail' },
    predict: '这个 POST 在 9200 上会创建出 key 吗?',
    expect: '400 no handler found for uri [/_security/api_key]——API key 的创建/校验/失效全挂在安全特性上,开关不开整套不存在。想在 9200 上复现实验 6 的 ApiKey 流程是不可能的;那边只有 destructive_requires_name 这类与凭据无关的默认闸(第 28 课)。'
  };

  window.ESEXPERIMENTS['ch29-16-anon-root'] = {
    version: 1, id: 'ch29-16-anon-root',
    title: '实验 16 · 对照 9200:同一条 GET /,无凭据 200',
    method: 'GET', path: '/',
    endpoint: PLAIN,
    body: null,
    predict: '和实验 1 一字不差的请求,发到 9200 呢?',
    expect: '200 + cluster 信息——两道闸整个不存在,人人都是匿名 superuser。同一条命令、两座集群、三种结局(401/200/200):排障时先弄清「我连的是哪个开关状态」,再看代码。'
  };

  window.ESEXPERIMENTS['ch29-17-del-user'] = {
    version: 1, id: 'ch29-17-del-user',
    title: '清理 · 删 alice',
    method: 'DELETE', path: '/_security/user/tut-l29-alice',
    endpoint: SECURE, auth: 'elastic:elastic-password',
    body: null,
    predict: '删用户会影响正在用它的连接吗?',
    expect: '{found:true}。已建立的认证缓存/凭据可能短暂残留,但下一次完整认证必然失败(下一个实验验证)。清理身份对象用 superuser 删 superuser 造的东西——与第 28 课「先索引后策略」同理,对象之间有引用与属主关系。'
  };

  window.ESEXPERIMENTS['ch29-18-del-role'] = {
    version: 1, id: 'ch29-18-del-role',
    title: '清理 · 删角色',
    method: 'DELETE', path: '/_security/role/tut-l29-reader',
    endpoint: SECURE, auth: 'elastic:elastic-password',
    body: null,
    predict: '角色删了,引用它的用户(刚删过)会残留坏引用吗?',
    expect: '{found:true}。alice 已在上一条删掉;若先删角色后删用户,用户也只是带着一个空角色名,授权时按无权限处理——RBAC 对缺失角色的容忍是「没有权限」,不是报错。'
  };

  window.ESEXPERIMENTS['ch29-19-alice-gone'] = {
    version: 1, id: 'ch29-19-alice-gone',
    title: '清理 · 用已删除的 alice 再试:401 回来了',
    method: 'GET', path: '/',
    endpoint: SECURE, auth: 'tut-l29-alice:alice-password',
    body: null,
    predict: '密码本身没变(还是 alice-password),这次会 403 还是 401?reason 像实验 1 还是实验 5?',
    expect: '401 unable to authenticate user [tut-l29-alice]——像实验 5(错密码),不像实验 1:Basic 头在,token 已抽出,只是用户查无此人。三种拒绝各归其位:缺凭据 401、认不出 401、认出了不许 403。收尾:docker compose -f docker/docker-compose-secure.yml down 可把 9201 整个收起(数据卷保留)。'
  };
})();
