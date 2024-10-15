from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import requests
import redis.asyncio as redis

app = FastAPI()

redis_client = redis.Redis(host='localhost', port=6379, db=0)

security = HTTPBasic()

class CoinRequest(BaseModel):
    symbol: str

def load_users_from_json() -> Dict:
    """Carrega os usuários a partir de um arquivo JSON."""
    with open("users.json", "r") as f:
        return json.load(f)

def authenticate(credentials: HTTPBasicCredentials):
    """Autentica o usuário com base nas credenciais fornecidas."""
    dados_usuarios = load_users_from_json()
    for user in dados_usuarios["users"]:
        if credentials.username == user["username"] and credentials.password == user["password"]:
            return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Basic"},
    )

def get_data_from_selenium(symbol: str) -> str:
    """Busca dados do Mercado Bitcoin"""
    url = f"https://ssstore.mercadobitcoin.com.br/api/v1/marketplace/product/unlogged?symbol={symbol}&limit=20&offset=0&order=desc&sort=release_date"

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as driver:
        driver.get(url)
        return driver.page_source

def extract_json_from_html(html_content: str) -> Optional[Dict]:
    """Extrai o JSON do conteudo HTML"""
    soup = BeautifulSoup(html_content, "html.parser")
    pre_tag = soup.find("pre")
    return json.loads(pre_tag.text) if pre_tag else None

def get_current_dollar_price() -> float:
    """Obtem a taxa de câmbio atual USD para BRL."""
    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    response = requests.get(url)
    data = response.json()
    return float(data["USDBRL"]["bid"])

def get_data_from_coingecko(symbol: str) -> Optional[Dict]:
    """Busca dados da API CoinGecko."""
    coingecko_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=brl&symbol={symbol.lower()}"
    response = requests.get(coingecko_url)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]
    return None

async def get_currency_from_cache(symbol: str) -> Dict:
    """BUsca dados de cache ou das APIs externas."""
    cached_data = await redis_client.get(symbol)
    if cached_data:
        return json.loads(cached_data)
    
    try:
        page_source = get_data_from_selenium(symbol)
        json_data = extract_json_from_html(page_source)
        if json_data and "response_data" in json_data and "products" in json_data["response_data"]:
            product_info = json_data["response_data"]["products"][0]
        else:
            raise Exception("API do Mercado Bitcoin não está disponível")
    except Exception:
        product_info = get_data_from_coingecko(symbol)
        if not product_info:
            return {"error": "Falha ao obter dados das APIs do Mercado Bitcoin e CoinGecko"}

    # Armazenar no cache por 60 segundos no Redis
    await redis_client.set(symbol, json.dumps(product_info), ex=60)
    return product_info

@app.post("/coin_infos/")
async def get_currency_price(
    request: CoinRequest, credentials: HTTPBasicCredentials = Depends(security)
) -> Dict:
    """Busca e retorna as informações de preço da moeda"""
    authenticate(credentials)
    
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dados_preco = await get_currency_from_cache(request.symbol)
    
    if "error" in dados_preco:
        return dados_preco

    dollar_price = get_current_dollar_price()
    coin_price = dados_preco.get("market_price") or dados_preco.get("current_price", "Preço indisponível")
    
    return {
        "coin_name": dados_preco.get("name", "Nome indisponível"),
        "symbol": request.symbol.upper(),
        "coin_price": coin_price,
        "coin_price_dolar": dollar_price,
        "date_consult": data_atual,
    }
