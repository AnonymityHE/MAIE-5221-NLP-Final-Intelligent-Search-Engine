"""
金融工具 - 获取股票和加密货币数据
"""
import requests
from typing import Dict, Optional
from services.core.logger import logger


def get_stock_price(symbol: str, region: str = "US") -> Optional[str]:
    """
    获取股票价格（使用免费的Yahoo Finance API模拟）
    
    Args:
        symbol: 股票代码（如 AAPL, TSLA, 0700.HK）
        region: 地区 (US, HK, CN等)
        
    Returns:
        股票价格信息字符串，如果失败返回None
    """
    try:
        # 注意：Yahoo Finance API可能需要认证，这里使用简化的实现
        # 实际生产环境建议使用正式的金融API（如Alpha Vantage）
        symbol_upper = symbol.upper()
        
        # 对于港股，使用Yahoo Finance格式
        if region == "HK" and not symbol_upper.endswith(".HK"):
            symbol_upper = f"{symbol_upper}.HK"
        
        # 使用免费的Yahoo Finance API（通过yfinance库或直接API调用）
        # 这里使用简化的网页搜索方式获取信息
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol_upper}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result = data.get("chart", {}).get("result", [])
            if result:
                quote = result[0].get("meta", {})
                current_price = quote.get("regularMarketPrice", "N/A")
                previous_close = quote.get("previousClose", "N/A")
                change = quote.get("regularMarketPrice", 0) - quote.get("previousClose", 0)
                change_percent = (change / quote.get("previousClose", 1)) * 100 if quote.get("previousClose") else 0
                
                info = f"股票代码: {symbol_upper}\n"
                info += f"当前价格: ${current_price:.2f}\n" if isinstance(current_price, (int, float)) else f"当前价格: {current_price}\n"
                info += f"前收盘价: ${previous_close:.2f}\n" if isinstance(previous_close, (int, float)) else f"前收盘价: {previous_close}\n"
                if isinstance(change, (int, float)) and isinstance(change_percent, (int, float)):
                    change_sign = "+" if change >= 0 else ""
                    info += f"涨跌: {change_sign}${change:.2f} ({change_sign}{change_percent:.2f}%)\n"
                
                logger.info(f"成功获取股票 {symbol_upper} 的价格信息")
                return info
        
        logger.warning(f"无法获取股票 {symbol_upper} 的价格信息")
        return None
        
    except Exception as e:
        logger.error(f"获取股票价格失败: {e}")
        return None


def get_crypto_price(symbol: str) -> Optional[str]:
    """
    获取加密货币价格（使用免费的CoinGecko API）
    
    Args:
        symbol: 加密货币代码（如 BTC, ETH, USDT）
        
    Returns:
        加密货币价格信息字符串，如果失败返回None
    """
    try:
        symbol_lower = symbol.lower()
        
        # 使用CoinGecko免费API
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": symbol_lower,  # CoinGecko使用id而不是symbol
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        
        # CoinGecko ID映射（常见币种）
        coin_ids = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "usdt": "tether",
            "bnb": "binancecoin",
            "sol": "solana",
            "ada": "cardano",
            "doge": "dogecoin",
            "xrp": "ripple",
            "dot": "polkadot",
            "matic": "matic-network"
        }
        
        coin_id = coin_ids.get(symbol_lower, symbol_lower)
        params["ids"] = coin_id
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                price_info = data[coin_id]
                price = price_info.get("usd", "N/A")
                change_24h = price_info.get("usd_24h_change", "N/A")
                
                info = f"加密货币: {symbol.upper()}\n"
                if isinstance(price, (int, float)):
                    info += f"当前价格: ${price:,.2f}\n"
                else:
                    info += f"当前价格: {price}\n"
                
                if isinstance(change_24h, (int, float)):
                    change_sign = "+" if change_24h >= 0 else ""
                    info += f"24小时涨跌: {change_sign}{change_24h:.2f}%\n"
                else:
                    info += f"24小时涨跌: {change_24h}\n"
                
                logger.info(f"成功获取加密货币 {symbol.upper()} 的价格信息")
                return info
        
        logger.warning(f"无法获取加密货币 {symbol.upper()} 的价格信息")
        return None
        
    except Exception as e:
        logger.error(f"获取加密货币价格失败: {e}")
        return None


