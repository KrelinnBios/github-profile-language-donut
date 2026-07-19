<<<<<<< HEAD
# GitHub Profile Language Donut Chart

<p align="center">
  <strong>儲存庫語言 · 自適應版面 · 自動更新</strong><br>
  為 GitHub 個人首頁產生簡潔、可設定的語言佔比環形圖
</p>

<p align="center">
  <a href="https://github.com/KrelinnBios/github-profile-language-donut/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/KrelinnBios/github-profile-language-donut/test.yml?branch=main&style=flat-square&label=%E6%B8%AC%E8%A9%A6&color=247344" alt="測試狀態"></a>
  <a href="https://github.com/KrelinnBios/github-profile-language-donut/releases"><img src="https://img.shields.io/github/v/release/KrelinnBios/github-profile-language-donut?style=flat-square&label=%E7%89%88%E6%9C%AC&color=7F52FF" alt="最新版本"></a>
  <img src="https://img.shields.io/badge/%E5%B9%B3%E5%8F%B0-GitHub%20Actions-247344?style=flat-square" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/%E6%8E%88%E6%AC%8A-MIT-1f5f9c?style=flat-square" alt="MIT License">
</p>

<p align="center">
  <a href="README.md">簡體中文</a> ·
  <a href="README.zh-TW.md">繁體中文</a> ·
  <a href="README.en.md">English</a>
</p>

## 專案簡介

GitHub Profile Language Donut Chart 是一個可重複使用的 GitHub Action。它讀取帳號名下公開儲存庫的語言資料，產生適合放在個人首頁 README 中的 SVG 環形圖，並自動維護 README 內的圖片連結。

專案適合希望展示目前開源專案語言構成、又不想依賴外部圖片服務的 GitHub 使用者。產生結果直接儲存在自己的首頁儲存庫中，樣式和更新方式都由使用者控制。

## 功能概覽

- 自適應版面：1–5 種語言顯示為一欄，6–9 種語言自動變為兩欄。
- 語言彙總：最多顯示 10 項；第 10 項為 `Other`，彙總其餘語言。
- 主題適應：同一 SVG 自動回應 GitHub 的淺色與深色顯示模式。
- 樣式設定：可調整畫布、邊距、圖例、環形圖尺寸、文字顏色和語言顏色。
- 高對比色板：預設配色主動拉開相鄰語言的色相差異，小佔比扇段也容易辨認。
- 新語言相容：未預設顏色的語言會根據名稱獲得穩定的自動配色。
- 小佔比可見：極小語言扇段使用最低可見角度和平直端點，避免相鄰顏色互相遮蓋。
- 快取處理：每次使用內容摘要產生版本化 SVG 檔名，避免舊圖片快取。
- 舊圖清理：產生新圖片時自動刪除同一字首下的舊版 SVG。
- 資料範圍可控：預設忽略首頁儲存庫、Fork 和已歸檔儲存庫，也可依需求修改範圍。
- 無第三方依賴：產生器使用 Python 標準庫，可直接在 GitHub 託管執行器中執行。

## 效果預覽

<p align="center">
  <img src="examples/preview.svg" alt="語言佔比環形圖預覽">
</p>

預設版面規則：

| 語言數量 | 圖例版面 | 環形圖位置 |
| --- | --- | --- |
| 1–5 | 左側一欄 | 右側，與圖例整體垂直置中 |
| 6–9 | 左側兩欄，每欄自動縮窄 | 隨畫布擴展時向右移動 |
| 10 及以上 | 前 9 種語言 + `Other` | 維持兩欄版面與垂直置中 |

## 使用方式

### 1. 準備個人首頁儲存庫

GitHub 個人首頁 README 來自與使用者名稱同名的公開儲存庫。例如使用者名稱為 `octocat`，首頁儲存庫應為 `octocat/octocat`。

### 2. 在 README 中加入圖片佔位

在首頁儲存庫的 `README.md` 中加入：

```html
<p align="left">
  <img src="./language-donut.svg" alt="Language distribution donut chart" />
</p>
```

第一次執行後，Action 會把 `language-donut.svg` 自動替換為類似 `language-donut-a1b2c3d4e5f6.svg` 的版本化檔名。

圖片佔位的目錄和字首必須與工作流程中的 `output-directory`、`output-prefix` 一致。

