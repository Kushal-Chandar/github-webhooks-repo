from flask import Blueprint, request, jsonify
from ..extensions import events_collection
from pymongo import errors
from ..models.event import create_event, Action

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route("/receiver", methods=["POST"])
def receiver():
    try:
        data = request.json
        event_type = request.headers.get("X-GitHub-Event")

        if not data or not event_type:
            return jsonify({"status": "failure", "message": "Invalid payload"}), 400

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
            return jsonify({"status": "failure", "message": "Unsupported event type"}), 400

        if not event:
            return jsonify({"status": "failure", "message": "Event creation failed"}), 500

        event["_id"] = str(events_collection.insert_one(event).inserted_id)
        return jsonify({"status": "success", "data": event}), 201

    except errors.PyMongoError as e:
        return jsonify({"status": "failure", "message": "Database error"}), 500
    except KeyError as e:
        return jsonify({"status": "failure", "message": f"Missing data: {e}"}), 400
    except Exception as e:
        return jsonify({"status": "failure", "message": "An unexpected error occurred"}), 500
