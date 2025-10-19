"""
AMLSim Transaction Document Generator
Converts transaction data to natural language documents for RAG.
Phase 4: Week 3-4 - AMLSim Integration
"""
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AMLSimDocumentGenerator:
    """
    Generate natural language documents from AMLSim transaction data.
    
    Converts structured transaction data into human-readable documents
    that can be indexed in ChromaDB for RAG queries.
    """
    
    def __init__(self):
        """Initialize document generator."""
        self.generated_documents = 0
        logger.info("AMLSimDocumentGenerator initialized")
    
    def generate_transaction_document(self, transaction: pd.Series,
                                      source_account: pd.Series = None,
                                      dest_account: pd.Series = None,
                                      alert_data: Dict = None) -> str:
        """
        Generate natural language document for a transaction.
        
        Args:
            transaction: Transaction row
            source_account: Source account data (optional)
            dest_account: Destination account data (optional)
            alert_data: Alert information (optional)
            
        Returns:
            Natural language document
        """
        doc_parts = []
        
        # Transaction header
        txn_id = transaction.get('TXN_ID', 'UNKNOWN')
        doc_parts.append(f"Transaction ID: TXN_{txn_id}")
        doc_parts.append("")
        
        # Transaction details
        doc_parts.append("TRANSACTION DETAILS:")
        doc_parts.append(f"- Amount: ${transaction.get('TXN_AMOUNT_ORIG', 0):,.2f}")
        doc_parts.append(f"- Type: {transaction.get('TXN_SOURCE_TYPE_CODE', 'TRANSFER')}")
        doc_parts.append(f"- Timestamp: {transaction.get('start', 0)}")
        doc_parts.append("")
        
        # Account information
        doc_parts.append("TRANSACTION FLOW:")
        source_id = transaction.get('ACCOUNT_ID', 'UNKNOWN')
        dest_id = transaction.get('COUNTER_PARTY_ACCOUNT_NUM', 'UNKNOWN')
        
        doc_parts.append(f"- From: Account {source_id}")
        if source_account is not None:
            country = source_account.get('country', 'Unknown')
            business = source_account.get('business', 'I')
            business_type = 'Individual' if business == 'I' else 'Corporate'
            is_suspicious = source_account.get('suspicious', False)
            
            doc_parts.append(f"  * Type: {business_type}")
            doc_parts.append(f"  * Country: {country}")
            doc_parts.append(f"  * Balance: ${source_account.get('init_balance', 0):,.2f}")
            if is_suspicious:
                doc_parts.append(f"  * Status: SUSPICIOUS ACCOUNT")
        
        doc_parts.append(f"- To: Account {dest_id}")
        if dest_account is not None:
            country = dest_account.get('country', 'Unknown')
            business = dest_account.get('business', 'I')
            business_type = 'Individual' if business == 'I' else 'Corporate'
            is_suspicious = dest_account.get('suspicious', False)
            
            doc_parts.append(f"  * Type: {business_type}")
            doc_parts.append(f"  * Country: {country}")
            doc_parts.append(f"  * Balance: ${dest_account.get('init_balance', 0):,.2f}")
            if is_suspicious:
                doc_parts.append(f"  * Status: SUSPICIOUS ACCOUNT")
        
        doc_parts.append("")
        
        # Alert information
        if alert_data:
            doc_parts.append("SUSPICIOUS ACTIVITY ALERT:")
            doc_parts.append(f"- Alert Type: {alert_data.get('alert_type', 'UNKNOWN')}")
            doc_parts.append(f"- Risk Level: {alert_data.get('risk_level', 'UNKNOWN')}")
            doc_parts.append(f"- Pattern: {alert_data.get('pattern_description', 'Money laundering pattern detected')}")
            doc_parts.append(f"- SAR Filed: YES")
            doc_parts.append("")
        
        # Risk assessment
        doc_parts.append("RISK ASSESSMENT:")
        amount = transaction.get('TXN_AMOUNT_ORIG', 0)
        
        risk_indicators = []
        if amount > 10000:
            risk_indicators.append("Large transaction amount")
        if amount > 9000 and amount < 10000:
            risk_indicators.append("Just below reporting threshold (structuring indicator)")
        if alert_data:
            risk_indicators.append(f"Part of {alert_data.get('alert_type', 'suspicious')} pattern")
        
        if risk_indicators:
            doc_parts.append(f"Risk Indicators: {', '.join(risk_indicators)}")
        else:
            doc_parts.append("Risk Indicators: Normal transaction")
        
        self.generated_documents += 1
        return "\n".join(doc_parts)
    
    def generate_account_summary_document(self, account: pd.Series,
                                         transactions: List[pd.Series] = None,
                                         alerts: List[Dict] = None) -> str:
        """
        Generate comprehensive account summary document.
        
        Args:
            account: Account data
            transactions: List of transactions for this account
            alerts: List of alerts for this account
            
        Returns:
            Natural language account summary
        """
        doc_parts = []
        
        account_id = account.get('ACCOUNT_ID', 'UNKNOWN')
        customer_id = account.get('PRIMARY_CUSTOMER_ID', 'UNKNOWN')
        
        # Account header
        doc_parts.append(f"Account Profile: Account {account_id}")
        doc_parts.append(f"Customer ID: {customer_id}")
        doc_parts.append("")
        
        # Account details
        doc_parts.append("ACCOUNT INFORMATION:")
        business = account.get('business', 'I')
        business_type = 'Individual' if business == 'I' else 'Corporate'
        
        doc_parts.append(f"- Account Type: {business_type}")
        doc_parts.append(f"- Country: {account.get('country', 'Unknown')}")
        doc_parts.append(f"- Initial Balance: ${account.get('init_balance', 0):,.2f}")
        doc_parts.append(f"- Status: {'SUSPICIOUS' if account.get('suspicious', False) else 'NORMAL'}")
        doc_parts.append(f"- Fraud Flag: {'YES' if account.get('isFraud', False) else 'NO'}")
        doc_parts.append("")
        
        # Transaction activity
        if transactions:
            doc_parts.append("TRANSACTION ACTIVITY:")
            doc_parts.append(f"- Total Transactions: {len(transactions)}")
            
            total_sent = sum(t.get('TXN_AMOUNT_ORIG', 0) for t in transactions 
                           if t.get('ACCOUNT_ID') == account_id)
            total_received = sum(t.get('TXN_AMOUNT_ORIG', 0) for t in transactions 
                               if t.get('COUNTER_PARTY_ACCOUNT_NUM') == account_id)
            
            doc_parts.append(f"- Total Sent: ${total_sent:,.2f}")
            doc_parts.append(f"- Total Received: ${total_received:,.2f}")
            doc_parts.append(f"- Net Flow: ${total_sent - total_received:,.2f}")
            doc_parts.append("")
        
        # Alert information
        if alerts:
            doc_parts.append("SUSPICIOUS ACTIVITY ALERTS:")
            for alert in alerts:
                doc_parts.append(f"- {alert.get('alert_type', 'Unknown')} pattern detected")
                doc_parts.append(f"  Risk: {alert.get('risk_level', 'Unknown')}")
            doc_parts.append("")
            doc_parts.append("REGULATORY ACTION REQUIRED:")
            doc_parts.append("- Suspicious Activity Report (SAR) filing recommended")
            doc_parts.append("- Enhanced due diligence required")
            doc_parts.append("- Transaction monitoring increased")
        
        return "\n".join(doc_parts)
    
    def generate_fraud_ring_document(self, fraud_ring: Dict) -> str:
        """
        Generate document describing a fraud ring pattern.
        
        Args:
            fraud_ring: Fraud ring data from extract_fraud_patterns()
            
        Returns:
            Natural language fraud ring description
        """
        doc_parts = []
        
        # Header
        doc_parts.append(f"Fraud Ring Analysis: {fraud_ring['pattern_id']}")
        doc_parts.append("")
        
        # Pattern details
        doc_parts.append("MONEY LAUNDERING PATTERN:")
        doc_parts.append(f"- Pattern Type: {fraud_ring['pattern_type'].upper()}")
        doc_parts.append(f"- Core Account: {fraud_ring['core_account']}")
        doc_parts.append(f"- Ring Members: {fraud_ring['member_count']} accounts")
        doc_parts.append(f"- Transaction Paths: {fraud_ring['transaction_paths']:,}")
        doc_parts.append(f"- Total Amount: ${fraud_ring['total_amount']:,.2f}")
        doc_parts.append(f"- Risk Level: {fraud_ring['risk_level']}")
        doc_parts.append("")
        
        # Transaction flow analysis
        doc_parts.append("TRANSACTION FLOW ANALYSIS:")
        doc_parts.append(f"- Outgoing Transactions: {fraud_ring['outgoing_transactions']}")
        doc_parts.append(f"- Incoming Transactions: {fraud_ring['incoming_transactions']}")
        
        # Pattern interpretation
        pattern_type = fraud_ring['pattern_type']
        doc_parts.append("")
        doc_parts.append("PATTERN INTERPRETATION:")
        
        if pattern_type == 'fan_out':
            doc_parts.append("This is a PLACEMENT/STRUCTURING pattern where a single account")
            doc_parts.append("distributes funds to multiple accounts, likely to:")
            doc_parts.append("- Break large amounts into smaller transactions")
            doc_parts.append("- Avoid regulatory reporting thresholds")
            doc_parts.append("- Obscure the source of funds")
        
        elif pattern_type == 'fan_in':
            doc_parts.append("This is an INTEGRATION/COLLECTION pattern where multiple accounts")
            doc_parts.append("send funds to a single destination, likely to:")
            doc_parts.append("- Consolidate illicit funds")
            doc_parts.append("- Complete the money laundering cycle")
            doc_parts.append("- Prepare funds for legitimate use")
        
        elif pattern_type == 'cycle_hub':
            doc_parts.append("This is a LAYERING HUB pattern where an account both receives and")
            doc_parts.append("distributes funds, likely to:")
            doc_parts.append("- Create complex transaction chains")
            doc_parts.append("- Obscure the money trail")
            doc_parts.append("- Distance funds from illegal source")
        
        else:
            doc_parts.append("This account participates in a complex money laundering network.")
        
        doc_parts.append("")
        doc_parts.append("REGULATORY IMPLICATIONS:")
        doc_parts.append("- Immediate SAR filing required")
        doc_parts.append("- Account freeze recommended")
        doc_parts.append("- Enhanced investigation warranted")
        doc_parts.append("- Potential PMLA (Prevention of Money Laundering Act) violation")
        
        return "\n".join(doc_parts)
    
    def generate_alert_document(self, alert: pd.Series) -> str:
        """
        Generate document for an alert.
        
        Args:
            alert: Alert row data
            
        Returns:
            Natural language alert document
        """
        doc_parts = []
        
        doc_parts.append(f"Suspicious Activity Alert: ALERT_{alert.get('ALERT_KEY', 'UNKNOWN')}")
        doc_parts.append("")
        doc_parts.append("ALERT DETAILS:")
        doc_parts.append(f"- Alert Type: {alert.get('ALERT_TEXT', 'Unknown')}")
        doc_parts.append(f"- Account: {alert.get('ACCOUNT_ID', 'Unknown')}")
        doc_parts.append(f"- Customer: {alert.get('CUSTOMER_ID', 'Unknown')}")
        doc_parts.append(f"- Date: {alert.get('EVENT_DATE', 'Unknown')}")
        doc_parts.append(f"- Check: {alert.get('CHECK_NAME', 'Unknown')}")
        doc_parts.append(f"- Organization: {alert.get('Organization_Type', 'Unknown')}")
        doc_parts.append(f"- Escalated: {alert.get('Escalated_To_Case_Investigation', 'NO')}")
        doc_parts.append("")
        doc_parts.append("This alert was generated by automated AML monitoring systems")
        doc_parts.append("and requires immediate analyst review.")
        
        return "\n".join(doc_parts)
    
    def batch_generate_documents(self, transactions_df: pd.DataFrame,
                                 accounts_df: pd.DataFrame,
                                 alerts_df: pd.DataFrame = None) -> List[Dict[str, Any]]:
        """
        Generate documents for all transactions in batch.
        
        Args:
            transactions_df: All transactions
            accounts_df: All accounts  
            alerts_df: All alerts (optional)
            
        Returns:
            List of dictionaries with document and metadata
        """
        documents = []
        
        logger.info(f"Generating documents for {len(transactions_df)} transactions...")
        
        # Create account lookup
        account_lookup = {row['ACCOUNT_ID']: row for _, row in accounts_df.iterrows()}
        
        # Create alert lookup by account
        alert_lookup = {}
        if alerts_df is not None and not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                account_id = alert['ACCOUNT_ID']
                if account_id not in alert_lookup:
                    alert_lookup[account_id] = []
                alert_lookup[account_id].append({
                    'alert_type': alert.get('ALERT_TEXT', 'unknown'),
                    'risk_level': 'HIGH',
                    'pattern_description': f"{alert.get('CHECK_NAME', 'AML pattern')} detected"
                })
        
        # Generate documents
        for idx, transaction in transactions_df.iterrows():
            source_id = transaction.get('ACCOUNT_ID')
            dest_id = transaction.get('COUNTER_PARTY_ACCOUNT_NUM')
            
            source_account = account_lookup.get(source_id)
            dest_account = account_lookup.get(dest_id)
            
            # Check if either account has alerts
            alert_data = None
            if source_id in alert_lookup:
                alert_data = alert_lookup[source_id][0]
            elif dest_id in alert_lookup:
                alert_data = alert_lookup[dest_id][0]
            
            # Generate document
            document = self.generate_transaction_document(
                transaction,
                source_account,
                dest_account,
                alert_data
            )
            
            # Create metadata
            metadata = {
                'transaction_id': int(transaction.get('TXN_ID', 0)),
                'source_account': int(source_id) if pd.notna(source_id) else 0,
                'dest_account': int(dest_id) if pd.notna(dest_id) else 0,
                'amount': float(transaction.get('TXN_AMOUNT_ORIG', 0)),
                'timestamp': int(transaction.get('start', 0)),
                'transaction_type': str(transaction.get('TXN_SOURCE_TYPE_CODE', 'TRANSFER')),
                'has_alert': alert_data is not None,
                'alert_type': alert_data.get('alert_type') if alert_data else None,
                'source': 'amlsim_transaction'
            }
            
            documents.append({
                'document': document,
                'metadata': metadata,
                'doc_id': f"amlsim_txn_{transaction.get('TXN_ID', idx)}"
            })
            
            if (idx + 1) % 1000 == 0:
                logger.info(f"Generated {idx + 1}/{len(transactions_df)} documents...")
        
        self.generated_documents = len(documents)
        logger.info(f"Generated {self.generated_documents} transaction documents")
        
        return documents


