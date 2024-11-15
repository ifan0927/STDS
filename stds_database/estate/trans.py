from modal import Room, Property, Tenants , Leases , Logs, Electric
from modal import initialize_firebase,idGenerate,clean_html,csv_to_objects
from modal import create_user_to_rent_mapping, read_csv_to_string
import ast,json 
from dataclasses import asdict
from datetime import datetime
db = initialize_firebase()

rent_user_data_str = read_csv_to_string("csv/xx_estate_rent_user.csv")
user_rent_map,rent_user_map = create_user_to_rent_mapping(rent_user_data_str)
property_id_map = {}
room_id_map = {}
tenants_id_map = {}
leases_id_map = {}
rooms_property_map = {}

def create_room(row:dict) ->Room:
    access = {
        'type' : 'internal',    # 'internal' | 'external'
        'companies' : ['STDS','YIDE'],  # 可訪問的公司列表
        'allowClients': ""  
    }
    try:
        storey = float(row['estate_room_storey']) if row['estate_room_storey'] else 0.0
    except (ValueError, TypeError):
        storey = 0.0

    id = idGenerate("ROOM")
    documentname = "房間-" + id
    try:
        old_property_id = int(row.get('estate_id','').strip())
        property_id = property_id_map[old_property_id]
        rooms_property_map[id] = property_id
    except Exception as e:
        print(e)
        

    room_id_map[int(row.get('estate_room_id', '').strip())] = id
    try:
        return documentname, Room(
            id=id,
            name=row.get('estate_room_title', '').strip(),
            size=float(row.get('estate_room_size', '').strip()),
            storey=storey,
            type=row.get('estate_room_type', '').strip(),
            payment_method=Room.simplify_payment_data(row.get('estate_room_price','')),
            facilities=Room.simplify_facility_data(row.get('estate_room_facility', '')),
            note=row.get('estate_room_note', '').strip(),
            property_id= property_id, #存舊的抓新的
            file= [],
            access = access
        )
    except Exception as e:
        print(e)

def create_property(row: dict) -> Property:
    access = {
        'type' : 'internal',    # 'internal' | 'external'
        'companies' : ['STDS','YIDE'],  # 可訪問的公司列表
        'allowClients': row.get('estate_name', '').strip()     # 是否允許客戶訪問
    }

    id = idGenerate("PROP")
    
    try:
        # 處理設施列表
        facilities = ast.literal_eval(row['estate_facility']) if row['estate_facility'] and row['estate_facility'] != 'null' else []
    except (ValueError, SyntaxError):
        facilities = []
    
    # 處理電費價格
    try:
        electric_price = float(row['electric_money']) if row['electric_money'] else 0.0
    except (ValueError, TypeError):
        electric_price = 0.0
    
    #處理documentname
    documentname = "物業-" + id
    property_id_map[int(row.get('estate_id', '').strip())] = id
    
    return documentname, Property(
        id=id,
        name=row.get('estate_title', '').strip(),
        nickname=row.get('estate_stitle', '').strip(),
        address=row.get('estate_addr', '').strip(),
        phone=str(row.get('estate_tel', '')).strip(),
        owner=row.get('estate_name', '').strip(),
        note=clean_html(row.get('estate_note', '')),
        facilities=facilities,
        electric_price=electric_price,
        electric_month=row.get('electric_month', '').strip(),
        file= [],
        access = access
    )

def create_teants(row : dict) -> Tenants:
    access = {
        'type' : 'internal',    # 'internal' | 'external'
        'companies' : ['STDS','YIDE'],  # 可訪問的公司列表
        'allowClients': ""  
    }
    id = idGenerate("TENA")
    document_name = "房客-" + id

    user_id = int(row.get('estate_user_id', '').strip())
    tenants_id_map[user_id] = id 
    date_string = row.get('estate_user_birthday').strip()
    try :
        
        birthday = datetime.strptime(date_string,"%Y-%m-%d")
    except Exception as e:
        birthday = datetime.strptime("1900-01-01","%Y-%m-%d")


    try:
        old_leases_id = int(user_rent_map[str(user_id)][0])
        leases_id = leases_id_map[old_leases_id]
        
    except Exception as e:
        print(e)
        leases_id = ""
    
    return document_name, Tenants(
        id = id ,
        name = row.get('estate_user_name','').strip(),
        birthday = birthday.strftime("%Y-%m-%d"),
        personal_id = row.get('estate_user_pid','').strip(),
        address = row.get('estate_user_addr','').strip(),
        tel = row.get('estate_user_tel','').strip(),
        job = row.get('estate_user_job','').strip(),
        contact = row.get('estate_user_contact','').strip(),
        contact_tel = "",
        email = row.get('estate_user_email','').strip(),
        note = row.get('estate_user_note','').strip(),
        leases_id = leases_id, #函數抓取
        file = [],
        access = access
    )

