# Weather Dashboard

StreamlitとWeatherAPIを使用して開発した、都市別の天気情報を確認できるWebアプリケーションです。

都市名を入力すると、現在の天気、3日間の予報、時間別の気温、降水確率に基づく傘通知、過去7日間の気温ヒートマップを表示します。

## Screenshot

![Weather Dashboard](images/app_screenshot.png)

## Features

* 都市名による天気情報の検索
* 現在の気温・体感温度・湿度・風速の表示
* 天気アイコンと現地時刻の表示
* 3日間の天気・最高気温・最低気温・降水確率の表示
* 24時間の気温推移を折れ線グラフで可視化
* 降水確率70%以上の時間帯に傘通知を表示
* 過去7日間の時間別気温をヒートマップで可視化
* 天気に応じた背景色の変更
* 通信エラーや入力エラーへの対応

## Technologies

* Python
* Streamlit
* WeatherAPI
* Requests
* pandas
* Matplotlib
* Seaborn

## Project Structure

```text
weather-dashboard-streamlit/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
└── images/
    └── app_screenshot.png
```

APIキーを保存する`.streamlit/secrets.toml`と、仮想環境の`.venv`はGitHubには公開していません。

## Setup

### 1. リポジトリを取得

```bash
git clone https://github.com/ユーザー名/weather-dashboard-streamlit.git
cd weather-dashboard-streamlit
```

### 2. 仮想環境を作成

Windowsの場合：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS・Linuxの場合：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 必要なライブラリをインストール

```bash
python -m pip install -r requirements.txt
```

### 4. WeatherAPIのAPIキーを設定

[WeatherAPI](https://www.weatherapi.com/)でAPIキーを取得します。

プロジェクト内に`.streamlit`フォルダを作成し、その中に`secrets.toml`を作成します。

```text
weather-dashboard-streamlit/
└── .streamlit/
    └── secrets.toml
```

`secrets.toml`にAPIキーを設定します。

```toml
WEATHER_API_KEY = "取得したAPIキー"
```

APIキーを含む`secrets.toml`は、GitHubへアップロードしないでください。

### 5. アプリを起動

```bash
python -m streamlit run app.py
```

ブラウザでアプリが開いたら、検索欄に都市名を入力します。

```text
Kumamoto
Tokyo
Fukuoka
```

## Application Flow

1. 利用者が都市名を入力
2. WeatherAPIから現在の天気と3日間予報を取得
3. 気温・湿度・風速などを画面に表示
4. 時間別データから気温グラフと傘通知を作成
5. 過去の気温データを取得してヒートマップを作成

## Error Handling

以下の状況では、利用者に分かりやすいエラーメッセージを表示します。

* 都市名が入力されていない
* 都市名が見つからない
* APIキーが設定されていない
* APIとの通信がタイムアウトした
* 過去の気温データを取得できない

過去データの一部だけを取得できなかった場合は、取得できた日付のデータを使ってヒートマップを表示します。

## Security

APIキーはソースコードに直接記述せず、Streamlit Secretsまたは環境変数から取得します。

```python
api_key = st.secrets.get("WEATHER_API_KEY")
```

`.gitignore`を使用して、APIキーや仮想環境がGitHubへ公開されないようにしています。

```gitignore
.streamlit/secrets.toml
.venv/
venv/
__pycache__/
*.pyc
```

## What I Learned

この開発を通じて、外部APIからJSON形式のデータを取得し、必要な情報を抽出してWeb画面に表示する一連の流れを学びました。

また、pandasによるデータ加工、Matplotlib・Seabornによる可視化、StreamlitによるUI構築に加えて、APIキーの安全な管理、例外処理、関数分割など、公開を意識したアプリケーション設計にも取り組みました。

## Future Improvements

* 都市名の入力候補表示
* お気に入り都市の保存
* 複数都市の天気比較
* 降水量や風速の追加グラフ
* 現在地を利用した天気表示
* APIリクエストのキャッシュ
* スマートフォン向けUIの改善

## Notes

WeatherAPIの契約プランによっては、過去の気象データを取得できない場合があります。その場合でも、現在の天気、3日間予報、時間別気温、傘通知は利用できます。

## License

This project is licensed under the MIT License.
