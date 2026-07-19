<<<<<<< HEAD
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

API_ROOT = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")


def repository_context(config):
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    context_owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    context_repository = ""
    if "/" in repository:
        context_owner, context_repository = repository.split("/", 1)

    owner = config["owner"] or context_owner
    if not owner:
        raise RuntimeError("无法确定 GitHub 用户名，请在配置中设置 owner。")
    return owner, config["profile_repository"] or context_repository or owner


def github_json(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-profile-language-donut",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(f"{API_ROOT}{path}", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API 请求失败（{error.code}）：{path}\n{detail}"
        ) from error


def public_repositories(owner, profile_repository, config):
    repositories = []
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {"per_page": 100, "page": page, "type": "owner", "sort": "updated"}
        )
        batch = github_json(f"/users/{owner}/repos?{query}")
        repositories.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    excluded = set(config["excluded_repositories"])
    excluded.add(profile_repository)
    return [
        repository["name"]
        for repository in repositories
        if repository["name"] not in excluded
        and (config["include_archived"] or not repository.get("archived", False))
        and (config["include_forks"] or not repository.get("fork", False))
    ]


def language_totals(owner, profile_repository, config):
    totals = Counter()
    for repository in public_repositories(owner, profile_repository, config):
        totals.update(github_json(f"/repos/{owner}/{repository}/languages"))
    if not totals:
        raise RuntimeError("GitHub 没有返回可用于生成图表的语言数据。")
    return totals
=======
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

API_ROOT = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")


def repository_context(config):
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    context_owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    context_repository = ""
    if "/" in repository:
        context_owner, context_repository = repository.split("/", 1)

    owner = config["owner"] or context_owner
    if not owner:
        raise RuntimeError("无法确定 GitHub 用户名，请在配置中设置 owner。")
    return owner, config["profile_repository"] or context_repository or owner


def github_json(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-profile-language-donut",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(f"{API_ROOT}{path}", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API 请求失败（{error.code}）：{path}\n{detail}"
        ) from error


def public_repositories(owner, profile_repository, config):
    repositories = []
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {"per_page": 100, "page": page, "type": "owner", "sort": "updated"}
        )
        batch = github_json(f"/users/{owner}/repos?{query}")
        repositories.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    excluded = set(config["excluded_repositories"])
    excluded.add(profile_repository)
    return [
        repository["name"]
        for repository in repositories
        if repository["name"] not in excluded
        and (config["include_archived"] or not repository.get("archived", False))
        and (config["include_forks"] or not repository.get("fork", False))
    ]


def language_totals(owner, profile_repository, config):
    totals = Counter()
    for repository in public_repositories(owner, profile_repository, config):
        totals.update(github_json(f"/repos/{owner}/{repository}/languages"))
    if not totals:
        raise RuntimeError("GitHub 没有返回可用于生成图表的语言数据。")
    return totals
>>>>>>> 23b6d9dccb1f19b39219aee4f0a0b2a3b8f1939d
