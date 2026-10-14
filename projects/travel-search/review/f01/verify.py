#!/usr/bin/env python3
"""作者验收：执行教程中的 shell 文件，核对实际输出；不参与读者实验。"""
import datetime
import hashlib
import json
import pathlib
import socket
import subprocess
import urllib.request

PROJECT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:19200"
INDEX = "tut-f01-attractions"
COMPOSE = ["docker", "compose", "-f", "infra/single-node/compose.yaml"]


def shell(args):
    result = subprocess.run(args, cwd=PROJECT, capture_output=True, text=True, timeout=240)
    if result.returncode:
        raise RuntimeError(f"{args}: {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result


def objects(raw):
    decoder = json.JSONDecoder()
    result = []
    while raw.strip():
        item, end = decoder.raw_decode(raw.lstrip())
        raw = raw.lstrip()[end:]
        result.append(item)
    return result


def step(name, round_no):
    result = shell(["bash", f"labs/f01/{name}.sh"])
    (RAW / f"round-{round_no}-{name}.txt").write_text(result.stdout + result.stderr)
    return objects(result.stdout)


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as response:
        assert response.status == 200
        return json.load(response)


def assert_search(body):
    assert not body["timed_out"] and body["_shards"]["failed"] == 0
    assert body["hits"]["total"] == {"value": 1, "relation": "eq"}
    assert [h["_id"] for h in body["hits"]["hits"]] == ["a-hz-xihu"]
    assert body["hits"]["hits"][0]["_source"]["name"] == "杭州西湖"


def run():
    # 若专用数据卷中已有本课索引，拒绝自动删：先人工点名清理后重新验收。
    with socket.socket() as sock:
        assert sock.connect_ex(("127.0.0.1", 19299)) != 0, "错误端口已有监听服务"
    shell(COMPOSE + ["up", "-d"])
    shell(["bash", "infra/single-node/wait.sh"])
    assert get("/")["cluster_name"] == "travel-search-lab"
    indices = get("/_cat/indices?format=json&h=index")
    assert all(x["index"] != INDEX for x in indices), "先手工点名清理本课索引"
    rounds = []
    for round_no in [1, 2]:
        print(f"round {round_no}: C01 启动/写查", flush=True)
        info, nodes, cluster = step("01-observe", round_no)
        assert info["version"]["number"] == "9.4.0"
        assert len(nodes) == 1 and nodes[0]["name"] == "travel-search-01"
        assert cluster["number_of_nodes"] == 1 and cluster["status"] == "green"
        created, health = step("02-create", round_no)
        assert created["acknowledged"] and created["shards_acknowledged"]
        assert not health["timed_out"] and health["status"] == "green"
        assert health["active_primary_shards"] == health["active_shards"] == 1
        write, = step("03-write", round_no)
        assert write["result"] == "created" and write["_version"] == 1
        refresh, search = step("04-search", round_no)
        assert refresh["_shards"]["failed"] == 0
        assert_search(search)
        mapping, count, doc = step("05-inspect", round_no)
        assert mapping[INDEX]["mappings"]["properties"]["name"] == {"type": "text", "analyzer": "standard"}
        assert count["count"] == 1 and doc["found"]
        assert doc["_source"] == json.loads((PROJECT / "data/f01/xihu.json").read_text())
        settings = get(f"/{INDEX}/_settings")[INDEX]["settings"]["index"]
        assert settings["number_of_shards"] == "1" and settings["number_of_replicas"] == "0"

        print(f"round {round_no}: C02 错误端口/停机/恢复", flush=True)
        errors = shell(["bash", "labs/f01/08-connection-errors.sh"])
        assert errors.stdout.count("curl exit=7") == 2
        assert errors.stderr.count("curl: (7)") == 2
        recovered = get(f"/{INDEX}/_search?q=name:%E8%A5%BF%E6%B9%96")
        assert_search(recovered)
        (RAW / f"round-{round_no}-connection-errors.txt").write_text(errors.stdout + errors.stderr)

        print(f"round {round_no}: C03 索引已存在/固定 ID 覆盖", flush=True)
        existing, = step("06-existing-index", round_no)
        assert existing["status"] == 400
        assert existing["error"]["type"] == "resource_already_exists_exception"
        update, refresh_again, count_again, doc_again = step("07-write-again", round_no)
        assert update["result"] == "updated" and update["_version"] == 2
        assert refresh_again["_shards"]["failed"] == 0
        assert count_again["count"] == 1 and doc_again["_version"] == 2
        cleaned, = step("cleanup", round_no)
        assert cleaned["acknowledged"]
        assert all(x["index"] != INDEX for x in get("/_cat/indices?format=json&h=index"))
        rounds.append({"round": round_no, "cases": {"f01-c01": "passed", "f01-c02": "passed", "f01-c03": "passed"},
                       "info": info, "nodes": nodes, "cluster": cluster, "created": created,
                       "index_health": health, "settings": settings, "write": write,
                       "refresh": refresh, "search": search, "mapping": mapping, "count": count,
                       "document": doc, "connection_exit_codes": [7, 7], "recovered_search": recovered,
                       "existing_index": existing, "rewrite": update, "count_after_rewrite": count_again,
                       "document_after_rewrite": doc_again, "cleanup": cleaned})
    jvm = get("/_nodes/jvm")
    result = {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "scope": "F01 shell commands, real ES; no Java/Boot, plugins, CDC or multi-node acceptance",
              "endpoint": BASE, "image_digest": shell(["docker", "image", "inspect",
                  "docker.elastic.co/elasticsearch/elasticsearch:9.4.0", "--format", "{{json .RepoDigests}}"] ).stdout.strip(),
              "docker_version": shell(["docker", "version", "--format", "{{.Server.Version}}"] ).stdout.strip(),
              "compose_version": shell(["docker", "compose", "version", "--short"] ).stdout.strip(),
              "container_memory_bytes": 1073741824, "heap_bytes": 536870912,
              "jvm": [{"version": n["jvm"]["version"],
                       "using_bundled_jdk": n["jvm"]["using_bundled_jdk"]} for n in jvm["nodes"].values()],
              "rounds": rounds, "final_state": "F01 index absent; own container stopped, volume retained",
              "source_sha256": {str(p.relative_to(PROJECT)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for folder in ["infra/single-node", "labs/f01", "data/f01", "search/f01"]
                  for p in sorted((PROJECT / folder).glob("*")) if p.is_file()}}
    (HERE / "es-review.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    # 正文使用首轮实际响应，摘录只选字段、不改值；搜索保留完整响应。
    observed = rounds[0]
    outputs = {
        "node": {"name": observed["info"]["name"], "cluster_name": observed["info"]["cluster_name"],
                 "version": {"number": observed["info"]["version"]["number"]}, "nodes": observed["nodes"]},
        "index-created": {"create": observed["created"], "index_health": {key: observed["index_health"][key]
             for key in ["status", "timed_out", "active_primary_shards", "active_shards"]}},
        "write": {key: observed["write"][key] for key in ["_index", "_id", "_version", "result"]},
        "search": observed["search"],
        "existing-index": {"error": {key: observed["existing_index"]["error"][key] for key in ["type", "reason"]},
                           "status": observed["existing_index"]["status"]},
        "rewrite": {"write": {key: observed["rewrite"][key] for key in ["_id", "_version", "result"]},
                    "count_after_refresh": observed["count_after_rewrite"]["count"]}
    }
    (HERE / "outputs").mkdir(exist_ok=True)
    for name, body in outputs.items():
        (HERE / "outputs" / f"{name}.json").write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n")
    print("F01 3 案例 × 2 轮通过，索引已清理", flush=True)


if __name__ == "__main__":
    try:
        run()
    finally:
        shell(COMPOSE + ["stop", "es"])