def create_leases(row:dict) ->Leases:
    access = {
        'type' : 'internal',    # 'internal' | 'external'
        'companies' : ['STDS','YIDE'],  # 可訪問的公司列表
        'allowClients': ""  
    }
    # 處理電費價格
    try:
        electric = float(row['estate_rent_electric']) if row['estate_rent_electric'] else 0.0
    except (ValueError, TypeError):
        electric = 0.0

    try:
        old_room_id = int(row.get('estate_room_id','').strip())
        room_id = room_id_map[old_room_id]
    except Exception as e:
        print(e)
    try:
        old_lease_id = row.get('estate_rent_id','').strip()
        old_tenant_id = int(rent_user_map[str(old_lease_id)][0])
    except Exception as e:
        print(e)
    


    id = idGenerate("LEAS")
    document_name = "租約-" + id

    leases_id_map[int(row.get('estate_rent_id', '').strip())] = id
    return document_name, Leases(
        id = id,
        time_start = Leases.time_transfer_YMD(row.get('estate_rent_start','').strip()),
        time_end = Leases.time_transfer_YMD(row.get('estate_rent_end','').strip()),
        time_early = Leases.time_transfer_YMD(row.get('estate_rent_early','').strip()),
        deposit = int(row.get('estate_rent_deposit','').strip()),
        payment_method = row.get('estate_rent_money','').strip(),
        electric= electric,
        version= 1,
        status = Leases.status_check(int(row.get('estate_rent_enable','').strip())),
        note = clean_html(row.get('estate_rent_note','').strip()),
        mini_note = row.get('estate_rent_pet','').strip(),
        property_id=rooms_property_map[room_id],
        tenant_id=old_tenant_id,
        room_id = room_id, #存舊的抓新的
        file = [],
        access=access

    )

def create_estate_logs(row:dict) ->Logs:
    old_room_id = int(row.get('estate_room_id','').strip())
    old_property_id = int(row.get('estate_id','').strip())
    date = Logs.time_transfer(row.get('estate_schedule_date','').strip())
    

    id = idGenerate("ESTA")
    name = "LOGS-" + id
    if old_room_id == 0 :
        room_id = 0
    else:
        room_id = room_id_map[old_room_id]
    property_id = property_id_map[old_property_id]

    return name , Logs(
        id = str(id),
        old_id = row.get('estate_schedule_id','').strip(),
        property_id = property_id,
        room_id = room_id,
        user_id = "",
        member = [],
        old_user_id = row.get('estate_schedule_uid','').strip(),
        updated_at = date,
        category = row.get('estate_schedule_kind','').strip(),
        facility = row.get('estate_schedule_facility','').strip(),
        content = row.get('estate_schedule_content','').strip(),
        file = []
    )

def create_electric_logs(row:dict)-> Electric:
    old_room_id = int(row.get('estate_room_id','').strip())
    room_id = room_id_map[old_room_id]
    date = Electric.time_transfer(row.get('estate_electric_update','').strip())

    id = idGenerate("ELEC")
    name = "LOGS-" + id

    # 處理電費價格
    try:
        degree = float(row['estate_electric_degrees']) if row['estate_electric_degrees'] else 0.0
    except (ValueError, TypeError):
        degree = 0.0


    return name, Electric(
        id = id,
        room_id = room_id,
        degrees = degree,
        user_id = '',
        old_user_id = row.get('estate_electric_uid','').strip(),
        updated_at = date
    )

def write_to_json(filename, objects):
    temp = []
    for key,value in objects.items():
        temp.append(asdict(value))
    try:
        json_file_path = "json/" + filename
        with open(json_file_path, 'a', encoding='utf-8') as json_file:
                json.dump(temp, json_file, ensure_ascii=False, indent=4, default=str)
    except Exception as e:
        print(f'錯誤檔案{filename}')
        print(e)

def log_write_to_json(filename, dicts):
    for key,value in dicts.items():

        temp = []
        for l in value:
            temp.append(asdict(l))

        json_file_path = "json/" + filename + str(key) + ".json"
        with open(json_file_path, 'a', encoding='utf-8') as json_file:
            json.dump(temp, json_file, ensure_ascii=False, indent=4, default=str)

    

if __name__ == "__main__":
    properties = csv_to_objects("csv/xx_estate.csv",create_property)
    rooms = csv_to_objects("csv/xx_estate_room.csv", create_room)
    leases = csv_to_objects("csv/xx_estate_rent.csv", create_leases)
    tenants = csv_to_objects("csv/xx_estate_user.csv", create_teants)
    logs = csv_to_objects("csv/xx_estate_schedule.csv", create_estate_logs)
    electrics = csv_to_objects("csv/xx_estate_electric.csv", create_electric_logs)

    for _,value in leases.items():
        new_id = tenants_id_map[value.tenant_id]
        value.tenant_id = new_id
    write_to_json("properties.json",properties)
    write_to_json("rooms.json",rooms)
    write_to_json("leases.json",leases)
    write_to_json("tenants.json",tenants)
    write_to_json("electrics.json",electrics)
    write_to_json("logs.json",logs)







    
    

