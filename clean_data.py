"""
Clean and organize Shopbop jewelry data
"""
import csv
import re

INPUT_FILE = "jewellery_shopbop.csv"
OUTPUT_FILE = "jewellery_shopbop_cleaned.csv"

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

def extract_price(price_str):
    """Extract numeric price from string like 'Previous Price $415.00' or '$249.00'"""
    if not price_str:
        return ""
    match = re.search(r'\$(\d+(?:\.\d{2})?)', price_str)
    return f"${match.group(1)}" if match else ""

def extract_original_price(price_str):
    """Extract original/previous price"""
    if not price_str:
        return ""
    match = re.search(r'Previous Price \$(\d+(?:\.\d{2})?)', price_str)
    return f"${match.group(1)}" if match else ""

def extract_color(color_str):
    """Clean color string like 'Color: Tan' to 'Tan'"""
    if not color_str:
        return ""
    return color_str.replace("Color: ", "").strip()

def get_first_image(image_str):
    """Get only the first image URL from a multi-line string"""
    if not image_str:
        return ""
    return image_str.split('\n')[0].strip()

def clean_row(row):
    """Transform raw row to cleaned format"""
    # Extract original price from the 'price' column
    original_price = extract_original_price(row.get('price', ''))
    
    # Sale price from lowPrice or price_1
    sale_price_raw = row.get('lowPrice', '') or row.get('price_1', '')
    if sale_price_raw and not sale_price_raw.startswith('$'):
        sale_price = f"${sale_price_raw}"
    else:
        sale_price = sale_price_raw
    
    # If no original price, use sale price as original
    if not original_price and sale_price:
        original_price = sale_price
    
    return {
        "Product page URL": row.get('item_page_link', '') or row.get('url_1', ''),
        "Product name": row.get('name', '') or row.get('title', '') or row.get('name_2', ''),
        "Brand name": row.get('name_1', '') or row.get('data', ''),
        "Retailer": "Shopbop",
        "Product description": row.get('Product_Description', '') or row.get('Brand_Description', '')[:200] if row.get('Brand_Description') else "",
        "Color": extract_color(row.get('product_color', '')),
        "Original price": original_price,
        "Sale price": sale_price if sale_price != original_price else "",
        "Product image URL": get_first_image(row.get('image', '') or row.get('image_2', '')),
        "Size availability": row.get('product_size', '') or row.get('product_sizes', '')
    }

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        cleaned_rows = []
        for row in reader:
            cleaned = clean_row(row)
            # Skip rows without essential data
            if cleaned["Product name"] and cleaned["Product page URL"]:
                cleaned_rows.append(cleaned)
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_HEADERS)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    
    print(f"✅ Cleaned {len(cleaned_rows)} products → '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()
