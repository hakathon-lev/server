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
from jsonschema import validate, ValidationError,Draft7Validator


app = Flask(__name__)
CORS(app)

# Ensure the directory for audio logs exists
os.makedirs("audio_logs", exist_ok=True)

class AudioProcessor:
    def __init__(self, sample_rate=44100, max_buffer_size=10):
        self.audio_buffer = []
        self.sample_rate = sample_rate
        self.max_buffer_size = max_buffer_size

    def process_chunk(self, audio_data):
        try:
            # Decode base64 audio chunk
            decoded_chunk = np.frombuffer(base64.b64decode(audio_data), dtype=np.int16)
            
            # Add to buffer
            self.audio_buffer.append(decoded_chunk)
            
            # Limit buffer size
            if len(self.audio_buffer) > self.max_buffer_size:
                self.audio_buffer.pop(0)
            
            # Process and save audio periodically
            if len(self.audio_buffer) == self.max_buffer_size:
                self._process_full_buffer()
        except Exception as e:
            print(f"Error processing audio chunk: {e}")

    def _process_full_buffer(self):
        try:
            # Combine audio chunks
            full_audio = np.concatenate(self.audio_buffer)
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join("audio_logs", f"audio_chunk_{timestamp}.wav")
            
            # Save to file
            sf.write(filename, full_audio, self.sample_rate)
            
            print(f"Saved audio chunk: {filename}")
            
            # Reset buffer
            self.audio_buffer.clear()
        except Exception as e:
            print(f"Error saving audio chunk: {e}")

audio_processor = AudioProcessor()

@app.route('/audio', methods=['POST'])
def receive_audio():
    try:
        data = request.json
        audio_data = data.get('audio')
        timestamp = data.get('timestamp')

        if audio_data:
            audio_processor.process_chunk(audio_data)
            return jsonify({
                'status': 'success', 
                'timestamp': timestamp,
                'message': 'Audio chunk processed'
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': 'No audio data'
            }), 400
    
    except Exception as e:
        print(f"Error processing audio: {e}")
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500