def get_finance_context(query: str, num_results: int = 3) -> str:
    """
    根据查询内容获取金融信息上下文
    
    Args:
        query: 用户查询
        num_results: 返回结果数量
        
    Returns:
        金融信息上下文字符串
    """
    query_lower = query.lower()
    contexts = []
    
    # 提取股票代码（增强的智能匹配）
    import re
    
    # 公司名到股票代码的映射（中英文）
    company_to_ticker = {
        # 美股
        "apple": "AAPL", "苹果": "AAPL",
        "microsoft": "MSFT", "微软": "MSFT",
        "google": "GOOGL", "alphabet": "GOOGL", "谷歌": "GOOGL",
        "amazon": "AMZN", "亚马逊": "AMZN",
        "tesla": "TSLA", "特斯拉": "TSLA",
        "meta": "META", "facebook": "META",
        "nvidia": "NVDA", "英伟达": "NVDA",
        "amd": "AMD",
        "intel": "INTC", "英特尔": "INTC",
        "netflix": "NFLX",
        # 中概股/港股
        "alibaba": "BABA", "阿里巴巴": "BABA", "阿里": "BABA",
        "tencent": "0700.HK", "腾讯": "0700.HK",
        "byd": "002594.SZ", "比亚迪": "002594.SZ",
        "xiaomi": "1810.HK", "小米": "1810.HK",
        "baidu": "BIDU", "百度": "BIDU",
        "jd": "JD", "京东": "JD",
        "nio": "NIO", "蔚来": "NIO",
        "xpeng": "XPEV", "小鹏": "XPEV",
        "li auto": "LI", "理想": "LI",
    }
    
    # 匹配股票代码模式（如 AAPL, TSLA, 0700.HK）
    stock_patterns = [
        r'\b([A-Z]{1,5}(?:\.HK|\.SS|\.SZ)?)\b',  # 股票代码
        r'([0-9]{4}\.(?:HK|SS|SZ))',  # 港股/A股代码
    ]
    
    # 匹配加密货币代码
    crypto_keywords = {
        "bitcoin": "btc", "btc": "btc",
        "ethereum": "eth", "eth": "eth",
        "usdt": "usdt", "tether": "usdt",
        "binance": "bnb", "bnb": "bnb",
        "solana": "sol", "sol": "sol",
    }
    
    # 检测股票相关查询
    if any(kw in query_lower for kw in ["stock", "股票", "股价", "price", "price of"]):
        # 优先尝试从公司名映射中查找
        tickers_found = []
        for company_name, ticker in company_to_ticker.items():
            if company_name in query_lower:
                tickers_found.append(ticker)
                logger.info(f"从公司名'{company_name}'识别股票代码: {ticker}")
        
        # 如果没有找到公司名，尝试从查询中提取股票代码
        if not tickers_found:
            for pattern in stock_patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        symbol = match[0]
                    else:
                        symbol = match
                    # 过滤掉常见的非股票代码词
                    if symbol.upper() not in ["STOCK", "PRICE", "OF", "THE", "AND", "OR", "FOR", "TO", "IN", "ON", "AT"]:
                        tickers_found.append(symbol)
        
        # 获取股票信息
        for ticker in tickers_found[:num_results]:
            # 判断地区
            region = "HK" if ".HK" in ticker else "US"
            if ".SS" in ticker or ".SZ" in ticker:
                region = "CN"
            
            stock_info = get_stock_price(ticker, region)
            if stock_info:
                contexts.append(stock_info)
                if len(contexts) >= num_results:
                    break
    
    # 检测加密货币相关查询
    if any(kw in query_lower for kw in ["crypto", "加密货币", "bitcoin", "ethereum", "btc", "eth"]):
        for keyword, symbol in crypto_keywords.items():
            if keyword in query_lower and len(contexts) < num_results:
                crypto_info = get_crypto_price(symbol)
                if crypto_info:
                    contexts.append(crypto_info)
                    if len(contexts) >= num_results:
                        break
    
    if not contexts:
        return ""
    
    return "\n\n".join(contexts)

