import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
from typing import Dict, Any, List
import argparse
from datetime import datetime
import random,string

def convert_dates_to_timestamp(data):
    # 深拷貝原始數據以避免修改原始物件
    new_data = data.copy()
    
    # 定義需要轉換的日期欄位 (純日期格式)
    date_fields = ['time_start', 'time_end', 'time_early', "birthday"]
    
    # 轉換純日期欄位 ('%Y-%m-%d')
    for field in date_fields:
        if field in new_data and new_data[field]:
            try:
                date = datetime.strptime(new_data[field], '%Y-%m-%d')
                new_data[field] = firestore.SERVER_TIMESTAMP if date is None else date
            except ValueError:
                print(f"無法解析日期: {new_data[field]}")
                continue

    # 處理 updated_at (完整日期時間格式 '%Y-%m-%d %H:%M:%S')
    if 'updated_at' in new_data and new_data['updated_at']:
        try:
            date = datetime.strptime(new_data['updated_at'], '%Y-%m-%d %H:%M:%S')
            new_data['updated_at'] = firestore.SERVER_TIMESTAMP if date is None else date
        except ValueError:
            print(f"無法解析 updated_at 日期: {new_data['updated_at']}")
    
    return new_data

def generateId(prefix, length = 8):

    return prefix + ''.join(random.choice(string.ascii_letters + string.digits) for x in range(10))

def initialize_firebase():
    """初始化 Firebase"""
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Firebase 初始化失敗: {str(e)}")
        raise

def get_document_id(item: Dict[str, Any], id_field: str) -> str:
    """從資料中獲取 document ID"""
    try:
        doc_id = str(item.get(id_field, '')).strip()
        if not doc_id:
            raise ValueError(f"指定的欄位 '{id_field}' 值為空")
        return doc_id
    except Exception as e:
        raise ValueError(f"無法從欄位 '{id_field}' 獲取有效的 document ID: {str(e)}")

def upload_to_firestore(db: firestore.Client, collection_name: str, data: Any):
    """上傳資料到 Firestore"""
    try:
        # 檢查資料是否為列表
        if not isinstance(data, list):
            raise ValueError("JSON 資料必須是列表格式")

        # 使用批次寫入
        batch = db.batch()
        count = 0
        total = len(data)
        
        # 記錄已使用的 document IDs，用於檢查重複
        used_ids = set()

        # 每 500 筆資料為一個批次（Firestore 限制）
        for i in range(0, total, 500):
            batch = db.batch()
            
            # 處理這個批次的資料
            for item in data[i:i+500]:
                try:
                    # 獲取 document ID
                    doc_id = get_document_id(item, "id")
                    
                    
                    used_ids.add(doc_id)
                    converted_data  = convert_dates_to_timestamp(item)
                    if 'updated_at' in converted_data and converted_data['updated_at']:
                        doc_data = {
                            **converted_data
                        }
                    else:
                        doc_data = {
                            **converted_data,  
                            "updated_at": firestore.SERVER_TIMESTAMP
                        }
                        
                    # 添加到批次
                    doc_ref = db.collection(collection_name).document(doc_id)
                    batch.set(doc_ref, doc_data)
                    count += 1
                    
                except Exception as e:
                    print(f"處理資料時發生錯誤: {str(e)}")
                    continue
            
            # 提交這個批次
            batch.commit()
            print(f"已上傳 {min(count, i+500)}/{total} 筆資料")
        
        print(f"\n上傳完成！")
        print(f"成功上傳: {count} 筆")
        print(f"重複 ID: {total - count} 筆")
            
    except Exception as e:
        print(f"上傳資料時發生錯誤: {str(e)}")
        raise

def main():
    # 初始化 Firebase
    print("初始化 Firebase...")
    db = initialize_firebase()

    json_list = [
            "estate/json/electrics.json",
            "estate/json/leases.json",
            "estate/json/logs.json",
            "estate/json/properties.json",
            "estate/json/rooms.json",
            "estate/json/tenants.json"
        ]
    col_name = [
        "electrics",
        "leases",
        "logs",
        "properties",
        "rooms",
        "tenants"
    ]
    for i in range(len(json_list)):
        try:
            # 讀取 JSON 檔案
            print(f"讀取 JSON 檔案: {json_list[i]}")
            with open(json_list[i], 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, list):
                raise ValueError("JSON 檔案必須包含資料列表")
                
            print(f"成功讀取 {len(data)} 筆資料")
                
            # 上傳資料到 Firestore
            print(f"開始上傳資料到 collection: {col_name[i]}")
            upload_to_firestore(db, col_name[i], data)
            print("{:=^50s}".format("Split Line"))
            
        except FileNotFoundError:
            print(f"找不到檔案: {col_name[i]}")
        except json.JSONDecodeError:
            print("JSON 檔案格式錯誤")
        except Exception as e:
            print(f"發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()