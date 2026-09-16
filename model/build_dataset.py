# -*- coding: utf-8 -*-
"""
Builds a seed dataset of scam vs. genuine messages/call-scripts.

Each row: text, label (scam / genuine), tactic (category, 'none' for genuine)

This is a hand-authored seed dataset built from well-documented real-world
scam patterns (bank/KYC phishing, OTP theft, courier/parcel scams, lottery
scams, tech-support scams, fake-authority threats) mixed with template
variation, plus a matching set of genuine everyday messages. It's meant to
bootstrap a working baseline model quickly. Swap in / append a larger public
dataset (e.g. an SMS spam corpus) later — the training script doesn't care
where the CSV came from.
"""
import csv
import os
import random

random.seed(42)

names = ["Ramesh", "Sunita", "Anil", "Priya", "Vikram", "Meena", "Rahul", "Geeta", "Suresh", "Kavita"]
banks = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "PNB", "your bank"]
amounts = ["Rs. 49,999", "Rs. 25,000", "Rs. 1,00,000", "Rs. 9,999", "Rs. 15,000"]
couriers = ["FedEx", "BlueDart", "the courier company", "Delhivery", "India Post"]
links = ["http://bit.ly/verify-kyc", "http://secure-bank-update.in", "http://claim-prize-now.co",
         "http://accountsafe-verify.com", "http://parcel-track-in.net"]

scam_templates = {
    "otp_request": [
        "Dear {name}, your {bank} account will be blocked today. Share the OTP sent to your number to keep it active.",
        "URGENT: Your ATM card is deactivated. Call us and provide the OTP to reactivate immediately.",
        "This is {bank} security team. We need the OTP you just received to verify a suspicious login.",
        "Your account has unusual activity. Please tell us the 6 digit code sent to your phone to secure it now.",
    ],
    "fake_bank_kyc": [
        "Dear customer, your {bank} KYC is expired. Update immediately at {link} or your account will be suspended in 24 hours.",
        "Your {bank} account is on hold due to incomplete KYC. Click {link} now to avoid permanent deactivation.",
        "IMPORTANT: {bank} - Your net banking will stop working from tomorrow. Verify your PAN and Aadhaar at {link} today.",
        "This is a final notice from {bank}. Your account access will be blocked unless you update KYC here: {link}",
    ],
    "lottery_prize": [
        "Congratulations {name}! You have won {amount} in the lucky draw. Click {link} to claim your prize now.",
        "You are selected as the winner of our anniversary lucky draw of {amount}. Pay a small processing fee to claim.",
        "Your mobile number has won {amount} cash prize from a lucky number contest. Visit {link} within 24 hours to claim.",
        "Dear winner, your lottery ticket has been selected for {amount}. Contact us urgently before the offer expires.",
    ],
    "courier_scam": [
        "{courier}: Your parcel is held at customs. Pay a small fee at {link} to release it immediately or it will be returned.",
        "Your package could not be delivered due to incomplete address. Confirm your details and pay Rs. 50 at {link}.",
        "{courier} attempted delivery today but failed. Click {link} to reschedule and pay the pending customs charge.",
        "Illegal items were found in a parcel booked using your ID. Contact us immediately or face legal action.",
    ],
    "tech_support": [
        "This is Microsoft support. We detected a virus on your computer. Please give us remote access to fix it now.",
        "Your device has been hacked. Call our technical team immediately and share your screen to remove the malware.",
        "Warning: your bank app is compromised. Download this tool and install it to secure your device right away.",
        "We are calling from your internet provider. Your connection will be suspended unless you verify your account PIN.",
    ],
    "fake_authority": [
        "This is from the Income Tax Department. A case has been filed against you. Pay the pending fine today to avoid arrest.",
        "Police department notice: your Aadhaar has been used in a crime. Call this number immediately to avoid legal action.",
        "This is TRAI. Your mobile number will be disconnected in 2 hours due to illegal activity. Press 1 to speak to an officer.",
        "Your electricity connection will be cut off tonight due to unpaid bill. Pay {amount} immediately at {link} to avoid disconnection.",
    ],
    "family_emergency": [
        "Mom I lost my phone, this is my friend's number. I'm in trouble and need {amount} urgently, please send it now.",
        "Grandpa it's me, I met with an accident and need money for the hospital right now, please don't tell anyone.",
        "Hi it's your son, I'm stuck at the airport and my card isn't working, can you transfer {amount} to this number quickly.",
    ],
}

