
from dataclasses import dataclass, asdict
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from collections import defaultdict
from typing import List
import json , csv , random ,string , re
import time ,io
from datetime import datetime

@dataclass
class Leases:
    id : str
    time_start: datetime # estate_rent_start
    time_end : datetime # estate_rent_end
    time_early : datetime # estate_rent_early
    deposit : int # estate_rent_deposit
    payment_method : str # estate_rent_money
    electric : float # estate_rent_electric
    version : int # default 1 
    status : bool # estate_rent_enable 
    note : str # estate_rent_note -> html clean
    mini_note : str # estate_rent_pet
    property_id : str
    tenant_id : str
    room_id : str
    file : list  
    access : dict #default
    @staticmethod
    def time_transfer_YMD(string) -> datetime:
        try:
            trans_time = datetime.strptime(string, "%Y-%m-%d")
        except Exception as e:
            trans_time = datetime.strptime("1901-01-01", "%Y-%m-%d")
        return trans_time.strftime("%Y-%m-%d")
    @staticmethod
    def status_check(enable) -> bool:
        if enable == 0 :
            return False
        return True

@dataclass
class Tenants:
    id : str 
    name : str # estate_user_name
    birthday : datetime # estate_user_birthday
    personal_id : str # estate_user_pid
    address : str # estate_user_addr
    tel : str # estate_user_tel
    job : str # estate_user_job 
    contact : str # estate_user_job
    contact_tel : str # blank
    email : str # estate_user_email
    note: str # estate_user_note
    leases_id : str 
    file : list # blank
    access : dict # default

@dataclass
class Room:
    id : str
    name: str # estate_room_title
    size: float # estate_room_size
    storey : str # estate_room_storey
    type : str # estate_room_type
    facilities : dict # estate_room_facility function trans
    payment_method : dict # estate_room_price
    note : str # estate_room_note
    property_id : str 
    file : list 
    access : dict  # default

    @staticmethod
    def simplify_facility_data(original_data) -> dict:
        data = json.loads(original_data)
        simplified = {}
        for key, value in data.items():
            try:
                # 確保 money 欄位存在且可以轉換為整數
                simplified[key] = int(value)
            except (ValueError, AttributeError):
                # 如果轉換失敗，設為 0 或進行其他錯誤處理
                simplified[key] = "error"
        return simplified

    @staticmethod
    def simplify_payment_data(original_data) -> dict:
        data = json.loads(original_data)
        simplified = {}
        for key, value in data.items():
            try:
                # 確保 money 欄位存在且可以轉換為整數
                simplified[key] = int(value.get('money', 0))
            except (ValueError, AttributeError):
                # 如果轉換失敗，設為 0 或進行其他錯誤處理
                simplified[key] = 0
        return simplified

@dataclass
class Property:
    id : str
    name: str # estate_title
    nickname: str # estate_stitle
    address: str # estate_address
    phone: str  # estate_tel
    owner: str # estate_name
    note: str # estate_note
    facilities: List[str] # estate_facility
    electric_price: float # electric_money
    electric_month: str # electric_month
    file : List
    access : dict

@dataclass
class Logs:
    id : str # 系統產生流水號
    old_id : str # estate_schedule_id
    property_id : str # 物業id
    room_id : str # estate_room_id 如果等於0 保持0
    user_id : str # new 
    member : List[str] # new blank for now
    old_user_id : str # estate_schedule_uid
    updated_at : datetime # estate_schedule_date
    category : str #  estate_schedule_kind
    facility : str # estate_schedule_facility
    content : str # estate_schedule_content
    file : List # blank

    @staticmethod
    def time_transfer(string) -> datetime:
        try:
            trans_time = datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            trans_time = datetime.strptime("1901-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        return trans_time.strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class Electric:
    id : str
    room_id : str # estate_room_id
    degrees : str # estate_electric_degrees
    user_id : str # blank
    old_user_id: str #estate_electric_uid
    updated_at: str # estate_electric_update

    @staticmethod
    def time_transfer(string) -> datetime:
        try:
            trans_time = datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            trans_time = datetime.strptime("1901-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        return trans_time.strftime("%Y-%m-%d %H:%M:%S")

    

    

def idGenerate(prefix: str) -> str:
    # 純本地運算，不需要數據庫操作
    timestamp = int(time.time() * 1000)
    random_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    return f"{prefix}_{timestamp}_{random_str}"

def initialize_firebase():
    """初始化 Firebase"""
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Firebase 初始化失敗: {str(e)}")
        raise

def clean_html(html_text: str) -> str:
    if not html_text:
        return ""
        
    # 移除HTML標籤
    text = re.sub(r'<[^>]+>', '\n', html_text)
    
    # 處理特殊HTML字符
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    
    # 處理多餘的換行和空格
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]  # 移除空行
    
    return '\n'.join(lines)

def read_csv_file(file_path: str) -> List[dict]:
    """讀取 CSV 檔案並返回資料列表"""
    with open(file_path, 'r', encoding='utf-8') as file:
        # 讀取整個檔案內容
        content = file.read()
        
        # 檢查並移除 BOM
        if content.startswith('\ufeff'):
            content = content[1:]
            
        # 將內容分割成行
        lines = content.splitlines()
        
        # 使用 csv.DictReader 處理這些行
        reader = csv.DictReader(lines)
        
        # 將所有行轉換為字典列表
        return list(reader)
    
def read_csv_to_string(filename):
    output = io.StringIO()
    with open(filename, 'r', encoding='utf-8') as file:
        writer = csv.writer(output)
        reader = csv.reader(file)
        for row in reader:
            writer.writerow(row)
    return output.getvalue()

def csv_to_objects(csv_file_path: str,func) -> dict:
    """讀取 CSV 檔案並轉換為物件和 JSON"""
    try:
        # 讀取 CSV 檔案
        rows = read_csv_file(csv_file_path)
        
        # 處理每一行資料
        item_dicts = {}
        for row in rows:
            try:
                name ,obj = func(row)
                item_dicts[name] = obj          
            except Exception as e:
                print(e)
                print(f"問題資料行: {row}")
        
        return item_dicts
            
    except Exception as e:
        print(f"處理檔案時發生錯誤: {str(e)}")
        raise

def csv_to_logs_objects(csv_file_path:str,func)->dict:
    try:
        rows = read_csv_file(csv_file_path)
        count = 0
        item_dicts = {}
        for row in rows:
            try:
                name, obj = func(row,count)
                if name in item_dicts.keys():
                    item_dicts[name].append(obj)
                else:
                    item_dicts[name] = [obj]
                count = count + 1

            except Exception as e:
                print(f"處理行時發生錯誤: {str(e)}")
                print(f"問題資料行: {row}")

        return item_dicts
    except Exception as e:
        print(f"處理檔案時發生錯誤: {str(e)}")
        raise


def create_user_to_rent_mapping(data_str):
    # 跳過標題行
    lines = data_str.strip().split('\n')[1:]
    
    # 創建映射字典
    user_to_rent = defaultdict(list)
    rent_to_user = defaultdict(list)
    for line in lines:
        rent_id, user_id = line.split(',')
        # 清理 \r
        clean_user_id = user_id.strip().replace('\r', '')
        clean_rent_id = rent_id.strip().replace('\r', '')
        user_to_rent[clean_user_id].append(clean_rent_id)
        rent_to_user[clean_rent_id].append(clean_user_id)        
    return user_to_rent,rent_to_user


