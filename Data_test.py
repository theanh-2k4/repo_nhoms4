from pymongo import MongoClient
import time

client = MongoClient("mongodb://localhost:27017/")
db = client['pharmacity']
products_collection = db['products']
sales_collection = db['sales']
products_detail = db['details']

#Liệt kê thông tin, số lượng dược phẩm được lưu trong database pharmacity
count =0
# for product in products_collection.find().sort({'Price': -1}):
#     count += 1
#     print(product)
# print(f'Số lượng dược phẩm trong db: {count}')

# Sắp xếp các dược phẩm theo số lượng bán giảm dần, loại bỏ các thuốc thuộc loại kê đơn
ckd = 0
for product in sales_collection.find().sort({'Sold': -1}):
    print(product)

#In sản phẩm bán chạy nhất, hiển thị tên, id, xuất xứ, số lượng bán, lượt thích
def banchaynhat():
    banchaynhat = sales_collection.aggregate([
        {"$match": {"Sold": {"$ne": "N/A"}}},  # Loại bỏ các sản phẩm có Sold là 'N/A', thuốc kê dơn
        {"$sort": {"Sold": -1}},               # Sắp xếp theo Sold từ cao đến thấp
        {"$limit": 1},                         # Lấy sản phẩm bán chạy nhất
        {"$lookup": {                          # Kết hợp với collection 'products' để lấy các thông tin khác của sản phẩm
            "from": "products",
            "localField": "Product_ID",        #kết nối thông tin sản phẩm thông qua product_id
            "foreignField": "Product_ID",
            "as": "product_info"
        }},
        {"$unwind": "$product_info"},
        {"$project": {                         # Chọn các trường cần thiết
            "Product_Name": "$product_info.Product_Name",
            "Product_ID": "$Product_ID",
            "Product_origin": "$product_info.Product_origin",
            "Price": "$product_info.Price",
            "Sold": "$Sold",
            "Likes": "$Likes"
        }}
    ])

    for p in banchaynhat:
        print(f'Sản phẩm bán chạy nhất:\n {p}')

#Liệt kê mã sp, tên, tổng số tiền bán thuốc được, không bao gồm thuốc kê đơn
def ketquaban():
    ketquaban = products_collection.aggregate([
        {"$match": {"Price": {"$ne": "N/A"}}},  # Lọc các sản phẩm không phải thuốc kê đơn
        {
            "$lookup": {  # Kết hợp với collection 'sales'
                "from": "sales",
                "localField": "Product_ID",
                "foreignField": "Product_ID",
                "as": "sales_info"
            }
        },
        {"$unwind": {"path": "$sales_info", "preserveNullAndEmptyArrays": True}},  # Bóc tách mảng sales_info
        {
            "$group": {  # Nhóm theo Product_ID và Product_Name
                "_id": {
                    "Product_ID": "$Product_ID",
                    "Product_Name": "$Product_Name"
                },
                "Total_Sales": {
                    "$sum": {"$multiply": ["$sales_info.Sold", "$Price"]}  # Tính tổng số tiền bán
                }
            }
        },
        {
            "$project": {  # Chọn các trường cần thiết
                "Product_ID": "$_id.Product_ID",
                "Product_Name": "$_id.Product_Name",
                "Total_Sales": {"$ifNull": ["$Total_Sales", 0]}  # Đảm bảo không có giá trị null
            }
        }
    ])


    for p in ketquaban:
        print(p)

ketquaban()