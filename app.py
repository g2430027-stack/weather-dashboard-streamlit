"""Streamlit weather dashboard powered by WeatherAPI."""

import datetime as dt
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import streamlit as st


BASE_URL = "https://api.weatherapi.com/v1"
REQUEST_TIMEOUT = 10


class WeatherAPIError(Exception):
    """Raised when WeatherAPI returns an error or cannot be reached."""


def get_api_key() -> str | None:
    """Read the API key from Streamlit Secrets or an environment variable."""
    try:
        secret_key = st.secrets.get("WEATHER_API_KEY")
    except Exception:
        secret_key = None

    return secret_key or os.getenv("WEATHER_API_KEY")


def request_weather(endpoint: str, api_key: str, **params) -> dict:
    """Request JSON data from WeatherAPI with consistent error handling."""
    request_params = {
        "key": api_key,
        "lang": "ja",
        **params,
    }

    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            params=request_params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        raise WeatherAPIError("通信がタイムアウトしました。もう一度お試しください。") from exc
    except requests.RequestException as exc:
        raise WeatherAPIError("天気情報の取得中に通信エラーが発生しました。") from exc
    except ValueError as exc:
        raise WeatherAPIError("APIから正しい形式のデータを取得できませんでした。") from exc

    if "error" in data:
        message = data["error"].get("message", "天気情報を取得できませんでした。")
        raise WeatherAPIError(message)

    return data


def background_color(condition: str) -> str:
    """Return a background color based on the Japanese weather description."""
    if "雷" in condition:
        return "#C5CAE9"
    if "雪" in condition:
        return "#E3F2FD"
    if "雨" in condition:
        return "#CFD8DC"
    if "曇" in condition:
        return "#ECEFF1"
    if "晴" in condition:
        return "#E1F5FE"
    return "#FFFFFF"


