

from transformers import pipeline
from jsonschema import validate, ValidationError,Draft7Validator
def validate_json(my_json):

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
        for error in errors:
            if error.validator == "required":
                for field in error.schema["required"]:
                    if field not in error.instance:
                        print(f"- Missing field: {field[::-1]}")
            else:
                print(f"- {error.message}")
    
        print("Document is valid.")


document ={
       
            "מס משימה": "5678",
            "מס ניידת": "1234",
            "תאריך": "23/10/2024",
            
            "פרטי המטופל": {
                "סוג תעודה": "אחר",
                #"גיל": 50,
                "שם האב": "null",
                "מייל": "null",
                "מין": "זכר",
                "ת. לידה": "null",
                "קופת חולים": "null",
                "כתובת": "null",
                "שם מלא": "null",
                "טלפון": "null",
                "ישוב": "null"
            },
            "פרטי האירוע":
            {
                "כתובת": "איילון דרום",
                "מקום האירוע": "רישות הרבים",
                "עיר": "תל אביב"

            },
            "פירוט המקרה": {

                "המקרה שנמצא": "דום לב",
                "תלונה עיקרית": "דום לב ונשימה- החיאה",
                "אנמנזה": '''
                
                ''',
                "סטטוס המטופל": "קשה, לא יציב",
                "רקע רפואי": "לא ידוע",
                "רגישויות": "לא ידוע",
                "תרופות קבועות": "לא ידוע"
            },
            

            "מדדים": [
                {
                "זמן בדיקה":"12:30",
                "הכרה": 'לא',
                "נשימה": 'מונשם',
                "קצב נשימה": '12 בדקה',
                "דופק": 'קרודיטי לא נמוש',
                "דופק לדקה": '0',
                "מצב העור": 'חיוור',
                "סרגל כאב": '1',
                "האזנה": 'תקינה',
                "ריאה ימין":'כ"א טובה',
                "ריאה שמאל": 'אחר',
                "ETCO2": '22',
                "קצב לב": 'PEA',
                "אישונים": 'שווים',
                "ציון גלזגו": '3',
                }
            ],
            "טיפולים":[
                {
                    "זמן": "12:35",
                    "טיפול שניתן":  ["החייאה", "דפיברילטור"]
                }
            ] ,
            "טיפול תרופתי": [
                {
                    "זמן": "12:35",
                    "תרופה": ["adrenaline"]
                }
            ],
            "פינוי":
            {
                "אופן הפינוי": "אמבולנס",
                "יעד הפינוי": "בית חולים",
                "שם בית החולים": "סורוקה",
                "מחלקה": "חדר טראומה",
                "שם המקבל ביעד הפינוי": 'ד"ר דריה'
            }
            
        }

#validate_json(document)
    
