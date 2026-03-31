import requests
import json
import os
import random
import datetime

TARGET_URL = "https://github.com/zhanghaichao520"
LINKS = {f"Tile {i}": TARGET_URL for i in range(9)}

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "zhanghaichao520")
PROFILE_REPO = os.getenv("PROFILE_REPO", GITHUB_USERNAME)
PROFILE_NAME = os.getenv("PROFILE_NAME", "张海超")
PROFILE_EMAIL = os.getenv("PROFILE_EMAIL", "zhang_haichao@163.com")
PROFILE_LINKEDIN = os.getenv(
    "PROFILE_LINKEDIN",
    "https://www.linkedin.com/in/%E6%B5%B7%E8%B6%85-%E5%BC%A0-8236312a5/",
)
PROFILE_TWITTER = os.getenv("PROFILE_TWITTER", "https://x.com/zhanghaichao961")
PROFILE_URL = f"https://github.com/{GITHUB_USERNAME}"
REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{PROFILE_REPO}"
ASSET_BASE_URL = f"{REPO_URL}/blob/master/assets"


def get_tile_count():
    headers = {"User-Agent": "Mozilla/5.0"}
    api_key = os.environ["API_KEY"]
    workspace_id = os.environ["WORKSPACE_ID"]
    url = f"https://app.linklyhq.com/api/v1/workspace/{workspace_id}/links/export?api_key={api_key}"

    r = requests.get(url=url, headers=headers)
    json_data = r.json()

    tile_click_count_new = {}
    tile_click_count_difference = {}

    for tile in json_data:
        tile_click_count_new[tile["name"]] = tile["clicks_count"]

    if not os.path.exists("tile_count.json"):
        tile_click_count_difference = tile_click_count_new.copy()
    else:
        with open("tile_count.json", "r") as f:
            tile_click_counter_old = json.load(f)
            tile_click_count_difference = {
                key: tile_click_count_new[key] - tile_click_counter_old.get(key, 0)
                for key in tile_click_count_new
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
        tile_click_count,
        key=lambda x: tile_click_count[x] if game_state["tiles"][x] is None else -1,
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
    tile_content = {}
    for tile in range(9):
        if game_state["tiles"][f"Tile {tile}"] is None:
            tile_content[f"Tile {tile}"] = (
                f"[![Tile {tile}]({ASSET_BASE_URL}/{game_state['tiles'][f'Tile {tile}']}.png)]({LINKS[f'Tile {tile}']})"
            )
        else:
            tile_content[f"Tile {tile}"] = (
                f"[![Tile {tile}]({ASSET_BASE_URL}/{game_state['tiles'][f'Tile {tile}']}.png)]({PROFILE_URL})"
            )

    status_line = (
        f'当前轮到: <img src="{ASSET_BASE_URL}/{not game_state["last_played"]}.png" alt="当前回合" width="32"/>'
        if winner is None
        else f'获胜方: <img src="{ASSET_BASE_URL}/{winner}.png" alt="获胜方" width="32"/>'
    )

    README = f"""# 你好，我是 {PROFILE_NAME}！
### 欢迎来到我的 <img src="https://img.icons8.com/color/96/000000/github--v1.png" height="24"/>GitHub 主页

<p align="center">
  <a href="{PROFILE_URL}"><img src="https://img.icons8.com/color/96/000000/github--v1.png" height="16"/>GitHub 主页</a> ·
  <a href="{PROFILE_LINKEDIN}"><img src="https://img.icons8.com/color/96/000000/linkedin-circled.png" height="16"/>LinkedIn</a> ·
  <a href="{PROFILE_TWITTER}"><img src="https://img.icons8.com/color/96/000000/twitter-circled.png" height="16"/>Twitter</a> ·
  <a href="mailto:{PROFILE_EMAIL}"><img src="https://img.icons8.com/color/96/000000/email.png" height="16"/>邮箱</a> ·
  <a href="{REPO_URL}"><img src="https://img.icons8.com/color/96/000000/code.png" height="16"/>Profile 仓库</a>
</p>

#### 来玩一局井字棋（Tic-Tac-Toe）吧
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

你好，我是 {PROFILE_NAME}（GitHub: [{GITHUB_USERNAME}]({PROFILE_URL})）。  
我的邮箱是 [{PROFILE_EMAIL}](mailto:{PROFILE_EMAIL})。  
LinkedIn: [{PROFILE_LINKEDIN}]({PROFILE_LINKEDIN})。  
Twitter: [{PROFILE_TWITTER}]({PROFILE_TWITTER})。  
这里是我的 GitHub Profile 仓库，主要用于展示和维护这个互动井字棋小游戏。  
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(README)


if __name__ == "__main__":
    tile_click_count = get_tile_count()
    game_state, winner = tictactoe(tile_click_count)
    update_readme(game_state, winner)
