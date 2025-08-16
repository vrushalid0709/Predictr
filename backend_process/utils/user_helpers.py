from db_connection.db import db

def generate_user_id():
    counters = db['counters']
    counter_doc = counters.find_one_and_update(
        {"_id": "user_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return f"USR-{counter_doc['seq']}"