def apply_background(condition: str) -> None:
    """Apply the selected color to the Streamlit app background."""
    color = background_color(condition)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_current_weather(data: dict) -> None:
    """Display current weather metrics."""
    current = data["current"]
    location = data["location"]

    st.caption(
        f"{location['name']}, {location['country']}｜"
        f"現地時刻 {location['localtime']}"
    )

    st.image(f"https:{current['condition']['icon']}", width=120)
    st.subheader(current["condition"]["text"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️ 気温", f"{current['temp_c']}℃")
    col2.metric("🤔 体感温度", f"{current['feelslike_c']}℃")
    col3.metric("💧 湿度", f"{current['humidity']}%")
    col4.metric("🍃 風速", f"{current['wind_kph']} km/h")


def show_three_day_forecast(forecast: list[dict]) -> None:
    """Display one card for each forecast day."""
    columns = st.columns(len(forecast))

    for column, day in zip(columns, forecast):
        day_info = day["day"]

        with column:
            st.write(f"**{day['date']}**")
            st.image(f"https:{day_info['condition']['icon']}", width=80)
            st.write(day_info["condition"]["text"])
            st.write(f"⬆️ 最高 {day_info['maxtemp_c']}℃")
            st.write(f"⬇️ 最低 {day_info['mintemp_c']}℃")
            st.write(f"☔ 降水確率 {day_info['daily_chance_of_rain']}%")


def show_hourly_forecast(hours: list[dict]) -> None:
    """Display rain alerts and an hourly temperature chart."""
    st.subheader("☔ 傘通知")

    rainy_hours = [
        (hour["time"][11:16], hour["chance_of_rain"])
        for hour in hours
        if hour["chance_of_rain"] >= 70
    ]

    if rainy_hours:
        for time, chance in rainy_hours:
            st.warning(f"{time}：降水確率 {chance}% → 傘の携帯をおすすめします")
    else:
        st.success("今日は降水確率70%以上の時間帯はありません")

    hourly_df = pd.DataFrame(
        {
            "時間": [hour["time"][11:16] for hour in hours],
            "気温": [hour["temp_c"] for hour in hours],
        }
    ).set_index("時間")

    st.subheader("📈 時間別気温")
    st.line_chart(hourly_df)


def fetch_history(
    city: str,
    api_key: str,
    local_date: dt.date,
    days: int = 7,
) -> tuple[pd.DataFrame, list[str]]:
    """Fetch hourly temperatures for the requested location's recent days."""
    records = []
    errors = []

    for days_ago in range(days - 1, -1, -1):
        target_date = local_date - dt.timedelta(days=days_ago)

        try:
            history = request_weather(
                "history.json",
                api_key,
                q=city,
                dt=target_date.isoformat(),
            )
        except WeatherAPIError as exc:
            errors.append(f"{target_date}: {exc}")
            continue

        hours = history["forecast"]["forecastday"][0]["hour"]
        row = {"日付": target_date.isoformat()}

        for hour in hours:
            hour_label = f"{hour['time'][11:13]}時"
            row[hour_label] = hour["temp_c"]

        records.append(row)

    if not records:
        return pd.DataFrame(), errors

    return pd.DataFrame(records).set_index("日付"), errors


def show_temperature_heatmap(
    city: str,
    api_key: str,
    local_date: dt.date,
) -> None:
    """Display a seven-day hourly temperature heatmap."""
    with st.spinner("過去7日間の気温を取得しています..."):
        history_df, errors = fetch_history(city, api_key, local_date)

    if history_df.empty:
        st.error("過去の気温データを取得できませんでした。")
        if errors:
            st.caption(errors[0])
        return

    if errors:
        st.warning(
            f"{len(errors)}日分のデータを取得できなかったため、"
            "取得できた日だけを表示しています。"
        )

    figure, axis = plt.subplots(figsize=(14, 5))
    sns.heatmap(
        history_df,
        annot=True,
        fmt=".1f",
        cmap="coolwarm",
        cbar_kws={"label": "気温（℃）"},
        ax=axis,
    )
    axis.set_xlabel("時間")
    axis.set_ylabel("日付")
    axis.set_title("過去7日間の時間別気温")
    plt.tight_layout()
    st.pyplot(figure)
    plt.close(figure)


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="天気予報アプリ",
        page_icon="🌤️",
        layout="wide",
    )

    st.title("🌤️ Weather Dashboard")
    st.write("都市名を入力すると、現在の天気や3日間の予報を確認できます。")

    api_key = get_api_key()
    if not api_key:
        st.error(
            "WeatherAPIのAPIキーが設定されていません。"
            "WEATHER_API_KEYをStreamlit Secretsまたは環境変数に設定してください。"
        )
        st.stop()

    city = st.text_input(
        "都市名を入力してください",
        placeholder="例：Kumamoto, Tokyo, Fukuoka",
        key="city_input",
    ).strip()

    if not st.button("天気を取得", type="primary"):
        st.info("都市名を入力して「天気を取得」を押してください。")
        return

    if not city:
        st.warning("都市名を入力してください。")
        return

    try:
        with st.spinner("天気情報を取得しています..."):
            data = request_weather(
                "forecast.json",
                api_key,
                q=city,
                days=3,
                aqi="no",
                alerts="no",
            )
    except WeatherAPIError as exc:
        st.error(f"天気情報を取得できませんでした：{exc}")
        return

    current = data["current"]
    forecast = data["forecast"]["forecastday"]
    local_date = dt.date.fromisoformat(data["location"]["localtime"][:10])

    apply_background(current["condition"]["text"])

    current_tab, forecast_tab, hourly_tab, history_tab = st.tabs(
        [
            "🌤️ 現在の天気",
            "📅 3日間予報",
            "📈 時間別",
            "🌡️ 過去7日",
        ]
    )

    with current_tab:
        show_current_weather(data)

    with forecast_tab:
        show_three_day_forecast(forecast)

    with hourly_tab:
        show_hourly_forecast(forecast[0]["hour"])

    with history_tab:
        show_temperature_heatmap(city, api_key, local_date)


if __name__ == "__main__":
    main()
