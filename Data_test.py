from pymongo import MongoClient
import time

client = MongoClient("mongodb://localhost:27017/")
db = client['pharmacity']
products_collection = db['products']
sales_collection = db['sales']
products_detail = db['details']

# 1.Hiện tất cả các sản phẩm và số lượng sản phẩm trong collection 'products'
for product in db.products.find():
    print(product)
sl = db.products.count_documents({})
print(f'Tổng số sản phẩm trong products là: {sl}')
print('\n')

# 2.Tìm sản phẩm không kê đơn có giá cao nhất
highest_price = db.products.find({"Type": "Thuốc không kê đơn"}).sort("Price", -1).limit(1)
print("Thuốc không kê đơn có giá cao nhất:")
for product in highest_price:
    print(product)
print('\n')

# 3.Tìm sản phẩm không kê đơn có giá thấp nhất
lowest_price = db.products.find({"Type": "Thuốc không kê đơn"}).sort("Price", 1).limit(1)
print("Thuốc không kê đơn có giá thấp nhất:")
for product in lowest_price:
    print(product)
print('\n')

# 4.Lấy sản phẩm có thành phần hoạt tính chứa "Levocetirizin"
timhoattinh = db.details.find({"Active_element": {"$regex": "Levocetirizin", "$options": "i"}})
for tim in timhoattinh:
    print(f'Thuốc có hoạt tính Levocetirizin là {tim}')
print('\n')

# 5.Đếm số sản phẩm có nguồn gốc từ "Việt Nam"

fromVN = db.details.count_documents({"Product_origin": "Việt Nam"})
print(f'Tổn số sản phẩm đến từ VN là {fromVN}')
print('\n')

# 6.Đếm số sản phẩm không có nguồn gốc từ "Việt Nam"
notfromVN = db.details.count_documents({"Product_origin": {"$ne":"Việt Nam"}})
print(f'Tổn số sản phẩm không đến từ VN là {notfromVN}')
print('\n')

# 7.Tìm sản phẩm có giá bán hơn 100k
print('Sản phẩm có giá bán hơn 100k:')
for p in db.products.find({"Price": {"$gt": 100000}}):
    print(p)
print('\n')

# 8.Tìm sản phẩm có số lượng bán hơn 5000
print('Sản phẩm có số lượng bán hơn 5000:')
for p in db.sales.find({"Sold": {"$gt": 5000}}):
    print(p)
print('\n')

# 9.Lấy thông tin chi tiết sản phẩm và với thông tin bán hàng
product_sales_details = db.sales.aggregate([
    {
        "$lookup": {
            "from": "products",
            "localField": "Product_ID",
            "foreignField": "Product_ID",
            "as": "product_info"
        }
    }
])
print('Thông tin chi tiết sản phẩm: ')
for p in product_sales_details:
    print(p)
print('\n')

# 10.Tìm sản phẩm có tên chứa từ khóa Eagle
print('Sản phẩm có tên chứa từ khóa Eagle: ')
for p in db.products.find({"Product_Name": {"$regex": "Eagle"}}):
    print(p)
print('\n')

# 11. Tìm sản phẩm theo Product_ID
product = db.products.find_one({"Product_ID": "P14941"})
print(f'Sản phẩm có ID P14941 là: \t{product}')
print('\n')

# 12.Tìm sản phẩm có số lượt thích thấp nhất và trả về tên, giá bán, like só lượng bán ra sản phẩm
lowest = db.sales.aggregate([{
        "$lookup": {
            "from": "products",
            "localField": "Product_ID",
            "foreignField": "Product_ID",
            "as": "product_info"
        }},
    {
        "$unwind": "$product_info"},{"$sort": {"Likes": 1}},{"$limit": 1},
    {
        "$project": {
            "Product_Name": "$product_info.Product_Name",
            "Price": "$product_info.Price",
            "Likes": "$Likes",
            "Sold": "$Sold"
        }
    }
])
print('Sản phẩm có lượt thích thấp nhất là:')
for product in lowest:
    print(product)
print('\n')

# 13.Tìm sản phẩm có số lượt thích cao nhất và trả về tên, giá bán, like só lượng bán ra sản phẩm
highest = db.sales.aggregate([{
        "$lookup": {
            "from": "products",
            "localField": "Product_ID",
            "foreignField": "Product_ID",
            "as": "product_info"
        }},
    {
        "$unwind": "$product_info"},{"$sort": {"Likes": -1}},{"$limit": 1},
    {
        "$project": {
            "Product_Name": "$product_info.Product_Name",
            "Price": "$product_info.Price",
            "Likes": "$Likes",
            "Sold": "$Sold"
        }
    }
])
print('Sản phẩm có lượt thích cao nhất là:')
for product in highest:
    print(product)
print('\n')

# 14.Tính tổng số lượng sản phẩm bán được từ collection 'sales'
sold_c = db.sales.aggregate([{"$group": {"_id": None, "Tổng số thuốc không kê đơn bán ra là:": {"$sum": "$Sold"}}}])
for c in sold_c:
    print(c)
print('\n')

# 15.Tính tổng số tiền bán thuốc không kê đơn
total_sales = db.sales.aggregate([
    {
        "$lookup": {
            "from": "products",
            "localField": "Product_ID",
            "foreignField": "Product_ID",
            "as": "product_info"
        }
    },
    {
        "$unwind": "$product_info"
    },
    {
        "$match": {"product_info.Type": "Thuốc không kê đơn"},
    },
    {
        "$group": {
            "_id": None,
            "Tổng số tiền bán thuốc không kê đơn là": {"$sum": {"$multiply": ["$Sold", "$product_info.Price"]}}
        }
    }
])
for s in total_sales:
    print(s)