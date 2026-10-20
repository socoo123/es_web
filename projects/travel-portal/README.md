# 行旅 · React + Java 旅游门户（历史草稿）

本目录保存此前未提交的门户草稿，使用 Boot 3 / JDK 21。现行框架篇采用 [travel-search](../travel-search/README.md) 的 Boot 4 / JDK 25 工程，Java 与本机展示壳见 [F07](../../framework/f07.html)；本草稿不计入当前课次交付。

草稿包含首页、景点/酒店表单、房型请求路由，以及 Java 健康 API；没有搜索结果、库存、报价、数据库或 ES 接入。静态预览只展示路由与请求，健康结果需本机工程验证。下文保留旧工程的启动方式。

- [当前课程目录](../../framework/index.html) / [历史案例步骤](labs/f01/README.md)
- [历史验收记录及本次检查范围](review/f01/README.md)

## 锁定依赖与启动

JDK 21；Node 建议 22/24 LTS（至少 22.12，package.json 限定 `<25`）。本轮真实环境为 Oracle JDK 21.0.2、Node 23.11.0、npm 11.7.0。React 19.1.1 / Router 7.18.4 / TypeScript 5.9.3 / Vite 7.3.7 / React 插件 5.0.4 锁定在 package.json + package-lock.json；Spring Boot 3.5.16 管理 Java 依赖；Maven Wrapper 3.3.4 下载 Maven 3.9.11。首次需联网获取依赖。

从仓库根目录开两个终端：

```bash
# A: Java
cd projects/travel-portal/backend
./mvnw -B package
java -jar target/travel-portal-0.1.0.jar
```

```bash
# B: React
cd projects/travel-portal/frontend
npm ci
npm run dev
```

打开 http://127.0.0.1:5173/ 。Java 监听 127.0.0.1:8080；Vite 的 `/api` 开发代理保留路径。本课健康返回 `{"status":"UP","service":"travel-portal","stage":"F01"}`，不探测 ES/数据库。Windows 使用 mvnw.cmd。

## 构建与静态预览

```bash
cd projects/travel-portal/frontend
npm run build
npm run build:lesson
```

`build` 输出本机/未来部署用的 frontend/dist。`build:lesson` 用同一份 React 源码生成仓库的 framework/labs/travel-portal，采用相对资产与 HashRouter，供 Pages HTTP 阅读。lesson 模式明确关闭健康 API 请求，显示“在线静态预览”，不伪造服务健康。生产构建不含 Vite 开发代理，后续需独立配置真实 API 的同源部署。

此草稿不参与当前教程的代码片段同步。静态预览保留在 `framework/labs/travel-portal`，未加入现行课程入口；仓库结构仍用 `node tools/check.mjs` 检查。

## 重做

Ctrl+C 停止各自的终端进程，按上述入口重新启动。当前无索引、数据库或用户状态可删除；回到 `/#/` 并重新填写固定样本即可。框架篇已读状态由教学站单独保存，不影响项目状态。
