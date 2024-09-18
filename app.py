from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from enum import Enum

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["events"]
events_collection = db["github_webhooks"]

class Action(Enum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    MERGE = "merge"

def create_event(author, from_branch, to_branch, action, request_id):
    return {
        "author": author,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": datetime.utcnow().isoformat(),
        "action": action.value,
        "request_id": request_id,
    }

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    if event_type == Action.PUSH.value:
        event = create_event(
            data["pusher"]["name"],
            None,
            data["ref"].split("/")[-1],
            Action.PUSH,
            data["head_commit"]["id"],
        )
    elif event_type == Action.PULL_REQUEST.value:
        action = Action.MERGE if data["pull_request"]["merged"] else Action.PULL_REQUEST
        event = create_event(
            data["pull_request"]["user"]["login"],
            data["pull_request"]["head"]["ref"],
            data["pull_request"]["base"]["ref"],
            action,
            (
                data["pull_request"]["id"]
                if action == Action.PULL_REQUEST
                else data["pull_request"]["merge_commit_sha"]
            ),
        )
    else:
        return jsonify({"status": "failure"}), 400

    event["_id"] = str(events_collection.insert_one(event).inserted_id)
    return jsonify({"status": "success", "data": event}), 201

@app.route("/events", methods=["GET"])
def get_events():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    skip = (page - 1) * limit

    events = events_collection.find().sort("timestamp", -1).skip(skip).limit(limit)
    total_count = events_collection.count_documents({})
    total_pages = (total_count // limit) + (1 if total_count % limit > 0 else 0)

    events_data = [{**event, "_id": str(event["_id"])} for event in events]

    return jsonify(
        {
            "events": events_data,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }
    )

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
