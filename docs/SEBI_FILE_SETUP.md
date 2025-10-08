# SEBI File Processing Setup Guide

This guide explains how to set up and use the SEBI file processing system for manually downloaded SEBI documents.

## Overview

The SEBI file processing system allows you to process manually downloaded SEBI documents (PDFs, text files, etc.) instead of web scraping. This approach is more reliable and allows you to work with specific documents of interest.

## Directory Structure

Create the following directory structure in your project:

```
data/
└── sebi/
    ├── adjudication_orders/          # Place adjudication order PDFs here
    ├── investigation_reports/        # Place investigation report PDFs here
    ├── press_releases/               # Place press release files here
    └── other/                        # Place other SEBI documents here
```

## Supported File Types

The system supports the following file formats:

- **PDF files** (`.pdf`) - Most common format for SEBI orders
- **Text files** (`.txt`) - Plain text documents
- **Word documents** (`.doc`, `.docx`) - Microsoft Word files
- **Files without extensions** - Plain text files without extensions

## Getting SEBI Documents

### 1. Adjudication Orders
- **Source**: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=6
- **What to download**: PDF files of adjudication orders
- **Naming**: Use descriptive names like `insider_trading_2024.pdf` or `market_manipulation_company_name.pdf`

### 2. Investigation Reports
- **Source**: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=4&ssid=38&smid=35
- **What to download**: Major investigation reports and committee reports
- **Naming**: Use names like `hindenburg_adani_report_2024.pdf`

### 3. Press Releases
- **Source**: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=6&ssid=23&smid=0
- **What to download**: Relevant press releases about enforcement actions
- **Naming**: Use names like `press_release_2024_09.pdf`

## Usage

### Basic File Processing

```python
from src.data.sebi_file_processor import SEBIFileProcessor

# Initialize processor
processor = SEBIFileProcessor(sebi_directory="./data/sebi")

# Process all files in the directory
documents = processor.process_all_files()

# Save results to CSV
processor.save_documents_to_csv(documents, "sebi_documents.csv")

# Get processing summary
summary = processor.get_processing_summary(documents)
print(summary)
```

### Full Pipeline Integration

```python
from src.data.ingestion import DataIngestion

# Initialize data ingestion
data_ingestion = DataIngestion()

# Run the complete SEBI pipeline
results = data_ingestion.run_sebi_pipeline(load_from_files=True)

# Access results
documents = results['loaded_documents']
chunks = results['processed_chunks']
summary = results['summary']
```

### Using with RAG Engine

```python
from src.data.ingestion import DataIngestion
from src.core.rag_engine import BaselineRAGEngine

# Load and process SEBI data
data_ingestion = DataIngestion()
data_ingestion.run_sebi_pipeline(load_from_files=True)

# Initialize RAG engine
rag_engine = BaselineRAGEngine()

# Load processed chunks into RAG system
chunks = data_ingestion.load_processed_sebi_chunks()
rag_engine.add_sebi_chunks(chunks)

# Search for fraud-related information
results = rag_engine.search_sebi_documents(
    query="insider trading penalties",
    n_results=5,
    document_type="adjudication_order",
    violation_type="insider_trading"
)
```

## File Organization Tips

### 1. Use Descriptive Filenames
```
adjudication_orders/
├── insider_trading_nucleus_software_2024.pdf
├── market_manipulation_xyz_company_2024.pdf
└── disclosure_violation_abc_corp_2024.pdf

investigation_reports/
├── hindenburg_adani_investigation_2024.pdf
└── committee_report_market_manipulation_2024.pdf

press_releases/
├── enforcement_actions_september_2024.pdf
└── regulatory_updates_2024.pdf
```

### 2. Include Date Information
- Add year to filename: `document_2024.pdf`
- Add month if relevant: `document_2024_09.pdf`
- Use consistent date format: `YYYY-MM-DD` or `YYYY_MM_DD`

### 3. Group by Document Type
- Create subdirectories for different document types
- Use consistent naming conventions
- Add metadata in filenames when possible

## Testing

Run the test script to verify everything is working:

```bash
python test_sebi_file_processing.py
```

This will:
1. Scan for SEBI files in the directory
2. Process all found files
3. Generate a processing summary
4. Save results to CSV

## Document Types Detected

The system automatically detects document types based on filename and content patterns:

- **adjudication_order**: Orders from SEBI Adjudicating Officers
- **investigation_report**: Investigation reports and committee reports
- **press_release**: Press releases and circulars

## Metadata Extraction

The system automatically extracts:

- **Violation Types**: insider_trading, market_manipulation, disclosure_violations, etc.
- **Entities**: Company names, individual names, penalties, dates
- **Financial Terms**: Revenue, profit, assets, securities, etc.
- **Penalty Information**: Amounts, types, enforcement actions

## Troubleshooting

### Common Issues

1. **No files found**
   ```
   WARNING: No SEBI files found in ./data/sebi directory
   ```
   - Ensure files are placed in the correct directory
   - Check file extensions are supported
   - Verify file permissions

2. **PDF extraction fails**
   ```
   WARNING: PyPDF2 extraction failed
   ```
   - The system tries multiple PDF libraries automatically
   - Most PDFs should work with at least one method
   - Check if PDF is password-protected

3. **Encoding issues**
   ```
   WARNING: Could not read file with any encoding
   ```
   - The system tries multiple encodings automatically
   - Ensure files are valid text/PDF files
   - Check file is not corrupted

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your processing code here
```

## Performance Tips

1. **Batch Processing**: Process files in smaller batches for large collections
2. **File Size**: Very large PDFs may take longer to process
3. **Memory Usage**: Monitor memory usage when processing many files
4. **Storage**: Ensure adequate disk space for processed outputs

## Next Steps

After processing your SEBI documents:

1. **Review Results**: Check the generated CSV file for accuracy
2. **Integrate with RAG**: Load processed chunks into your RAG system
3. **Build Insights**: Use the extracted metadata for fraud pattern analysis
4. **Expand Collection**: Add more documents to improve coverage

## Example Workflow

```bash
# 1. Download SEBI documents manually and place in ./data/sebi/

# 2. Test file processing
python test_sebi_file_processing.py

# 3. Run full pipeline
python -c "
from src.data.ingestion import DataIngestion
data_ingestion = DataIngestion()
results = data_ingestion.run_sebi_pipeline()
print(f'Processed {len(results[\"loaded_documents\"])} documents')
"

# 4. Use with RAG system
python -c "
from src.core.rag_engine import BaselineRAGEngine
rag = BaselineRAGEngine()
# Load and search SEBI data...
"
```




