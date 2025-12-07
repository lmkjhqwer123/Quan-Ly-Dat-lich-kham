import sys
sys.path.insert(0, '.')
from DataAccessLayer.data_access import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Bác sĩ Trần Thị B - doctor_id = 2
# Kiểm tra appointments vào 30/11
print('=== APPOINTMENTS ngày 30/11 ===')
cursor.execute("""
SELECT appointment_id, doctor_id, appointment_datetime, status
FROM APPOINTMENTS
WHERE CAST(appointment_datetime AS DATE) = '2025-11-30'
  AND doctor_id = 2
""")
results = cursor.fetchall()
if not results:
    print('Không có appointments')
else:
    for row in results:
        print(f'Appointment {row[0]}: doctor={row[1]}, time={row[2]}, status={row[3]}')

# Kiểm tra DOCTOR_LEAVES vào 30/11
print('\n=== DOCTOR_LEAVES ngày 30/11 ===')
cursor.execute("""
SELECT leave_id, doctor_id, start_datetime, end_datetime, status
FROM DOCTOR_LEAVES
WHERE doctor_id = 2
  AND (CAST(start_datetime AS DATE) = '2025-11-30' 
       OR CAST(end_datetime AS DATE) = '2025-11-30'
       OR (start_datetime < '2025-11-30 23:59:59' AND end_datetime > '2025-11-30 00:00:00'))
""")
results = cursor.fetchall()
if not results:
    print('Không có leaves')
else:
    for row in results:
        print(f'Leave {row[0]}: doctor={row[1]}, start={row[2]}, end={row[3]}, status={row[4]}')

# Test hàm check_available_slots
print('\n=== TEST check_available_slots ===')
from DataAccessLayer.chatbot_db import check_available_slots

result = check_available_slots(doctor_id=2, date='2025-11-30')
print(f"Success: {result['success']}")
print(f"Num days: {len(result['availability'])}")

if result['availability']:
    day = result['availability'][0]
    print(f"\nDate: {day['date']} ({day['day_name']})")
    for slot in day['slots']:
        print(f"  {slot['slot_name']}: available={slot['available']}, doctors={slot['available_doctors']}")

cursor.close()
conn.close()
