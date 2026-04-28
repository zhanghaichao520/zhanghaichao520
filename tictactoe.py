import requests
import json
import os
import random
import datetime
import re

LINKS = {
    "Tile 0": "https://linkly.link/2etNk",
    "Tile 1": "https://linkly.link/2etNS",
    "Tile 2": "https://linkly.link/2etOG",
    "Tile 3": "https://linkly.link/2etOj",
    "Tile 4": "https://linkly.link/2etP8",
    "Tile 5": "https://linkly.link/2etPZ",
    "Tile 6": "https://linkly.link/2etPr",
    "Tile 7": "https://linkly.link/2etQB",
    "Tile 8": "https://linkly.link/2etQZ",
}


def to_tile_key(name):
    if name in LINKS:
        return name

    if not isinstance(name, str):
        return None

    match = re.fullmatch(r"\s*(?:tile\s*)?#?\s*([0-8])\s*", name, flags=re.IGNORECASE)
    if match:
        return f"Tile {match.group(1)}"

    return None


def get_tile_count():
    headers = {"User-Agent": "Mozilla/5.0"}
    api_key = os.environ["API_KEY"]
    workspace_id = os.environ["WORKSPACE_ID"]
    url = f"https://app.linklyhq.com/api/v1/workspace/{workspace_id}/links/export?api_key={api_key}"

    r = requests.get(url=url, headers=headers)
    json_data = r.json()
    if not isinstance(json_data, list):
        raise RuntimeError(f"Unexpected Linkly response: {json_data}")

    tile_click_count_new = {key: 0 for key in LINKS}

    for tile in json_data:
        tile_key = to_tile_key(tile.get("name"))
        if tile_key is None:
            continue
        tile_click_count_new[tile_key] = tile.get("clicks_count", 0)

    if not os.path.exists("tile_count.json"):
        tile_click_count_difference = tile_click_count_new.copy()
    else:
        with open("tile_count.json", "r") as f:
            tile_click_counter_old = json.load(f)
            tile_click_count_difference = {
                key: tile_click_count_new[key] - tile_click_counter_old.get(key, 0)
                for key in LINKS
            }

    with open("tile_count.json", "w") as f:
        json.dump(tile_click_count_new, f)

    print(f"Click since last run:{tile_click_count_difference}")
    return tile_click_count_difference


def tictactoe(tile_click_count):
    if not os.path.exists("game_state.json"):
        game_state = {
            "last_played": None,
            "tiles": {
                "Tile 0": None,
                "Tile 1": None,
                "Tile 2": None,
                "Tile 3": None,
                "Tile 4": None,
                "Tile 5": None,
                "Tile 6": None,
                "Tile 7": None,
                "Tile 8": None,
            },
        }

    else:
        with open("game_state.json", "r") as f:
            game_state = json.load(f)

    if game_state["last_played"] is None:
        game_state["last_played"] = random.choice([True, False])

    move = max(
        game_state["tiles"],
        key=lambda x: tile_click_count.get(x, 0)
        if game_state["tiles"][x] is None
        else -1,
    )

    print(game_state)
    print(move)

    game_state["last_played"] = not game_state["last_played"]
    game_state["tiles"][move] = game_state["last_played"]

    print(game_state)

    winner = None
    for row in range(3):
        if (
            game_state["tiles"][f"Tile {3 * row}"] is not None
            and game_state["tiles"][f"Tile {3 * row}"]
            == game_state["tiles"][f"Tile {3 * row + 1}"]
            == game_state["tiles"][f"Tile {3 * row + 2}"]
        ):
            winner = game_state["tiles"][f"Tile {3 * row}"]

    for col in range(3):
        if (
            game_state["tiles"][f"Tile {col}"] is not None
            and game_state["tiles"][f"Tile {col}"]
            == game_state["tiles"][f"Tile {col + 3}"]
            == game_state["tiles"][f"Tile {col + 6}"]
        ):
            winner = game_state["tiles"][f"Tile {col}"]

    if (
        game_state["tiles"]["Tile 0"] is not None
        and game_state["tiles"]["Tile 0"]
        == game_state["tiles"]["Tile 4"]
        == game_state["tiles"]["Tile 8"]
    ):
        winner = game_state["tiles"]["Tile 0"]

    if (
        game_state["tiles"]["Tile 2"] is not None
        and game_state["tiles"]["Tile 2"]
        == game_state["tiles"]["Tile 4"]
        == game_state["tiles"]["Tile 6"]
    ):
        winner = game_state["tiles"]["Tile 2"]

    if winner is None and all(v is not None for k, v in game_state["tiles"].items()):
        winner = "Draw"

    print(winner)

    if winner is not None and os.path.exists("game_state.json"):
        os.remove("game_state.json")
    else:
        with open("game_state.json", "w") as f:
            json.dump(game_state, f)

    return game_state, winner


def update_readme(game_state, winner):
    profile_url = "https://github.com/zhang-haichao"
    asset_base_url = "https://github.com/zhang-haichao/zhang-haichao/blob/master/assets"

    tile_content = {}
    for tile in range(9):
        if game_state["tiles"][f"Tile {tile}"] is None:
            tile_content[f"Tile {tile}"] = (
                f"[![Tile {tile}]({asset_base_url}/{game_state['tiles'][f'Tile {tile}']}.png)]({LINKS[f'Tile {tile}']})"
            )
        else:
            tile_content[f"Tile {tile}"] = (
                f"[![Tile {tile}]({asset_base_url}/{game_state['tiles'][f'Tile {tile}']}.png)]({profile_url})"
            )

    status_line = (
        f'当前轮到: <img src="{asset_base_url}/{not game_state["last_played"]}.png" alt="当前回合" width="32"/>'
        if winner is None
        else f'获胜方: <img src="{asset_base_url}/{winner}.png" alt="获胜方" width="32"/>'
    )

    README = f"""# 你好，我是 张海超！
### 欢迎来到我的 <img src="https://img.icons8.com/color/96/000000/github--v1.png" height="24"/>GitHub 主页

<p align="center">
  <a href="https://zhang-haichao.github.io/"><img src="https://img.icons8.com/color/96/000000/github--v1.png" height="16"/>个人主页</a> ·
  <a href="https://www.linkedin.com/in/%E6%B5%B7%E8%B6%85-%E5%BC%A0-8236312a5/"><img src="https://img.icons8.com/color/96/000000/linkedin-circled.png" height="16"/>LinkedIn</a> ·
  <a href="https://x.com/zhanghaichao961"><img src="https://img.icons8.com/color/96/000000/twitter-circled.png" height="16"/>Twitter</a> ·
  <a href="mailto:zhang_haichao@163.com"><img src="https://img.icons8.com/color/96/000000/email.png" height="16"/>邮箱</a>
</p>

#### 来玩一局井字棋吧
点击一个格子即可参与落子投票  
每小时会自动选择点击次数最多的一步

{status_line}

| Tic | Tac | Toe |
|--|--|--|
| {tile_content["Tile 0"]} | {tile_content["Tile 1"]} | {tile_content["Tile 2"]} |
| {tile_content["Tile 3"]} | {tile_content["Tile 4"]} | {tile_content["Tile 5"]} |
| {tile_content["Tile 6"]} | {tile_content["Tile 7"]} | {tile_content["Tile 8"]} |

## 玩法说明

每个空格都是一个带图片的超链接。点击后会统计点击次数，并跳转回我的 GitHub 主页。  
脚本每次运行时，会在所有可落子位置里选择“新增点击最多”的那一步。  
GitHub Actions 通过定时任务每小时运行一次脚本。  
其余规则与普通井字棋完全一致。  

## 关于我

你好，我是张海超，目前在西交利物浦大学攻读PhD (Recommendation system & LLM)。我曾在阿里巴巴从事广告推荐与数据平台研发，具备大规模系统和高并发场景下的工程实践经验。我的研究主要聚焦 LLM、RAG、推荐去偏与遗忘、可控生成和参数高效适配，相关成果已发表于或投稿于 ICDM、APWEB、SIGIR、IJCAI 等会议。熟悉 Python、Java 与 PyTorch，长期关注“科研创新 + 工业落地”的结合。
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(README)


if __name__ == "__main__":
    tile_click_count = get_tile_count()
    game_state, winner = tictactoe(tile_click_count)
    update_readme(game_state, winner)