### 3. 新增設定檔

將 [`examples/language-donut.config.json`](./examples/language-donut.config.json) 複製到首頁儲存庫根目錄，並依需求修改使用者名稱、排除儲存庫和樣式。

最小設定可以只寫：

```json
{
  "owner": "YOUR_GITHUB_USERNAME",
  "profile_repository": "YOUR_GITHUB_USERNAME"
}
```

在與使用者名稱同名的個人首頁儲存庫中，這兩個欄位也可以省略，Action 會讀取目前儲存庫上下文。

### 4. 新增更新工作流程

將 [`examples/update-language-donut.yml`](./examples/update-language-donut.yml) 複製到首頁儲存庫的 `.github/workflows/update-language-donut.yml`。

完整工作流程包括檢出儲存庫、呼叫 Action 和提交產生結果：

```yaml
name: Update language donut chart

on:
  workflow_dispatch:
  repository_dispatch:
    types:
      - code-pushed
  push:
    paths:
      - ".github/workflows/update-language-donut.yml"
      - "language-donut.config.json"

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Check out profile repository
        uses: actions/checkout@v4

      - name: Generate language donut chart
        id: language-donut
        uses: KrelinnBios/github-profile-language-donut@v1.0.1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          config-path: language-donut.config.json
          output-prefix: language-donut

      - name: Commit generated chart
        if: steps.language-donut.outputs.changed == 'true'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -A -- README.md 'language-donut-*.svg'
          git commit -m "Update language donut chart"
          git push
```

### 5. 首次執行

開啟首頁儲存庫的 **Actions** 頁面，選擇更新工作流程並點選 **Run workflow**。執行成功後，產生的 SVG 和更新後的 README 會提交到首頁儲存庫。

## 統計範圍與計算方式

預設統計範圍是指定帳號擁有的公開儲存庫，並遵循以下規則：

- 自動排除個人首頁儲存庫本身。
- 預設排除 Fork 儲存庫和已歸檔儲存庫。
- `excluded_repositories` 中列出的儲存庫不會參與統計。
- 私有儲存庫不會包含在公開使用者儲存庫 API回傳的資料中。
- 每個儲存庫的語言資料來自 GitHub Languages API，數值表示 GitHub Linguist 識別出的語言位元組數。
- 百分比按所有納入統計的語言位元組數彙總計算。

圖例和環形圖中心的百分比始終使用實際資料。為避免極小佔比的顏色在環形圖中消失，低於 `min_segment_percentage` 的扇段會使用最低可見角度，其餘扇段按比例縮放；這只影響環形圖的可見幾何，不會修改文字百分比。

因此，圖表反映的是公開儲存庫目前程式碼量的語言構成，不代表熟練度、提交次數、開發時間或最近活躍程度。

## 設定說明

### 頂層設定

| 欄位 | 預設值 | 說明 |
| --- | --- | --- |
| `owner` | 目前儲存庫擁有者 | 需要統計的 GitHub 使用者名稱 |
| `profile_repository` | 目前儲存庫名稱 | 需要自動排除的個人首頁儲存庫名稱 |
| `excluded_repositories` | `[]` | 額外排除的儲存庫名稱列表 |
| `include_archived` | `false` | 是否包含已歸檔儲存庫 |
| `include_forks` | `false` | 是否包含 Fork 儲存庫 |
| `max_named_languages` | `9` | 個別顯示的語言數量，更多語言彙總為 `Other` |

### `chart` 圖表版面

| 欄位 | 預設值 | 說明 |
| --- | ---: | --- |
| `width` | `525` | 單欄模式的基礎畫布寬度 |
| `min_height` | `188` | 畫布最小高度 |
| `vertical_padding` | `28` | 圖例參與高度計算時的上下留白 |
| `row_height` | `32` | 每個語言條目的行高 |
| `legend_x` | `20` | 左側圖例起始位置 |
| `legend_width` | `256` | 圖例區域的基礎寬度 |
| `legend_column_gap` | `20` | 兩欄圖例之間的間距 |
| `two_column_extra_width` | `90` | 兩欄模式增加的畫布寬度，也是環形圖右移量 |
| `legend_rows_per_column` | `5` | 每欄最多顯示的語言數量 |
| `legend_max_columns` | `2` | 圖例最大欄數 |
| `legend_vertical_offset` | `6` | 圖例整體縱向微調量 |
| `donut_center_x` | `418` | 單欄模式的環形圖圓心水平座標 |
| `donut_radius` | `72` | 環形圖半徑 |
| `donut_width` | `22` | 環形線寬 |
| `min_segment_percentage` | `0.8` | 極小語言扇段在環形圖中的最低可見百分比 |
| `round_segment_threshold` | `5` | 達到該真實百分比時使用圓潤端點，更小扇段使用平直端點 |
| `show_bars` | `true` | 是否顯示語言佔比橫條 |
| `show_center_label` | `true` | 是否顯示環形圖中心的首位語言與百分比 |

