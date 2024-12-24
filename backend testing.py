from backend import app
from pymongo import MongoClient
import json
import requests
url = "http://127.0.0.1:5000/"
case_data = {
        
        "מס משימה": "6060",
        "מס ניידת": "4171",
        "תאריך": "22/12/2024",
        "פרטי המטופל": {
            "סוג תעודה": "תעודת זהות",
            "גיל": 43,
            "שם האב": "דוד",
            #"מייל": "example@example.com",
            "מין": "נקבה",
            "ת. לידה": "22/12/2024",
            "קופת חולים": "מאוחדת",
            "כתובת": "ירושלים",
            "שם מלא": "שם דמיוני",
            "טלפון": "050-3724274",
            "ישוב": "אשדוד"
        },
        "פרטי האירוע": {
            "כתובת": "ירושלים צפון",
            "מקום האירוע": "בבית",
            "עיר": "באר שבע"
        },
        "פירוט המקרה": {
            "המקרה שנמצא": "דום לב",
            "תלונה עיקרית": "חשד ל-דום לב",
            "אנמנזה": "אנמנזה וסיפור מקרה של חשד ל-דום לב. המטופל חש ברע והוזמן צוות לטיפול.",
            "סטטוס המטופל": "לא יציב",
            "רקע רפואי": "סוכרת",
            "רגישויות": "אבקנים",
            "תרופות קבועות": "אספירין",
            "קוד אירוע": "10"
        },
        "מדדים": [
            {
                "זמן בדיקה": "12:29",
                "הכרה": "בהכרה",
                "נשימה": "סדירה",
                "קצב נשימה": "20 בדקה",
                "דופק": "נמוש",
                "דופק לדקה": "61",
                "מצב העור": "סמוק",
                "סרגל כאב": "4",
                "האזנה": "תקינה",
                "ריאה ימין": "כא טובה",
                "ריאה שמאל": "כא טובה",
                "ETCO2": "34",
                "קצב לב": "לא סדיר",
                "אישונים": "שווים",
                "ציון גלזגו": "15"
            }
        ],
        "טיפולים": [
            {
                "זמן": "16:12",
                "טיפול שניתן": [
                    "דפיברילטור",
                    "החייאה"
                ]
            }
        ],
        "טיפול תרופתי": [
            {
                "זמן": "14:48",
                "תרופה": [
                    "גלוקוז",
                    "תפוזים"
                ]
            }
        ],
        "פינוי": {
            "אופן הפינוי": "רכב פרטי",
            "יעד הפינוי": "בית חולים",
            "שם בית החולים": "הדסה",
            "מחלקה": "מיון",
            "שם המקבל ביעד הפינוי": "ד\"ר דוד"
        }
    }
def missingTreatmentsByProtocol(medical_case):
    with open("protocol.json", "r", encoding="utf-8") as file:
        protocols = json.load(file)

    diagnosis_code = medical_case.get("פירוט המקרה").get("קוד אירוע")
    
    if diagnosis_code not in protocols:
        raise ValueError(f"Diagnosis code {diagnosis_code} not found in protocols.")
    
    protocol = protocols[diagnosis_code]
    
    # Extract protocol recommendations
    required_tests = set(protocol.get("בדיקות", []))
    required_treatments = set(protocol.get("טיפולים", []))
    required_medications = set(protocol.get("תרופות", []))
    
    given_tests = [list(item.keys()) for item in medical_case.get("מדדים", [])]
    given_tests=set([item for sublist in given_tests for item in sublist]) #flatten list
    print(given_tests)
    given_treatments = [item["טיפול שניתן"] for item in medical_case.get("טיפולים", [])]
    given_treatments=set([item for sublist in given_treatments for item in sublist]) #flatten list
    given_medications = [item["טיפול תרופתי"] for item in medical_case.get("תרופה", [])]
    given_medications=set([item for sublist in given_medications for item in sublist]) #flatten list
    
    # Determine missing items
    missing_tests = list(required_tests - given_tests)
    missing_treatments = list(required_treatments - given_treatments)
    missing_medications = list(required_medications - given_medications)
    
    print( {
        "missing_tests": missing_tests,
        "missing_treatments": missing_treatments,
        "missing_medications": missing_medications
    })
    
    
missingTreatmentsByProtocol(case_data) 
    
def testInsert():
    response = requests.post(url+"insert_case", json=case_data)
    print(response.status_code)
    print(response.json())
def testSearch():
    response = requests.post(url+"search_similar", json=case_data)
    print(response.status_code)
    print(response.json())

def testSignin():
    user={
        "username": "yosihefez",
        "password": "peepeepoopoo"
    }
    response = requests.post(url+"signin", json=user)
    print(response.status_code)
    print(response.json())
    user={
        "username": "yosihefez",
        "password": "wrongpassword"
    }
    response = requests.post(url+"signin", json=user)
    print(response.status_code)
    print(response.json())

