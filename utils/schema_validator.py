
user_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["has_labels", "activities"],
        "properties": {
            "has_labels": {
                "bsonType": "bool"
            },
            "activities": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string",
                    "description": "activity id"
                }
            },
        }
    }
}

activity_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["user_id", "transportation_mode", "start_date_time", "end_date_time"],
        "properties": {
            "user_id": {
                "bsonType": "string",
                "description": "user id"
            },
            "transportation_mode": {
                "bsonType": ["string", "null"],
                "description": "transportation mode"
                # "enum": ["walk", "car", "bike", "bus", "airplane", "boat", "train"]
            },
            "start_date_time": {
                "bsonType": "date",
                "description": "start date time"
            },
            "end_date_time": {
                "bsonType": "date",
                "description": "end date time"
            },
        }
    }
}

track_point_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["user_id", "activity_id", "location", "altitude", "date_days", "date_time", "transportation_mode"],
        "properties": {
            "user_id": {
                "bsonType": "string",
                "description": "user id"
            },
            "activity_id": {
                "bsonType": "string",
                "description": "activity id"
            },
            "location": {
                "bsonType": "object",
                "description": "GeoJSON location",
                "properties": {
                    "type": {
                        "bsonType": "string",
                        "enum": ["Point"],
                        "description": "GeoJSON type"
                    },
                    "coordinates": {
                        "bsonType": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "bsonType": "double"
                        },
                        "description": "longitude and latitude"
                    }
                }
            },
            "altitude": {
                "bsonType": "double",
                "description": "altitude"
            },
            "date_days": {
                "bsonType": "double",
                "description": "date days"
            },
            "date_time": {
                "bsonType": "date",
                "description": "date time"
            },
            "prev_date_time": {
                "bsonType": ["date", "null"],
                "description": "previous date time"
            },
            "transportation_mode": {
                "bsonType": ["string", "null"],
                "description": "transportation mode"
            }
        }
    }
}
