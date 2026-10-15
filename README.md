# Makro Food Service Darkstore

คัดเลือกสาขา Makro Food Service ที่เหมาะจะเปิดเป็น Darkstore ส่งสินค้าให้ร้าน 7-Eleven (7 Delivery x Makro)

## เงื่อนไข

- **กรุงเทพฯ และปริมณฑล**: แต่ละฮับส่งได้ 280–320 ร้าน ร้านอยู่ในรัศมีไม่เกิน 5 กม. และ 7-11 หนึ่งร้านอยู่ได้แค่ฮับเดียว
- **ต่างจังหวัด**: จังหวัดละ 1 ฮับ เลือกสาขาที่มีร้าน 7-11 ในรัศมี 5 กม. มากที่สุด
- วัดระยะเป็นเส้นตรง (Haversine) ยังไม่ใช่ระยะตามถนน

## ผลลัพธ์

20 ฮับ ส่งได้ 2,933 ร้าน

| กลุ่ม | สถานะ | ฮับ | ร้าน |
|---|---|---|---|
| กทม.+ปริมณฑล | แนะนำเปิด | Kanlapaphruek, Chan Road, Pradit Manutham, Pinklao, Sukhumvit 22, Onnut, Mengjai, Phong Phet | 2,325 |
| ต่างจังหวัด | เพื่อใช้พิจารณา | Pattaya N., Sirimangkalajarn, Patong, Khon Kaen 2, Ko Samui, Nakhon Ratchsima 2, Cha-Am, Hua Hin, Ao Nang, Phitsanulok 2, Ban Phe, Ko Chang | 608 |

## ไฟล์

| ไฟล์ | รายละเอียด |
|---|---|
| `index.html` | แผนที่ OpenStreetMap และตารางเหตุผลการคัดเลือกทั้ง 51 สาขา เปิดในเบราว์เซอร์ได้เลย |
| `data/makro_food_service.csv` | สาขา Makro Food Service 51 สาขา พร้อมพิกัด |
| `data/7-11_store.csv` | ร้าน 7-11 15,609 ร้าน พร้อมพิกัด |
| `scripts/analyze.py` | สคริปต์คัดเลือกฮับและจับคู่ร้านกับฮับ |
| `output/hub_summary.csv` | สรุปผลของแต่ละสาขา Makro |
| `output/store_assignment.csv` | รายชื่อร้าน 7-11 ที่จับคู่กับแต่ละฮับ |
| `output/Makro_Darkstore_คัดเลือกฮับ.xlsx` | สรุปและรายชื่อร้านในรูปแบบ Excel |
| `output/7-11_รัศมี_Makro_Food_Service_310869.xlsx` | จำนวน 7-11 ในรัศมี 1/2/3/5 กม. ของแต่ละสาขา (ข้อมูล 31/8/69) |

## รันใหม่

```bash
pip install pandas numpy networkx
python scripts/analyze.py
```

ถ้าเปลี่ยนเกณฑ์ ให้แก้ค่า `RADIUS_KM`, `LO` และ `HI` ที่ต้นไฟล์ `scripts/analyze.py`

แผนที่พื้นหลัง © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors
