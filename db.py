import os
from typing import List, Optional, Tuple
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///watchlist.db"

# Create the SQLite engine and configure check_same_thread for Streamlit compatibility
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WatchlistItem(Base):
    """
    Watchlist table schema storing symbols and optional alert prices.
    """
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    alert_price = Column(Float, nullable=True)

def init_db() -> None:
    """Initializes the database by creating all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def add_to_watchlist(symbol: str, alert_price: Optional[float] = None) -> bool:
    """
    Adds a symbol to the watchlist. Returns True if added or updated, False on failure.
    If the symbol already exists, updates the alert price.
    """
    session = SessionLocal()
    try:
        symbol_upper = symbol.strip().upper()
        item = session.query(WatchlistItem).filter_by(symbol=symbol_upper).first()
        if item:
            item.alert_price = alert_price
        else:
            new_item = WatchlistItem(symbol=symbol_upper, alert_price=alert_price)
            session.add(new_item)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding {symbol} to watchlist: {e}")
        return False
    finally:
        session.close()

def remove_from_watchlist(symbol: str) -> bool:
    """
    Removes a symbol from the watchlist.
    Returns True if removed successfully, False if not found or on error.
    """
    session = SessionLocal()
    try:
        symbol_upper = symbol.strip().upper()
        item = session.query(WatchlistItem).filter_by(symbol=symbol_upper).first()
        if item:
            session.delete(item)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error removing {symbol} from watchlist: {e}")
        return False
    finally:
        session.close()

def get_watchlist() -> List[Tuple[str, Optional[float]]]:
    """
    Retrieves all watchlist items as a list of (symbol, alert_price) tuples.
    """
    session = SessionLocal()
    try:
        items = session.query(WatchlistItem).order_by(WatchlistItem.symbol).all()
        return [(item.symbol, item.alert_price) for item in items]
    except Exception as e:
        print(f"Error fetching watchlist: {e}")
        return []
    finally:
        session.close()