genuine_templates = {
    "bank_alert_real": [
        "Dear {name}, Rs. 2,500 debited from your {bank} account for UPI payment. Available balance Rs. 18,400. Not you? Call 1800-XXX customer care.",
        "Your {bank} account statement for last month is ready. Login to net banking to view or download it.",
        "Dear {name}, your {bank} credit card bill of Rs. 3,200 is due on 15th. Please pay before the due date to avoid late fee.",
        "This is to confirm your fixed deposit of {amount} has matured and been credited to your {bank} savings account.",
    ],
    "otp_genuine_context": [
        "Your OTP for login is 482913. Do not share this OTP with anyone, including bank staff. Valid for 10 minutes.",
        "482913 is your one time password for the transaction. Never share your OTP with anyone for any reason.",
    ],
    "delivery_notification": [
        "Your order #45213 has been shipped and will arrive by Thursday. Track it in the app.",
        "{courier}: Your package is out for delivery today between 2 PM and 6 PM.",
        "Your order has been delivered. Thank you for shopping with us. Rate your experience in the app.",
    ],
    "appointment_reminder": [
        "Reminder: Your appointment with Dr. Sharma is scheduled tomorrow at 10 AM at City Hospital.",
        "This is a reminder that your electricity meter reading is scheduled for next Monday.",
        "Your gas cylinder booking is confirmed. Delivery expected within 2 days.",
    ],
    "personal_message": [
        "Hi {name}, are we still meeting for lunch on Sunday? Let me know what time works for you.",
        "Happy birthday {name}! Hope you have a wonderful day, call me when you're free.",
        "Just checking in, how are you feeling today? Let me know if you need anything.",
        "Don't forget to take your medicine after dinner tonight, doctor said it's important.",
    ],
    "promotion_genuine": [
        "Get 20% off on your next grocery order this weekend. Use code SAVE20 at checkout.",
        "Your loyalty points are about to expire. Redeem them on your next purchase this month.",
    ],
}

# Hindi (Devanagari) and Hinglish (Latin-script Hindi) examples — this is
# how most real Indian SMS/call scams and genuine messages actually read,
# so the model needs native examples rather than relying on translation.
hindi_scam_templates = {
    "otp_request": [
        "प्रिय ग्राहक, आपका {bank} खाता आज ब्लॉक हो जाएगा। खाता चालू रखने के लिए OTP शेयर करें।",
        "Aapka ATM card band ho gaya hai. Turant OTP batao card dobara chalu karne ke liye.",
        "Yeh {bank} security team hai. Aapke number par aaya OTP hume turant batayein.",
    ],
    "fake_bank_kyc": [
        "आपका {bank} KYC एक्सपायर हो गया है। {link} पर तुरंत अपडेट करें वरना खाता बंद हो जाएगा।",
        "Aapka {bank} account KYC na hone ki wajah se hold par hai. {link} par turant update karein.",
        "FINAL NOTICE: Aapka net banking kal se band ho jayega. PAN Aadhaar verify karein {link} par.",
    ],
    "lottery_prize": [
        "बधाई हो {name} जी! आपने लकी ड्रा में {amount} जीता है। अभी {link} पर क्लिक करके क्लेम करें।",
        "Aapka number lucky draw mein select hua hai, {amount} jeetne ke liye thoda processing fee bhejein.",
    ],
    "courier_scam": [
        "{courier}: Aapka parcel customs mein ruka hua hai. Turant {link} par fee bharke release karayein.",
        "आपका पार्सल पता अधूरा होने के कारण डिलीवर नहीं हो सका। {link} पर विवरण की पुष्टि करें।",
    ],
    "tech_support": [
        "Aapke computer mein virus aaya hai, hum Microsoft support se hain, remote access dijiye theek karne ke liye.",
        "आपका डिवाइस हैक हो गया है। तुरंत हमारी टीम को स्क्रीन शेयर करें मालवेयर हटाने के लिए।",
    ],
    "fake_authority": [
        "यह आयकर विभाग है। आपके खिलाफ केस दर्ज हुआ है। गिरफ्तारी से बचने के लिए आज ही जुर्माना भरें।",
        "Police department se call hai, aapke Aadhaar ka misuse crime mein hua hai, turant call back karein.",
    ],
    "family_emergency": [
        "Mummy mera phone kho gaya hai, yeh friend ka number hai, mujhe turant {amount} bhejo, kisi ko mat batana.",
        "दादाजी मेरा एक्सीडेंट हो गया है, अस्पताल के लिए तुरंत पैसे भेजो, यह मेरा नया नंबर है।",
    ],
}

