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
                    "גלוקוז"
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

def searchSimilar(current_case):
    client = MongoClient("mongodb+srv://robin:VkplmHD1loRCTahp@cluster0.it781.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["medical_database"]
    collection = db["cases"]
    #try:
    query = {
        "פירוט המקרה.קוד אירוע": current_case["פירוט המקרה"]["קוד אירוע"],
        "פרטי המטופל.גיל": {"$gte": current_case["פרטי המטופל"]["גיל"] - 5, "$lte": current_case["פרטי המטופל"]["גיל"] + 5},
    }

    # Search for similar cases
    similar_cases = collection.find(query)
    fuzzy_query={}

    cases_list = []
    for case in similar_cases:
        case['_id'] = str(case['_id'])  # Convert ObjectId to string
        cases_list.append(case)
    similar_cases=cases_list   

    #find treatments and sort by frequency
    treatment_recommendations = {}
    medication_reccomendations ={}
    for case in similar_cases:
        treatments = case.get("טיפולים", [])
        for treatment in treatments:
            for treatment_name in treatment.get("טיפול שניתן", []):
                treatment_recommendations[treatment_name] = treatment_recommendations.get(treatment_name, 0) + 1
    ranked_treatments = sorted(treatment_recommendations.items(), key=lambda x: x[1], reverse=True)
    ranked_treatments_list=[x[0] for x in ranked_treatments]

    for case in similar_cases:
        medications=case.get("טיפול תרופתי", [])
        for medication in medications:
            for medication_name in medication.get("תרופה"):
                medication_reccomendations[medication_name]=medication_reccomendations.get(medication_name, 0) +1
    ranked_medication=sorted(medication_reccomendations.items(), key=lambda x: x[1], reverse=True)
    ranked_medication_list=[x[0] for x in ranked_medication]

    test_reccomendations={}
    for case in similar_cases:
        tests = case.get("מדדים")
        for test in tests:
            for (key, val) in test.items():
                if key=="זמן בדיקה":
                    continue
                if val!="null":
                    test_reccomendations[key] = test_reccomendations.get(key, 0) +1
    ranked_tests=sorted(test_reccomendations.items(), key=lambda x: x[1], reverse=True)      
    ranked_tests_list=[x[0] for x in ranked_tests]  
    print( {"suggested tests": ranked_tests_list, "suggested treatments": ranked_treatments_list, "suggested medication": ranked_medication_list})
    
    
    
    
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

searchSimilar(case_data)
