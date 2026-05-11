import yfinance as yf
import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session
from models import Asset

def add_asset(db: Session, ticker: str, quantity: float):
    # Regra: Garante sufixo .SA para ativos B3
    ticker = ticker.upper().strip()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    
    asset = db.query(Asset).filter(Asset.ticker == ticker).first()
    if asset:
        asset.quantity += quantity
    else:
        asset = Asset(ticker=ticker, quantity=quantity)
        db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

def delete_asset(db: Session, ticker: str):
    ticker = ticker.upper().strip()
    if not ticker.endswith('.SA'):
        ticker += '.SA'
    asset = db.query(Asset).filter(Asset.ticker == ticker).first()
    if asset:
        db.delete(asset)
        db.commit()

def get_all_assets(db: Session):
    return db.query(Asset).all()

# Cache de 60 segundos para evitar block de IP e otimizar velocidade
@st.cache_data(ttl=60)
def fetch_market_data(tickers: list[str]) -> dict:
    if not tickers:
        return {}
    
    try:
        # Busca em lote otimizada
        data = yf.download(tickers, period="1d", progress=False)
        latest_prices = {}
        
        for ticker in tickers:
            try:
                # yfinance retorna formato diferente se for 1 ticker ou múltiplos
                if len(tickers) == 1:
                    price = float(data['Close'].iloc[-1])
                else:
                    price = float(data['Close'][ticker].iloc[-1])
                latest_prices[ticker] = price
            except Exception:
                latest_prices[ticker] = 0.0
                
        return latest_prices
    except Exception as e:
        print(f"Erro ao buscar cotações no yfinance: {e}")
        return {}

def get_portfolio_summary(db: Session):
    assets = get_all_assets(db)
    if not assets:
        return pd.DataFrame(), 0.0
    
    tickers = [asset.ticker for asset in assets]
    market_data = fetch_market_data(tickers)
    
    portfolio_data = []
    total_patrimony = 0.0
    
    for asset in assets:
        price = market_data.get(asset.ticker, 0.0)
        if pd.isna(price):
            price = 0.0
            
        total_value = price * asset.quantity
        total_patrimony += total_value
        
        portfolio_data.append({
            "Ticker": asset.ticker,
            "Quantidade": asset.quantity,
            "Preço Atual (R$)": price,
            "Valor Total (R$)": total_value
        })
        
    df = pd.DataFrame(portfolio_data)
    return df, total_patrimony
