from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import time
import re

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['pharmacity']
client.drop_database('pharmacity')

products_collection = db['products']
sales_collection = db['sales']
products_detail = db['details']

# Khởi tạo WebDriver cho Firefox
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

# Truy cập vào trang dược phẩm
driver.get("https://www.pharmacity.vn/duoc-pham")

# Đợi trang tải
time.sleep(3)


# Hàm cào dữ liệu từng sản phẩm
def scrape_product(product_link):
    # Mở link sản phẩm
    driver.get(product_link)
    time.sleep(3)

    # Lấy mã sản phẩm
    try:
        product_code = driver.find_element(By.CSS_SELECTOR, "p.text-sm.leading-5.text-neutral-600").text
    except:
        product_code = "N/A"

    # Lấy tên sản phẩm
    try:
        product_name = driver.find_element(By.CSS_SELECTOR, "h1.text-neutral-900.font-semibold").text
    except:
        product_name = "N/A"

    # Lấy hình ảnh
    try:
        product_img = driver.find_element(By.XPATH,
                                          '//*[@id="mainContent"]/div/div[1]/div[3]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/img').get_attribute(
            'src')
    except:
        product_img = "N/A"

    # Lấy nơi sản xuất
    try:
        product_origin = driver.find_element(By.CSS_SELECTOR,
                                            '#mainContent > div > div:nth-child(1) > div.relative.grid.grid-cols-1.gap-6.md\\:container.md\\:grid-cols-\\[min\\(60\\%\\,calc\\(555rem\\/16\\)\\)\\,1fr\\].md\\:pt-6.lg\\:grid-cols-\\[min\\(72\\%\\,calc\\(888rem\\/16\\)\\)\\,1fr\\] > div.grid.md\\:gap-6 > div.grid.grid-cols-1.items-start.md\\:gap-6.lg\\:grid-cols-2.xl\\:grid-cols-2 > div:nth-child(2) > div > div.flex.flex-col.px-4.md\\:px-0 > div.gap-3.md\\:gap-4.mb-3.grid.md\\:mb-4 > div.grid.gap-3.md\\:gap-2 > div:nth-child(5) > div').text
    except:
        product_origin = "N/A"

    # Lấy thương hiệu
    try:
        product_brand = driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div[1]/div[3]/div[1]/div[1]/div[2]/div/div[3]/div[2]/div/a').text
    except:
        product_brand = "N/A"

    # Lấy giá bán
    try:
        product_price = driver.find_element(By.TAG_NAME, 'h3').text
        # Sử dụng regex để loại bỏ các ký tự không phải số và dấu phân cách thập phân
        # Giữ lại số và dấu chấm (.)
        cleaned_price_str = re.sub(r'[^\d.]', '', product_price)
        product_price = float(cleaned_price_str) * 1000
    except:
        product_price = "N/A"

    # Lấy lượt yêu thích
    try:
        product_likes = driver.find_element(By.CSS_SELECTOR, 'div.space-x-1:nth-child(2) > p:nth-child(1)').text
        cleaned_likes_str = re.sub(r'[^\d.]', '', product_likes)
        product_likes = float(cleaned_likes_str) * 1000
    except:
        product_likes = "N/A"

    # Lấy số lượng bán
    try:
        product_sold = driver.find_element(By.CSS_SELECTOR, 'p.text-sm:nth-child(3)').text
        cleaned_sold_str = re.sub(r'[^\d.]', '', product_sold)
        product_sold = float(cleaned_sold_str) * 1000
    except:
        product_sold = "N/A"

    # Lấy loại thuốc
    try:
        product_type = driver.find_element(By.CSS_SELECTOR, "div.md\\:text-base").text
    except:
        product_type = "N/A"

    # Lấy quy cách
    try:
        product_spec = driver.find_element(By.CSS_SELECTOR, "h1.text-neutral-900.font-semibold").text
        ps = re.search(r'\((.*?)\)', product_spec)
        product_spec = ps.group(1)
    except:
        product_spec = "N/A"

    # Lấy hoạt tính
    try:
        active_element = driver.find_element(By.CSS_SELECTOR, "#mainContent > div > div:nth-child(1) > div.relative.grid.grid-cols-1.gap-6.md\\:container.md\\:grid-cols-\\[min\\(60\\%\\,calc\\(555rem\\/16\\)\\)\\,1fr\\].md\\:pt-6.lg\\:grid-cols-\\[min\\(72\\%\\,calc\\(888rem\\/16\\)\\)\\,1fr\\] > div.grid.md\\:gap-6 > div.grid.grid-cols-1.items-start.md\\:gap-6.lg\\:grid-cols-2.xl\\:grid-cols-2 > div:nth-child(2) > div > div.flex.flex-col.px-4.md\\:px-0 > div.gap-3.md\\:gap-4.mb-3.grid.md\\:mb-4 > div.grid.gap-3.md\\:gap-2 > div:nth-child(2) > div").text
    except:
        active_element = "N/A"

    #Lấy chỉ định
    try:
        indication = driver.find_element(By.CSS_SELECTOR, "#mainContent > div > div:nth-child(1) > div.relative.grid.grid-cols-1.gap-6.md\\:container.md\\:grid-cols-\\[min\\(60\\%\\,calc\\(555rem\\/16\\)\\)\\,1fr\\].md\\:pt-6.lg\\:grid-cols-\\[min\\(72\\%\\,calc\\(888rem\\/16\\)\\)\\,1fr\\] > div.grid.md\\:gap-6 > div.grid.grid-cols-1.items-start.md\\:gap-6.lg\\:grid-cols-2.xl\\:grid-cols-2 > div:nth-child(2) > div > div.flex.flex-col.px-4.md\\:px-0 > div.gap-3.md\\:gap-4.mb-3.grid.md\\:mb-4 > div.grid.gap-3.md\\:gap-2 > div:nth-child(3) > div").text
    except:
        indication = "N/A"

    # Tạo từ điển lưu thông tin sản phẩm
    product_data = {
        "Product_ID": product_code,
        "Product_Name": product_name,
        "Img": product_img,
        "Brand": product_brand,
        "Price": product_price,
        "Link": product_link
    }
    sale_data = {
        "Product_ID": product_code,
        "Product_Name": product_name,
        "Likes": product_likes,
        "Sold": product_sold
    }

    detail_data = {
        "Product_ID": product_code,
        "Product_Name": product_name,
        "Type": product_type,
        "Product_Spec": product_spec,
        "Product_origin": product_origin,
        "Active_element": active_element,
        "Indication": indication
    }

    # Lưu vào MongoDB
    products_collection.insert_one(product_data)
    products_detail.insert_one(detail_data)
    if product_type == "Thuốc không kê đơn":
        sales_collection.insert_one(sale_data)

    print(f"Đã lưu: {product_name}")

# Hàm cuộn xuống cuối trang và nhấn nút xem thêm
def load_all_products():
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        try:
            # Tìm nút "Xem thêm" và nhấn vào nó
            load_more_button = driver.find_element(By.XPATH, "//button[span[contains(text(), 'Xem thêm')]]")
            load_more_button.click()
            time.sleep(2)
        except:
            break

# Lấy danh sách link sản phẩm
def get_product_links():
    product_links = []
    try:
        products = driver.find_elements(By.CSS_SELECTOR, "a:has(h3.line-clamp-2.h-10.text-sm.font-semibold)")
        for product in products:
            product_link = product.get_attribute("href")
            product_links.append(product_link)
            print(product_link)
    except Exception as e:
        print(f"Error: {e}")
    return product_links




load_all_products()
links = get_product_links()
#print(f'Tổng số link sản phẩm {len(links)} \n')

# Cào dữ liệu từ trang web
for link in links:
    scrape_product(link)
driver.quit()

