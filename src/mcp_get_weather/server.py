import contextlib
import logging
import os
from collections.abc import AsyncIterator

import anyio
import click
import httpx
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

# ---------------------------------------------------------------------------
# Weather helpers
# ---------------------------------------------------------------------------
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
DEFAULT_UNITS = "metric"  # use Celsius by default
DEFAULT_LANG = "zh_cn"  # Chinese descriptions


async def fetch_weather(city: str, api_key: str) -> dict[str, str]:
    """Call OpenWeather API and return a simplified weather dict.

    Raises:
        httpx.HTTPStatusError: if the response has a non-2xx status.
    """
    params = {
        "q": city,
        "appid": api_key,
        "units": DEFAULT_UNITS,
        "lang": DEFAULT_LANG,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(OPENWEATHER_URL, params=params)
        r.raise_for_status()
        data = r.json()
    # Extract a concise summary
    weather_main = data["weather"][0]["main"]
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    return {
        "city": city,
        "weather": weather_main,
        "description": description,
        "temp": f"{temp}°C",
        "feels_like": f"{feels_like}°C",
        "humidity": f"{humidity}%",
    }


async def fetch_weekly_weather(city: str, api_key: str) -> list[dict[str, str]]:
    """Call OpenWeather forecast API and return a 7-day weather forecast.

    Raises:
        httpx.HTTPStatusError: if the response has a non-2xx status.
    """
    params = {
        "q": city,
        "appid": api_key,
        "units": DEFAULT_UNITS,
        "lang": DEFAULT_LANG,
        "cnt": 56,  # 7 days * 8 forecasts per day (every 3 hours)
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(OPENWEATHER_FORECAST_URL, params=params)
        r.raise_for_status()
        data = r.json()
    
    # Group forecasts by date and extract daily summaries
    from datetime import datetime
    daily_forecasts = {}
    
    for item in data["list"]:
        # Parse the forecast timestamp
        dt = datetime.fromtimestamp(item["dt"])
        date_key = dt.strftime("%Y-%m-%d")
        
        # If we haven't seen this date yet, or this is a midday forecast, store it
        if date_key not in daily_forecasts or dt.hour == 12:
            daily_forecasts[date_key] = {
                "date": dt.strftime("%Y年%m月%d日"),
                "description": item["weather"][0]["description"],
                "temp": f"{item['main']['temp']:.1f}°C",
                "temp_min": f"{item['main']['temp_min']:.1f}°C",
                "temp_max": f"{item['main']['temp_max']:.1f}°C",
                "humidity": f"{item['main']['humidity']}%",
            }
    
    # Return up to 7 days
    return list(daily_forecasts.values())[:7]


@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option(
    "--api-key",
    envvar="OPENWEATHER_API_KEY",
    required=True,
    help="OpenWeather API key (or set OPENWEATHER_API_KEY env var)",
)
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(port: int, api_key: str, log_level: str, json_response: bool) -> int:
    """Run an MCP weather server using Streamable HTTP transport."""

    # ---------------------- Configure logging ----------------------
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("weather-server")

    # ---------------------- Create MCP Server ----------------------
    app = Server("mcp-streamable-http-weather")

    # ---------------------- Tool implementation -------------------
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls for both current and weekly weather."""
        ctx = app.request_context
        city = arguments.get("location")
        if not city:
            raise ValueError("'location' is required in arguments")

        if name == "get-weather":
            # Send an initial log message so the client sees streaming early.
            await ctx.session.send_log_message(
                level="info",
                data=f"Fetching weather for {city}…",
                logger="weather",
                related_request_id=ctx.request_id,
            )

            try:
                weather = await fetch_weather(city, api_key)
            except Exception as err:
                # Stream the error to the client and re-raise so MCP returns error.
                await ctx.session.send_log_message(
                    level="error",
                    data=str(err),
                    logger="weather",
                    related_request_id=ctx.request_id,
                )
                raise

            # Stream a success notification (optional)
            await ctx.session.send_log_message(
                level="info",
                data="Weather data fetched successfully!",
                logger="weather",
                related_request_id=ctx.request_id,
            )

            # Compose human-readable summary for the final return value.
            summary = (
                f"{weather['city']}：{weather['description']}，温度 {weather['temp']}，"
                f"体感 {weather['feels_like']}，湿度 {weather['humidity']}。"
            )

            return [
                types.TextContent(type="text", text=summary),
            ]

        elif name == "get-weekly-weather":
            # Send an initial log message
            await ctx.session.send_log_message(
                level="info",
                data=f"Fetching 7-day weather forecast for {city}…",
                logger="weather",
                related_request_id=ctx.request_id,
            )

            try:
                forecasts = await fetch_weekly_weather(city, api_key)
            except Exception as err:
                # Stream the error to the client and re-raise so MCP returns error.
                await ctx.session.send_log_message(
                    level="error",
                    data=str(err),
                    logger="weather",
                    related_request_id=ctx.request_id,
                )
                raise

            # Stream a success notification
            await ctx.session.send_log_message(
                level="info",
                data=f"Fetched {len(forecasts)} days of forecast data!",
                logger="weather",
                related_request_id=ctx.request_id,
            )

            # Compose human-readable summary for the forecast
            summary_lines = [f"{city}未来一周天气预报：\n"]
            for forecast in forecasts:
                summary_lines.append(
                    f"• {forecast['date']}：{forecast['description']}，"
                    f"温度 {forecast['temp']}（最低 {forecast['temp_min']}，最高 {forecast['temp_max']}），"
                    f"湿度 {forecast['humidity']}"
                )
            
            summary = "\n".join(summary_lines)

            return [
                types.TextContent(type="text", text=summary),
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")

    # ---------------------- Tool registry -------------------------
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """Expose available tools to the LLM."""
        return [
            types.Tool(
                name="get-weather",
                description="查询指定城市的实时天气（OpenWeather 数据）",
                inputSchema={
                    "type": "object",
                    "required": ["location"],
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市的英文名称，如 'Beijing'",
                        }
                    },
                },
            ),
            types.Tool(
                name="get-weekly-weather",
                description="查询指定城市未来一周的天气预报（OpenWeather 数据）",
                inputSchema={
                    "type": "object",
                    "required": ["location"],
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市的英文名称，如 'Beijing'",
                        }
                    },
                },
            ),
        ]

    # ---------------------- Session manager -----------------------
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,  # 无状态；不保存历史事件
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:  # noqa: D401,E501
        await session_manager.handle_request(scope, receive, send)

    # ---------------------- Lifespan Management --------------------
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            logger.info("Weather MCP server started! 🚀")
            try:
                yield
            finally:
                logger.info("Weather MCP server shutting down…")

    # ---------------------- ASGI app + Uvicorn ---------------------
    starlette_app = Starlette(
        debug=False,
        routes=[Mount("/mcp", app=handle_streamable_http)],
        lifespan=lifespan,
    )

    import uvicorn

    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

    return 0


if __name__ == "__main__":
    main()
