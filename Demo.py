from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import time

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['pharmacity']
client.drop_database('pharmacity')
products_collection = db['products']  # Tên collection

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
    time.sleep(2)

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

    try:
        product_img = driver.find_element(By.TAG_NAME, 'img').get_attribute('src')
    except:
        product_img = "N/A"

    # Lấy thương hiệu
    try:
        product_brand = driver.find_element(By.CSS_SELECTOR, "div.md\\:text-base").text
    except:
        product_brand = "N/A"

    # Lấy giá bán
    try:
        product_price = driver.find_element(By.TAG_NAME, 'h3').text
    except:
        product_price = "N/A"

    # Lấy lượt yêu thích (nếu có)
    try:
        product_likes = driver.find_element(By.CSS_SELECTOR, 'div.space-x-1:nth-child(2) > p:nth-child(1)').text
    except:
        product_likes = "N/A"

    # Lấy số lượng bán (nếu có)
    try:
        product_sold = driver.find_element(By.CSS_SELECTOR, 'p.text-sm:nth-child(3)').text
    except:
        product_sold = "N/A"

    if product_price == "N/A":
        product_type = "Kê đơn"
    else:
        product_type = "Không kê đơn"

    # Tạo từ điển lưu thông tin sản phẩm
    product_data = {
        "Mã sản phẩm": product_code,
        "Tên sản phẩm": product_name,
        "Loại sản phẩm": product_type,
        "Hình ảnh": product_img,
        "Thương hiệu": product_brand,
        "Giá bán": product_price,
        "Lượt yêu thích": product_likes,
        "Số lượng bán": product_sold,
        "Link sản phẩm": product_link
    }

    # Lưu vào MongoDB
    products_collection.insert_one(product_data)
    print(f"Đã lưu: {product_name}")


# Hàm nhấn nút "Xem thêm" để tải thêm sản phẩm
def load_more_products():
    try:
        load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Xem thêm')]")
        load_more_button.click()
        time.sleep(3)  # Đợi trang tải thêm sản phẩm
    except:
        print("Không còn sản phẩm để tải thêm.")

# Hàm cuộn trang xuống cuối để tải thêm sản phẩm
def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Đợi một chút để các sản phẩm tải xuống


# Lấy danh sách link sản phẩm
def get_product_links():
    product_links = []
    products = driver.find_elements(By.CSS_SELECTOR, "a:has(h3.line-clamp-2.h-10.text-sm.font-semibold)")
    for product in products:
        product_link = product.get_attribute("href")
        product_links.append(product_link)
    return product_links


# Cào dữ liệu từ trang đầu và tiếp tục nhấn "Xem thêm"
while True:
    # Lấy danh sách link sản phẩm trên trang hiện tại
    links = get_product_links()

    # Cào dữ liệu từng sản phẩm
    for link in links:
        scrape_product(link)

    # Cuộn xuống cuối trang để tải thêm sản phẩm
    scroll_down()

    # Nhấn nút "Xem thêm" nếu có
    # try:
    #     load_more_products()
    # except:
    #     break  # Nếu không còn nút "Xem thêm", thoát khỏi vòng lặp

driver.quit()
