"""
Clean and organize Shopbop clothing data
"""
import csv
import re

INPUT_FILE = "clothing_shopbop.csv"
OUTPUT_FILE = "clothing_shopbop_cleaned.csv"

OUTPUT_HEADERS = [
    "Product page URL",
    "Product name",
    "Brand name",
    "Retailer",
    "Product description",
    "Color",
    "Original price",
    "Sale price",
    "Product image URL",
    "Size availability"
]

# Resellers - not actual brands
RESELLERS = ["What Goes Around Comes Around", "Shopbop Archive"]

# Known luxury brands to extract from product names
LUXURY_BRANDS = [
    "Louis Vuitton", "Gucci", "Chanel", "Prada", "Hermes", "Hermès", 
    "Balenciaga", "Dior", "Fendi", "Celine", "Céline", "Bottega Veneta",
    "Saint Laurent", "YSL", "Givenchy", "Valentino", "Burberry", "Loewe",
    "Versace", "Dolce & Gabbana", "Alexander McQueen", "Miu Miu"
]

def extract_brand_from_product_name(product_name, fallback_brand):
    """Extract actual brand from product name for reseller items"""
    if fallback_brand not in RESELLERS:
        return fallback_brand
    
    for brand in LUXURY_BRANDS:
        if brand.lower() in product_name.lower():
            return brand
    
    return fallback_brand

def extract_prices(price_str, item_page_title):
    """Extract original and sale prices from price string and item_page_title"""
    original_price = ""
    sale_price = ""
    
    # Check item_page_title for sale price (more reliable)
    if item_page_title:
        prev_match = re.search(r'Previous Price [€$]([\d,]+(?:\.\d{2})?)', item_page_title)
        sale_match = re.search(r'Sale Price [€$]([\d,]+(?:\.\d{2})?)', item_page_title)
        
        if prev_match:
            original_price = "€" + prev_match.group(1)
        if sale_match:
            sale_price = "€" + sale_match.group(1)
    
    # If no previous price found, check price column for single price
    if not original_price and price_str:
        prev_match = re.search(r'Previous Price [€$]([\d,]+(?:\.\d{2})?)', price_str)
        if prev_match:
            original_price = "€" + prev_match.group(1)
        else:
            match = re.search(r'[€$]([\d,]+(?:\.\d{2})?)', price_str)
            if match:
                original_price = "€" + match.group(1)
    
    return original_price, sale_price

def clean_row(row):
    item_page_title = row.get("item_page_title", "")
    original_price, sale_price = extract_prices(row.get("price", ""), item_page_title)
    
    # Get raw brand and product name
    raw_brand = row.get("data_1", "") or row.get("data", "")
    product_name = row.get("data_2", "") or row.get("data2", "")
    
    # Extract actual brand (handles reseller items)
    brand = extract_brand_from_product_name(product_name, raw_brand)
    
    # Build product description
    description = f"{brand} {product_name}".strip()
    
    return {
        "Product page URL": row.get("item_page_link", ""),
        "Product name": product_name,
        "Brand name": brand,
        "Retailer": "Shopbop",
        "Product description": description,
        "Color": row.get("Product_Color", ""),
        "Original price": original_price,
        "Sale price": sale_price,
        "Product image URL": row.get("image_1", "") or row.get("image", ""),
        "Size availability": row.get("Product_Size", "")
    }

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        cleaned_rows = []
        for row in reader:
            cleaned = clean_row(row)
            if cleaned["Product name"] and cleaned["Product page URL"]:
                cleaned_rows.append(cleaned)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_HEADERS)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"✅ Cleaned {len(cleaned_rows)} products → '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()
