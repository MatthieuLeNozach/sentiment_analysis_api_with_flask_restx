from flask import request
from app.models import User, UsageTracking, RequestResponseLog
from app.extensions import db
from datetime import datetime
import json


import json

import json
from datetime import datetime
from .extensions import db
from .models import RequestResponseLog, UsageTracking

def log_request_response(user_id, model_name, request_content, response_content):
    # Query for an existing UsageTracking record
    usage = UsageTracking.query.filter_by(user_id=user_id, model_name=model_name).first()
    print("\n[USAGE]\n", usage)
    
    # If no record exists, create a new one
    if not usage:
        usage = UsageTracking(user_id=user_id, model_name=model_name, request_count=0, total_input_size=0)
        db.session.add(usage)
    
    # Update the usage tracking information
    usage.request_count += 1
    usage.total_input_size += len(request_content)
    usage.last_used = datetime.utcnow()
    
    print("print from log_request_response,  request_content: ", request_content)
    
    # Extract keys from response_content
    try:
        response_content_dict = json.loads(response_content)
    except json.JSONDecodeError:
        response_content_dict = {"error": "Invalid JSON response"}

    # Ensure only valid keys are included
    valid_keys = {'positive', 'neutral', 'negative', 'score', 'interpretation'}
    filtered_response_content = {k: v for k, v in response_content_dict.items() if k in valid_keys}
    
    # Log the request-response
    log = RequestResponseLog(user_id=user_id, model_name=model_name, request_content=request_content, **filtered_response_content)
    db.session.add(log)
    
    # Commit the changes to the database
    db.session.commit()