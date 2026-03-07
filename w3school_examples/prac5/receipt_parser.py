import re

with open(r"C:\Users\Admin\Desktop\python\w3school_examples\prac5\raw.txt", "r", encoding="utf-8") as f:
    text = f.read()
unit_prices = re.findall(r'x (\d{1,3}(?: \d{3})*,\d{2})', text)
pattern = r'\d+\.\s*(.*?)\s*\d+,\d{3,} x'
names = re.findall(pattern, text, re.DOTALL)
names = [name.replace('\n',' ').strip() for name in names]
totals = re.findall(r'Стоимость\s*[\r\n]+(\d{1,3}(?: \d{3})*,\d{2})', text)
totals_float = [float(t.replace(' ', '').replace(',', '.')) for t in totals]
grand_total_calc = sum(totals_float)
datetime_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4})\s*(\d{2}:\d{2}:\d{2})', text)
date = datetime_match.group(1) if datetime_match else "не найдено"
time = datetime_match.group(2) if datetime_match else "не найдено"
payment_match = re.search(r'([А-Яа-яЁё\s]+):\s*\d', text)
payment_method = payment_match.group(1).strip() if payment_match else "не найдено"
print("\n====== RECEIPT ======\n")
print(f"Date: {date}  Time: {time}")
print(f"Payment Method: {payment_method}\n")
print(f"{'№':<3} {'Product':<50} {'Quantity':<8} {'Price/unit':<10} {'Total':<10}")
print("-"*85)
for i, (name, unit, total) in enumerate(zip(names, unit_prices, totals), start=1):
    print(f"{i:<3} {name:<50} {'-':<8} {unit:<10} {total:<10}")
print("-"*85)
print(f"{'Total by receipt:':<73} {grand_total_calc:.2f} ₸\n")