hindi_genuine_templates = {
    "bank_alert_real": [
        "प्रिय {name}, आपके {bank} खाते से UPI भुगतान के लिए Rs. 2,500 डेबिट हुए। शेष राशि Rs. 18,400. यह आप नहीं थे? 1800-XXX पर कॉल करें।",
        "Aapka {bank} credit card bill Rs. 3,200 ka hai, 15 tarikh tak bhar dein.",
    ],
    "otp_genuine_context": [
        "आपका OTP 482913 है। इसे किसी के साथ साझा न करें, बैंक कर्मचारी के साथ भी नहीं। यह 10 मिनट के लिए मान्य है।",
        "482913 aapka one time password hai transaction ke liye. Kisi ke saath bhi share mat karein.",
    ],
    "delivery_notification": [
        "आपका ऑर्डर #45213 भेज दिया गया है और गुरुवार तक पहुंच जाएगा।",
        "{courier}: Aapka package aaj 2 baje se 6 baje ke beech deliver hoga.",
    ],
    "personal_message": [
        "नमस्ते {name}, क्या हम रविवार को लंच पर मिल रहे हैं? समय बताइए।",
        "Janamdin mubarak ho {name}! Din bahut acha guzre, jab free ho tab call karna.",
        "दवा खाना मत भूलना, डॉक्टर ने कहा है यह जरूरी है।",
    ],
}


def fill(template):
    return template.format(
        name=random.choice(names),
        bank=random.choice(banks),
        amount=random.choice(amounts),
        courier=random.choice(couriers),
        link=random.choice(links),
    )


def build_rows():
    rows = []
    for tactic, templates in scam_templates.items():
        for t in templates:
            for _ in range(6):  # repeat with random fills for variety
                rows.append((fill(t), "scam", tactic))
    for tactic, templates in genuine_templates.items():
        for t in templates:
            for _ in range(6):
                rows.append((fill(t), "genuine", tactic))
    for tactic, templates in hindi_scam_templates.items():
        for t in templates:
            for _ in range(6):
                rows.append((fill(t), "scam", tactic))
    for tactic, templates in hindi_genuine_templates.items():
        for t in templates:
            for _ in range(6):
                rows.append((fill(t), "genuine", tactic))
    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    rows = build_rows()
    out_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "tactic"])
        writer.writerows(rows)
    scam_count = sum(1 for r in rows if r[1] == "scam")
    genuine_count = sum(1 for r in rows if r[1] == "genuine")
    print(f"Wrote {len(rows)} rows to {out_path}")
    print(f"scam: {scam_count}, genuine: {genuine_count}")