# Ensure the directory for logs exists
os.makedirs("logs", exist_ok=True)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        print("Received data:", data)

        # Ensure logs directory and log file exist
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "queries.json")

        # Read the existing log file or create a new one
        if os.path.exists(log_file_path):
            with open(log_file_path, "r", encoding="utf-8") as file:
                try:
                    logs = json.load(file)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        # Add the new log entry
        logs.append({
            "caseLocation": data.get("caseLocation", "N/A"),
            "exitPoint": data.get("exitPoint", "N/A"),
            "caseType": data.get("caseType", "N/A"),
            "timestamp": data.get("timestamp", "N/A"),
            "actions": data.get("actions", "N/A")
        })

        # Write back to the JSON file
        with open(log_file_path, "w", encoding="utf-8") as file:
            json.dump(logs, file, indent=4, ensure_ascii=False)

        return jsonify({"message": "Data logged successfully!", "details": data}), 200

    except Exception as e:
        print(f"Error during logging to file: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    

client = MongoClient("mongodb+srv://robin:VkplmHD1loRCTahp@cluster0.it781.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["medical_database"]
patient_collection = db["cases"]


@app.route('/insert_case', methods=['POST'])
def insert_case():
    try:
        data = request.json
        case_metadata = generate_json(data)
        error_list = validate_json(case_metadata)
        if error_list:
            return jsonify({"error: missing fields": error_list}), 500
        result = patient_collection.insert_one(case_metadata)
        return jsonify({"message": "Case inserted successfully", "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)








#**********************************  helper funcs *********************************************#

def generate_json(data):
    case_metadata = {
        "מס משימה": data.get("מס משימה", "5678"),
        "מס ניידת": data.get("מס ניידת", "1234"),
        "תאריך": data.get("תאריך", "23/10/2024"),
        "פרטי המטופל": data.get("פרטי המטופל", {}),
        "פרטי האירוע": data.get("פרטי האירוע", {}),
        "פירוט המקרה": data.get("פירוט המקרה", {}),
        "מדדים": data.get("מדדים", []),
        "טיפולים": data.get("טיפולים", []),
        "טיפול תרופתי": data.get("טיפול תרופתי", []),
        "פינוי": data.get("פינוי", {}),
    }
    return case_metadata

def validate_json(document):

    schema ={
    "type": "object",
    "required": ["מס משימה", "מס ניידת", "תאריך", "פרטי המטופל", "פרטי האירוע", "פירוט המקרה", "מדדים", "טיפולים", "טיפול תרופתי", "פינוי"],
    "properties": {
        "מס משימה": {"type": "string"},
        "מס ניידת": {"type": "string"},
        "תאריך": {"type": "string"},
        "פרטי המטופל": {
        "type": "object",
        "required": ["סוג תעודה", "גיל", "מין"],
        "properties": {
            "סוג תעודה": {"type": "string"},
            "גיל": {"type": "integer"},
            "שם האב": {"type": "string"},
            "מייל": {"type": "string"},
            "מין": {"type": "string"},
            "ת. לידה": {"type": "string"},
            "קופת חולים": {"type": "string"},
            "כתובת": {"type": "string"},
            "שם מלא": {"type": "string"},
            "טלפון": {"type": "string"},
            "ישוב": {"type": "string"}
        }
        },
        "פרטי האירוע": {
        "type": "object",
        "required": ["כתובת", "מקום האירוע", "עיר"],
        "properties": {
            "כתובת": {"type": "string"},
            "מקום האירוע": {"type": "string"},
            "עיר": {"type": "string"}
        }
        },
        "פירוט המקרה": {
        "type": "object",
        "required": ["המקרה שנמצא", "תלונה עיקרית", "אנמנזה", "סטטוס המטופל"],
        "properties": {
            "המקרה שנמצא": {"type": "string"},
            "תלונה עיקרית": {"type": "string"},
            "אנמנזה": {"type": "string"},
            "סטטוס המטופל": {"type": "string"},
            "רקע רפואי": {"type": "string"},
            "רגישויות": {"type": "string"},
            "תרופות קבועות": {"type": "string"}
        }
        },
        "מדדים": {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["זמן בדיקה", "הכרה", "נשימה"],
            "properties": {
            "זמן בדיקה": { "type": "string" },
                "הכרה": { "type": "string" },
                "נשימה": { "type": "string" },
                "קצב נשימה": { "type": "string" },
                "דופק": { "type": "string" },
                "דופק לדקה": { "type": "string" },
                "מצב העור": { "type": "string" },
                "סרגל כאב": { "type": "string" },
                "האזנה": { "type": "string" },
                "ריאה ימין": { "type": "string" },
                "ריאה שמאל": { "type": "string" },
                "ETCO2": { "type": "string" },
                "קצב לב": { "type": "string" },
                "אישונים": { "type": "string" },
                "ציון גלזגו": { "type": "string" }       
                }
            }
        }
        },
        "טיפולים": {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["זמן", "טיפול שניתן"],
            "properties": {
            "זמן": {"type": "string"},
            "טיפול שניתן": {"type": "array", "items": {"type": "string"}}
            }
        }
        },
        "טיפול תרופתי": {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["זמן", "תרופה"],
            "properties": {
            "זמן": {"type": "string"},
            "תרופה": {"type": "array", "items": {"type": "string"}}
            }
        }
        },
        "פינוי": {
        "type": "object",
        "required": ["אופן הפינוי", "יעד הפינוי", "שם בית החולים"],
        "properties": {
            "אופן הפינוי": {"type": "string"},
            "יעד הפינוי": {"type": "string"},
            "שם בית החולים": {"type": "string"},
            "מחלקה": {"type": "string"},
            "שם המקבל ביעד הפינוי": {"type": "string"}
        }
        }
    }
    
    try:
        validate(instance=document, schema=schema)
        print("Document is valid. Proceeding to insert.")
        # Insert into MongoDB here
    except ValidationError as e:
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(document))
        error_list=[]
        for error in errors:
            if error.validator == "required":
                for field in error.schema["required"]:
                    if field not in error.instance:
                        error_list.append(field[::-1])
        if error_list:
            return ( error_list)

    return ([])