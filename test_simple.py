#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, '.')

try:
    from DataAccessLayer.chatbot_db import check_available_slots
    from datetime import datetime

    print("Test check_available_slots for doctor_id=2 on 2025-11-30")
    print("=" * 60)

    result = check_available_slots(doctor_id=2, date='2025-11-30')

    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print(f"Num days: {len(result['availability'])}")
    print()

    if result['availability']:
        day = result['availability'][0]
        print(f"Date: {day['date']} ({day['day_name']})")
        print("Slots:")
        for slot in day['slots']:
            print(f"  {slot['slot_name']}: available={slot['available']}")
            if slot['available']:
                print(f"    Doctors: {slot['available_doctors']}")
            else:
                print(f"    Reason: {slot['reason']}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