### `theme` 主題顏色

`theme` 分別控制淺色和深色模式下的主要文字、次要文字與軌道顏色：

- `light_text`、`light_muted`、`light_track`
- `dark_text`、`dark_muted`、`dark_track`

SVG 使用 `prefers-color-scheme` 自動切換，不需要分別產生兩張圖片。

### `colors` 語言顏色

在 `colors` 中用語言名稱覆寫顏色：

```json
{
  "colors": {
    "Kotlin": "#7F52FF",
    "Python": "#22C55E",
    "PowerShell": "#EC4899",
    "Other": "#8B949E"
  }
}
```

語言名稱應與 GitHub Languages API 回傳的名稱一致。未設定的語言會根據名稱產生穩定顏色，同一語言在後續更新中不會隨機變色。

## 更新方式

### 設定修改或手動更新

示例首頁工作流程會在以下情況執行：

- 手動點選 **Run workflow**。
- 修改更新工作流程本身。
- 修改 `language-donut.config.json`。
- 收到型別為 `code-pushed` 的 `repository_dispatch` 事件。

Action 只在 SVG 內容、README 連結或舊圖檔案發生變化時輸出 `changed=true`，因此相同資料不會產生重複提交。

### 在程式碼提交後更新

如果希望程式碼儲存庫有新提交時立即更新首頁，可將 [`examples/notify-profile.yml`](./examples/notify-profile.yml) 複製到每個程式碼儲存庫：

1. 建立一個只授權個人首頁儲存庫的 fine-grained personal access token。
2. 為該 Token 授予個人首頁儲存庫的 **Contents: Read and write** 權限。
3. 在程式碼儲存庫的 **Settings → Secrets and variables → Actions** 中新增 `PROFILE_REPO_TOKEN`。
4. 將示例中的 `YOUR_GITHUB_USERNAME` 替換為自己的使用者名稱。

通知工作流程透過 `paths-ignore` 忽略 Markdown 和授權條款檔案，因此僅修改這些檔案不會觸發首頁更新。若預設分支不是 `main`，請同步修改工作流程中的分支名稱。

請不要把 Token 直接寫入儲存庫檔案或日誌。

## Action 輸入與輸出

### 輸入

| 名稱 | 必填 | 預設值 | 用途 |
| --- | --- | --- | --- |
| `github-token` | 是 | 無 | 讀取 GitHub 儲存庫與語言資料 |
| `config-path` | 否 | `language-donut.config.json` | 設定檔路徑；不存在時使用預設設定 |
| `readme-path` | 否 | `README.md` | 需要更新圖片連結的 README |
| `output-directory` | 否 | `.` | SVG 輸出目錄 |
| `output-prefix` | 否 | `language-donut` | SVG 檔名字首 |

### 輸出

| 名稱 | 說明 |
| --- | --- |
| `image` | 本次產生的版本化 SVG 路徑 |
| `changed` | 是否修改了 SVG、README 或清理了舊圖，值為 `true` 或 `false` |

## 版本選擇與安全

- `KrelinnBios/github-profile-language-donut@v1.0.1`：目前可用的穩定版本，適合直接使用。
- 其他完整版本標籤：從 [Releases](https://github.com/KrelinnBios/github-profile-language-donut/releases) 選擇，升級時由使用者決定。
- 固定提交 SHA：可獲得最嚴格的供應鏈可重複性，但需要手動追蹤更新。

首頁工作流程中的 `contents: write` 用於提交產生的 SVG 和 README；Action 本身不會向其他儲存庫寫入內容。跨儲存庫通知所用的 `PROFILE_REPO_TOKEN` 應只授權個人首頁儲存庫，並使用滿足需求的最小權限。

## 常見問題

### README 顯示 `Error Fetching Resource`

先確認工作流程已成功提交新版 SVG，並檢查 README 中的檔名是否確實存在。Action 使用版本化檔名是為了繞過 GitHub 對同名圖片的快取；請不要手動改回固定檔名。

### 提示找不到 README 中的環形圖連結

確認圖片佔位的路徑與 `output-directory`、`output-prefix` 一致。例如字首為 `language-donut` 時，首次執行前應連結 `./language-donut.svg`。

### 部分儲存庫沒有參與統計

檢查儲存庫是否為公開儲存庫、是否屬於目標使用者、是否為 Fork 或已歸檔儲存庫，以及是否出現在 `excluded_repositories` 中。

### 沒有產生新的提交

如果語言資料和樣式都沒有變化，產生的內容摘要也不會變化，`changed` 會是 `false`。這是正常行為。

### 程式碼提交後沒有觸發首頁更新

檢查程式碼儲存庫是否存在 `PROFILE_REPO_TOKEN`、Token 是否能存取個人首頁儲存庫且擁有 `Contents: Read and write`、事件名稱是否為 `code-pushed`，以及首頁工作流程是否位於預設分支。

## 本地開發

專案只使用 Python 標準庫。執行測試：

```shell
python -m unittest discover -s tests -v
```

測試覆蓋單列版面、兩欄版面、`Other` 彙總、未知語言配色和版本化檔案清理。

## 授權條款

本專案依據 [MIT License](./LICENSE) 釋出，允許使用、修改、散布和商業用途，但須保留授權條款與版權宣告。

GitHub、GitHub Actions、GitHub Linguist 及 GitHub API 分別適用其自身條款；它們不因被本專案呼叫或提及而納入本專案的 MIT 授權。

## 意見回饋與貢獻

歡迎透過 [GitHub Issues](https://github.com/KrelinnBios/github-profile-language-donut/issues) 提交使用問題、版面相容問題、新語言配色建議、文件改善或其他功能建議。
=======
# GitHub Profile Language Donut Chart

<p align="center">
  <strong>儲存庫語言 · 自適應版面 · 自動更新</strong><br>
  為 GitHub 個人首頁產生簡潔、可設定的語言佔比環形圖
</p>

<p align="center">
  <a href="https://github.com/KrelinnBios/github-profile-language-donut/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/KrelinnBios/github-profile-language-donut/test.yml?branch=main&style=flat-square&label=%E6%B8%AC%E8%A9%A6&color=247344" alt="測試狀態"></a>
  <a href="https://github.com/KrelinnBios/github-profile-language-donut/releases"><img src="https://img.shields.io/github/v/release/KrelinnBios/github-profile-language-donut?style=flat-square&label=%E7%89%88%E6%9C%AC&color=7F52FF" alt="最新版本"></a>
  <img src="https://img.shields.io/badge/%E5%B9%B3%E5%8F%B0-GitHub%20Actions-247344?style=flat-square" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/%E6%8E%88%E6%AC%8A-MIT-1f5f9c?style=flat-square" alt="MIT License">
</p>

<p align="center">
  <a href="README.md">簡體中文</a> ·
  <a href="README.zh-TW.md">繁體中文</a> ·
  <a href="README.en.md">English</a>
</p>

## 專案簡介

GitHub Profile Language Donut Chart 是一個可重複使用的 GitHub Action。它讀取帳號名下公開儲存庫的語言資料，產生適合放在個人首頁 README 中的 SVG 環形圖，並自動維護 README 內的圖片連結。

專案適合希望展示目前開源專案語言構成、又不想依賴外部圖片服務的 GitHub 使用者。產生結果直接儲存在自己的首頁儲存庫中，樣式和更新方式都由使用者控制。

## 功能概覽

- 自適應版面：1–5 種語言顯示為一欄，6–9 種語言自動變為兩欄。
- 語言彙總：最多顯示 10 項；第 10 項為 `Other`，彙總其餘語言。
- 主題適應：同一 SVG 自動回應 GitHub 的淺色與深色顯示模式。
- 樣式設定：可調整畫布、邊距、圖例、環形圖尺寸、文字顏色和語言顏色。
- 高對比色板：預設配色主動拉開相鄰語言的色相差異，小佔比扇段也容易辨認。
- 新語言相容：未預設顏色的語言會根據名稱獲得穩定的自動配色。
- 小佔比可見：極小語言扇段使用最低可見角度和平直端點，避免相鄰顏色互相遮蓋。
- 快取處理：每次使用內容摘要產生版本化 SVG 檔名，避免舊圖片快取。
- 舊圖清理：產生新圖片時自動刪除同一字首下的舊版 SVG。
- 資料範圍可控：預設忽略首頁儲存庫、Fork 和已歸檔儲存庫，也可依需求修改範圍。
- 無第三方依賴：產生器使用 Python 標準庫，可直接在 GitHub 託管執行器中執行。

## 效果預覽

<p align="center">
  <img src="examples/preview.svg" alt="語言佔比環形圖預覽">
</p>

預設版面規則：

| 語言數量 | 圖例版面 | 環形圖位置 |
| --- | --- | --- |
| 1–5 | 左側一欄 | 右側，與圖例整體垂直置中 |
| 6–9 | 左側兩欄，每欄自動縮窄 | 隨畫布擴展時向右移動 |
| 10 及以上 | 前 9 種語言 + `Other` | 維持兩欄版面與垂直置中 |

## 使用方式

### 1. 準備個人首頁儲存庫

GitHub 個人首頁 README 來自與使用者名稱同名的公開儲存庫。例如使用者名稱為 `octocat`，首頁儲存庫應為 `octocat/octocat`。

### 2. 在 README 中加入圖片佔位

在首頁儲存庫的 `README.md` 中加入：

```html
<p align="left">
  <img src="./language-donut.svg" alt="Language distribution donut chart" />
</p>
```

第一次執行後，Action 會把 `language-donut.svg` 自動替換為類似 `language-donut-a1b2c3d4e5f6.svg` 的版本化檔名。

圖片佔位的目錄和字首必須與工作流程中的 `output-directory`、`output-prefix` 一致。

### 3. 新增設定檔

將 [`examples/language-donut.config.json`](./examples/language-donut.config.json) 複製到首頁儲存庫根目錄，並依需求修改使用者名稱、排除儲存庫和樣式。

最小設定可以只寫：

```json
{
  "owner": "YOUR_GITHUB_USERNAME",
  "profile_repository": "YOUR_GITHUB_USERNAME"
}
```

在與使用者名稱同名的個人首頁儲存庫中，這兩個欄位也可以省略，Action 會讀取目前儲存庫上下文。

### 4. 新增更新工作流程

將 [`examples/update-language-donut.yml`](./examples/update-language-donut.yml) 複製到首頁儲存庫的 `.github/workflows/update-language-donut.yml`。

完整工作流程包括檢出儲存庫、呼叫 Action 和提交產生結果：

```yaml
name: Update language donut chart

on:
  workflow_dispatch:
  repository_dispatch:
    types:
      - code-pushed
  push:
    paths:
      - ".github/workflows/update-language-donut.yml"
      - "language-donut.config.json"

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Check out profile repository
        uses: actions/checkout@v4

      - name: Generate language donut chart
        id: language-donut
        uses: KrelinnBios/github-profile-language-donut@v1.0.1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          config-path: language-donut.config.json
          output-prefix: language-donut

      - name: Commit generated chart
        if: steps.language-donut.outputs.changed == 'true'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -A -- README.md 'language-donut-*.svg'
          git commit -m "Update language donut chart"
          git push
```

### 5. 首次執行

開啟首頁儲存庫的 **Actions** 頁面，選擇更新工作流程並點選 **Run workflow**。執行成功後，產生的 SVG 和更新後的 README 會提交到首頁儲存庫。

## 統計範圍與計算方式

預設統計範圍是指定帳號擁有的公開儲存庫，並遵循以下規則：

- 自動排除個人首頁儲存庫本身。
- 預設排除 Fork 儲存庫和已歸檔儲存庫。
- `excluded_repositories` 中列出的儲存庫不會參與統計。
- 私有儲存庫不會包含在公開使用者儲存庫 API回傳的資料中。
- 每個儲存庫的語言資料來自 GitHub Languages API，數值表示 GitHub Linguist 識別出的語言位元組數。
- 百分比按所有納入統計的語言位元組數彙總計算。

圖例和環形圖中心的百分比始終使用實際資料。為避免極小佔比的顏色在環形圖中消失，低於 `min_segment_percentage` 的扇段會使用最低可見角度，其餘扇段按比例縮放；這只影響環形圖的可見幾何，不會修改文字百分比。

因此，圖表反映的是公開儲存庫目前程式碼量的語言構成，不代表熟練度、提交次數、開發時間或最近活躍程度。

## 設定說明

### 頂層設定

| 欄位 | 預設值 | 說明 |
| --- | --- | --- |
| `owner` | 目前儲存庫擁有者 | 需要統計的 GitHub 使用者名稱 |
| `profile_repository` | 目前儲存庫名稱 | 需要自動排除的個人首頁儲存庫名稱 |
| `excluded_repositories` | `[]` | 額外排除的儲存庫名稱列表 |
| `include_archived` | `false` | 是否包含已歸檔儲存庫 |
| `include_forks` | `false` | 是否包含 Fork 儲存庫 |
| `max_named_languages` | `9` | 個別顯示的語言數量，更多語言彙總為 `Other` |

### `chart` 圖表版面

| 欄位 | 預設值 | 說明 |
| --- | ---: | --- |
| `width` | `525` | 單欄模式的基礎畫布寬度 |
| `min_height` | `188` | 畫布最小高度 |
| `vertical_padding` | `28` | 圖例參與高度計算時的上下留白 |
| `row_height` | `32` | 每個語言條目的行高 |
| `legend_x` | `20` | 左側圖例起始位置 |
| `legend_width` | `256` | 圖例區域的基礎寬度 |
| `legend_column_gap` | `20` | 兩欄圖例之間的間距 |
| `two_column_extra_width` | `90` | 兩欄模式增加的畫布寬度，也是環形圖右移量 |
| `legend_rows_per_column` | `5` | 每欄最多顯示的語言數量 |
| `legend_max_columns` | `2` | 圖例最大欄數 |
| `legend_vertical_offset` | `6` | 圖例整體縱向微調量 |
| `donut_center_x` | `418` | 單欄模式的環形圖圓心水平座標 |
| `donut_radius` | `72` | 環形圖半徑 |
| `donut_width` | `22` | 環形線寬 |
| `min_segment_percentage` | `0.8` | 極小語言扇段在環形圖中的最低可見百分比 |
| `round_segment_threshold` | `5` | 達到該真實百分比時使用圓潤端點，更小扇段使用平直端點 |
| `show_bars` | `true` | 是否顯示語言佔比橫條 |
| `show_center_label` | `true` | 是否顯示環形圖中心的首位語言與百分比 |

### `theme` 主題顏色

`theme` 分別控制淺色和深色模式下的主要文字、次要文字與軌道顏色：

- `light_text`、`light_muted`、`light_track`
- `dark_text`、`dark_muted`、`dark_track`

SVG 使用 `prefers-color-scheme` 自動切換，不需要分別產生兩張圖片。

### `colors` 語言顏色

在 `colors` 中用語言名稱覆寫顏色：

```json
{
  "colors": {
    "Kotlin": "#7F52FF",
    "Python": "#22C55E",
    "PowerShell": "#EC4899",
    "Other": "#8B949E"
  }
}
```

語言名稱應與 GitHub Languages API 回傳的名稱一致。未設定的語言會根據名稱產生穩定顏色，同一語言在後續更新中不會隨機變色。

## 更新方式

### 設定修改或手動更新

示例首頁工作流程會在以下情況執行：

- 手動點選 **Run workflow**。
- 修改更新工作流程本身。
- 修改 `language-donut.config.json`。
- 收到型別為 `code-pushed` 的 `repository_dispatch` 事件。

Action 只在 SVG 內容、README 連結或舊圖檔案發生變化時輸出 `changed=true`，因此相同資料不會產生重複提交。

### 在程式碼提交後更新

如果希望程式碼儲存庫有新提交時立即更新首頁，可將 [`examples/notify-profile.yml`](./examples/notify-profile.yml) 複製到每個程式碼儲存庫：

1. 建立一個只授權個人首頁儲存庫的 fine-grained personal access token。
2. 為該 Token 授予個人首頁儲存庫的 **Contents: Read and write** 權限。
3. 在程式碼儲存庫的 **Settings → Secrets and variables → Actions** 中新增 `PROFILE_REPO_TOKEN`。
4. 將示例中的 `YOUR_GITHUB_USERNAME` 替換為自己的使用者名稱。

通知工作流程透過 `paths-ignore` 忽略 Markdown 和授權條款檔案，因此僅修改這些檔案不會觸發首頁更新。若預設分支不是 `main`，請同步修改工作流程中的分支名稱。

請不要把 Token 直接寫入儲存庫檔案或日誌。

## Action 輸入與輸出

### 輸入

| 名稱 | 必填 | 預設值 | 用途 |
| --- | --- | --- | --- |
| `github-token` | 是 | 無 | 讀取 GitHub 儲存庫與語言資料 |
| `config-path` | 否 | `language-donut.config.json` | 設定檔路徑；不存在時使用預設設定 |
| `readme-path` | 否 | `README.md` | 需要更新圖片連結的 README |
| `output-directory` | 否 | `.` | SVG 輸出目錄 |
| `output-prefix` | 否 | `language-donut` | SVG 檔名字首 |

### 輸出

| 名稱 | 說明 |
| --- | --- |
| `image` | 本次產生的版本化 SVG 路徑 |
| `changed` | 是否修改了 SVG、README 或清理了舊圖，值為 `true` 或 `false` |

## 版本選擇與安全

- `KrelinnBios/github-profile-language-donut@v1.0.1`：目前可用的穩定版本，適合直接使用。
- 其他完整版本標籤：從 [Releases](https://github.com/KrelinnBios/github-profile-language-donut/releases) 選擇，升級時由使用者決定。
- 固定提交 SHA：可獲得最嚴格的供應鏈可重複性，但需要手動追蹤更新。

首頁工作流程中的 `contents: write` 用於提交產生的 SVG 和 README；Action 本身不會向其他儲存庫寫入內容。跨儲存庫通知所用的 `PROFILE_REPO_TOKEN` 應只授權個人首頁儲存庫，並使用滿足需求的最小權限。

## 常見問題

### README 顯示 `Error Fetching Resource`

先確認工作流程已成功提交新版 SVG，並檢查 README 中的檔名是否確實存在。Action 使用版本化檔名是為了繞過 GitHub 對同名圖片的快取；請不要手動改回固定檔名。

### 提示找不到 README 中的環形圖連結

確認圖片佔位的路徑與 `output-directory`、`output-prefix` 一致。例如字首為 `language-donut` 時，首次執行前應連結 `./language-donut.svg`。

### 部分儲存庫沒有參與統計

檢查儲存庫是否為公開儲存庫、是否屬於目標使用者、是否為 Fork 或已歸檔儲存庫，以及是否出現在 `excluded_repositories` 中。

### 沒有產生新的提交

如果語言資料和樣式都沒有變化，產生的內容摘要也不會變化，`changed` 會是 `false`。這是正常行為。

### 程式碼提交後沒有觸發首頁更新

檢查程式碼儲存庫是否存在 `PROFILE_REPO_TOKEN`、Token 是否能存取個人首頁儲存庫且擁有 `Contents: Read and write`、事件名稱是否為 `code-pushed`，以及首頁工作流程是否位於預設分支。

## 本地開發

專案只使用 Python 標準庫。執行測試：

```shell
python -m unittest discover -s tests -v
```

測試覆蓋單列版面、兩欄版面、`Other` 彙總、未知語言配色和版本化檔案清理。

## 授權條款

本專案依據 [MIT License](./LICENSE) 釋出，允許使用、修改、散布和商業用途，但須保留授權條款與版權宣告。

GitHub、GitHub Actions、GitHub Linguist 及 GitHub API 分別適用其自身條款；它們不因被本專案呼叫或提及而納入本專案的 MIT 授權。

## 意見回饋與貢獻

歡迎透過 [GitHub Issues](https://github.com/KrelinnBios/github-profile-language-donut/issues) 提交使用問題、版面相容問題、新語言配色建議、文件改善或其他功能建議。
>>>>>>> 23b6d9dccb1f19b39219aee4f0a0b2a3b8f1939d
