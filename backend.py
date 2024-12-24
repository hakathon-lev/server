from pymongo import MongoClient
import json

import os
import base64
import json
import numpy as np
#import soundfile as sf
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)
CORS(app)



client = MongoClient("mongodb+srv://robin:VkplmHD1loRCTahp@cluster0.it781.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["medical_database"]
patient_collection = db["cases"]
users_collection = db["users"]

def generate_json(data):
    case_metadata = {
        "מס משימה": data.get("מס משימה", "null"),
        "מס ניידת": data.get("מס ניידת", "null"),
        "תאריך": data.get("תאריך", "null"),
        "פרטי המטופל": data.get("פרטי המטופל", {}),
        "פרטי האירוע": data.get("פרטי האירוע", {}),
        "פירוט המקרה": data.get("פירוט המקרה", {}),
        "מדדים": data.get("מדדים", []),
        "טיפולים": data.get("טיפולים", []),
        "טיפול תרופתי": data.get("טיפול תרופתי", []),
        "פינוי": data.get("פינוי", {}),
    }
    return case_metadata


@app.route('/insert_case', methods=['POST'])
def insert_case():
    try:
        data = request.json
        data = generate_json(data)
        result = patient_collection.insert_one(data)
        return jsonify({"message": "Case inserted successfully", "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def searchSimilar(current_case):
    client = MongoClient("mongodb+srv://robin:VkplmHD1loRCTahp@cluster0.it781.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["medical_database"]
    collection = db["cases"]
    try:
        query = {
            "פירוט המקרה.קוד אירוע": current_case["פירוט המקרה"]["קוד אירוע"],
            "פרטי המטופל.גיל": {
                "$gte": current_case["פרטי המטופל"]["גיל"] - 5,
                "$lte": current_case["פרטי המטופל"]["גיל"] + 5
                },
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
        return( {"suggested tests": ranked_tests_list, "suggested treatments": ranked_treatments_list, "suggested medication": ranked_medication_list})
    except Exception as e:
        return f"error {str(e)}"



@app.route('/signin', methods=['POST'])
def sign_in():
    try:
        data = request.json  # Extract JSON data from the request body
        username = data.get("username")
        password = data.get("password")
        query = {
            "username": username,
            "password": password
        }
        # Validate credentials (example logic)
        user_exists = users_collection.count_documents(query)
        if user_exists:
            return jsonify({"message": "Sign-in successful!"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
