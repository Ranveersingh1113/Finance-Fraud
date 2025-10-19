"""
AMLSim Data Loader for Financial Intelligence Platform.
Loads and parses AMLSim transaction network data.
Phase 4: Week 3 - AMLSim Integration
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AMLSimLoader:
    """
    Load and parse AMLSim transaction data.
    
    Data Files:
    - accounts.csv: Account information
    - tx.csv: Account-to-account transactions
    - alerts.csv: Suspicious pattern alerts
    - cash_tx.csv: Cash transactions
    """
    
    def __init__(self, data_directory: str = "./data/amlsim"):
        """
        Initialize AMLSim data loader.
        
        Args:
            data_directory: Directory containing AMLSim CSV files
        """
        self.data_directory = Path(data_directory)
        logger.info(f"AMLSimLoader initialized: {data_directory}")
    
    def load_accounts(self) -> pd.DataFrame:
        """
        Load account data.
        
        Returns:
            DataFrame with account information
        """
        file_path = self.data_directory / "accounts.csv"
        
        if not file_path.exists():
            logger.error(f"Accounts file not found: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} accounts")
            return df
        except Exception as e:
            logger.error(f"Error loading accounts: {e}")
            return pd.DataFrame()
    
    def load_transactions(self) -> pd.DataFrame:
        """
        Load transaction data.
        
        Returns:
            DataFrame with account-to-account transactions
        """
        file_path = self.data_directory / "tx.csv"
        
        if not file_path.exists():
            logger.error(f"Transactions file not found: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} transactions")
            return df
        except Exception as e:
            logger.error(f"Error loading transactions: {e}")
            return pd.DataFrame()
    
    def load_alerts(self) -> pd.DataFrame:
        """
        Load alert data.
        
        Returns:
            DataFrame with suspicious activity alerts
        """
        file_path = self.data_directory / "alerts.csv"
        
        if not file_path.exists():
            logger.warning(f"Alerts file not found: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} alerts")
            return df
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
            return pd.DataFrame()
    
    def load_cash_transactions(self) -> pd.DataFrame:
        """
        Load cash transaction data.
        
        Returns:
            DataFrame with cash transactions
        """
        file_path = self.data_directory / "cash_tx.csv"
        
        if not file_path.exists():
            logger.warning(f"Cash transactions file not found: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} cash transactions")
            return df
        except Exception as e:
            logger.error(f"Error loading cash transactions: {e}")
            return pd.DataFrame()
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all AMLSim data files.
        
        Returns:
            Dictionary with all dataframes
        """
        return {
            'accounts': self.load_accounts(),
            'transactions': self.load_transactions(),
            'alerts': self.load_alerts(),
            'cash_transactions': self.load_cash_transactions()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of loaded data.
        
        Returns:
            Dictionary with summary statistics
        """
        data = self.load_all_data()
        
        accounts_df = data['accounts']
        transactions_df = data['transactions']
        alerts_df = data['alerts']
        cash_df = data['cash_transactions']
        
        summary = {
            'accounts': len(accounts_df),
            'transactions': len(transactions_df),
            'alerts': len(alerts_df),
            'cash_transactions': len(cash_df)
        }
        
        if not accounts_df.empty:
            summary['suspicious_accounts'] = accounts_df['suspicious'].sum() if 'suspicious' in accounts_df.columns else 0
            summary['account_types'] = accounts_df['business'].value_counts().to_dict() if 'business' in accounts_df.columns else {}
        
        if not alerts_df.empty:
            summary['alert_types'] = alerts_df['ALERT_TEXT'].value_counts().to_dict() if 'ALERT_TEXT' in alerts_df.columns else {}
        
        return summary

