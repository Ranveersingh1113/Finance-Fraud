#!/usr/bin/env python3
"""
Setup script to create SEBI directory structure and provide guidance.
"""

import os
from pathlib import Path

def create_sebi_directory_structure():
    """Create the recommended SEBI directory structure."""
    
    base_dir = Path("./data/sebi")
    
    # Create subdirectories
    directories = [
        "adjudication_orders",
        "investigation_reports", 
        "press_releases",
        "other"
    ]
    
    print("Creating SEBI directory structure...")
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {dir_path}")
        
        # Create a README file in each directory
        readme_content = f"""# {directory.replace('_', ' ').title()}

Place your SEBI {directory.replace('_', ' ')} files in this directory.

Supported formats:
- PDF files (.pdf)
- Text files (.txt)
- Word documents (.doc, .docx)
- Files without extensions (plain text)

Recommended naming convention:
- Use descriptive names: insider_trading_company_name_2024.pdf
- Include date information: document_2024_09.pdf
- Group by violation type: market_manipulation_xyz.pdf

Example files:
- adjudication_order_insider_trading_2024.pdf
- investigation_report_hindenburg_adani_2024.pdf
- press_release_enforcement_september_2024.pdf
"""
        
        readme_path = dir_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    # Create main README
    main_readme_content = """# SEBI Documents Directory

This directory contains manually downloaded SEBI documents for processing.

## Directory Structure

- `adjudication_orders/` - SEBI Adjudication Orders (PDF files)
- `investigation_reports/` - Investigation Reports and Committee Reports  
- `press_releases/` - Press Releases and Circulars
- `other/` - Other SEBI documents

## Getting Started

1. Download SEBI documents from:
   - Adjudication Orders: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=6
   - Investigation Reports: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=4&ssid=38&smid=35
   - Press Releases: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=6&ssid=23&smid=0

2. Place downloaded files in appropriate subdirectories

3. Run the processing script:
   ```bash
   python test_sebi_file_processing.py
   ```

## File Processing

The system will automatically:
- Extract text from PDF files
- Detect document types
- Extract violation types and entities
- Generate metadata
- Create searchable chunks for RAG

## Supported File Types

- PDF files (.pdf) - Most common
- Text files (.txt) - Plain text
- Word documents (.doc, .docx)
- Files without extensions (plain text)

## Naming Recommendations

Use descriptive filenames with date information:
- `insider_trading_nucleus_software_2024.pdf`
- `market_manipulation_xyz_company_2024.pdf`
- `investigation_report_hindenburg_adani_2024.pdf`
- `press_release_enforcement_september_2024.pdf`
"""
    
    main_readme_path = base_dir / "README.md"
    with open(main_readme_path, 'w', encoding='utf-8') as f:
        f.write(main_readme_content)
    
    print(f"\n✓ Created main README: {main_readme_path}")
    
    # Create a sample test file
    sample_file = base_dir / "adjudication_orders" / "sample_document.txt"
    sample_content = """SEBI Adjudication Order

IN THE MATTER OF SUSPECTED INSIDER TRADING ACTIVITY

This is a sample SEBI adjudication order document. 

The order relates to suspected insider trading activity in the scrip of ABC Company Limited. The investigation revealed violations of SEBI (Prohibition of Insider Trading) Regulations, 2015.

VIOLATIONS FOUND:
- Insider trading based on unpublished price sensitive information
- Failure to maintain confidentiality of material information
- Trading in securities while in possession of UPSI

PENALTY IMPOSED:
- Monetary penalty of Rs. 5,00,000 (Five Lakh Rupees)
- Cease and desist from further violations

Date: 15 September 2024
Order No: AO/2024/001
"""
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"✓ Created sample document: {sample_file}")
    
    print(f"\n🎉 SEBI directory structure created successfully!")
    print(f"📁 Base directory: {base_dir}")
    print(f"📋 Next steps:")
    print(f"   1. Download SEBI documents and place them in appropriate subdirectories")
    print(f"   2. Run: python test_sebi_file_processing.py")
    print(f"   3. Check the generated CSV file for processed results")

def main():
    """Main setup function."""
    print("=== SEBI Directory Setup ===")
    create_sebi_directory_structure()

if __name__ == "__main__":
    main()




