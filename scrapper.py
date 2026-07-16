import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. Target URL for Jumia Egypt searching for "omega 3"
url = "https://www.jumia.com.eg/catalog/?q=omega+3"

# 2. Add Headers to mimic a real browser session and avoid getting blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Connecting to Jumia Egypt...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Connection successful! Parsing HTML...")
    soup = BeautifulSoup(response.text, "html.parser")
    
    # List to store scraped products
    product_list = []
    
    # Jumia wraps each product in an <article> tag with class "prd"
    products = soup.find_all("article", class_="prd")
    
    for product in products:
        try:
            # Extract product name
            name = product.find("h3", class_="name").text.strip()
            
            # Extract product price
            price = product.find("div", class_="prc").text.strip()
            
            # Extract product link (Jumia uses relative links, so we add the domain)
            relative_link = product.find("a", class_="core")["href"]
            full_link = "https://www.jumia.com.eg" + relative_link
            
            # Append to our list
            product_list.append({
                "Product Name": name,
                "Price": price,
                "Link": full_link
            })
        except AttributeError:
            # Skip product card if any essential element (like price or name) is missing
            continue
            
    # 3. Create DataFrame and export
    if product_list:
        df = pd.DataFrame(product_list)
        print(f"\nSuccessfully scraped {len(df)} products!")
        print("\n--- Sample of Scraped Data ---")
        print(df.head())
        
        # Save with 'utf-8-sig' to ensure perfect display in Excel
        df.to_csv("jumia_omega3_prices.csv", index=False, encoding="utf-8-sig")
        print("\nData saved successfully to: jumia_omega3_prices.csv")
    else:
        print("No products found. Jumia HTML structure might have changed.")
else:
    print(f"Failed to retrieve page. Status Code: {response.status_code}")