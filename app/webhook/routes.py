from flask import Blueprint, request, jsonify, current_app
from ..extensions import events_collection
from pymongo import errors
from ..models.event import create_event, Action

webhook = Blueprint("Webhook", __name__, url_prefix="/webhook")


@webhook.route("/receiver", methods=["POST"])
def receiver():
    current_app.logger.info("POST /webhook/receiver endpoint called")

    try:
        data = request.json
        event_type = request.headers.get("X-GitHub-Event")

        if not data or not event_type:
            current_app.logger.warning(
                "Invalid payload received: missing data or event type"
            )
            return jsonify({"status": "failure", "message": "Invalid payload"}), 400

        current_app.logger.info(f"Processing event of type: {event_type}")

        if event_type == Action.PUSH.value:
            current_app.logger.debug(
                f"Handling PUSH event for pusher: {data['pusher']['name']}"
            )
            event = create_event(
                data["pusher"]["name"],
                None,
                data["ref"].split("/")[-1],
                Action.PUSH,
                data["head_commit"]["id"],
            )
        elif event_type == Action.PULL_REQUEST.value:
            action = (
                Action.MERGE if data["pull_request"]["merged"] else Action.PULL_REQUEST
            )
            current_app.logger.debug(f"Handling PULL_REQUEST event, action: {action}")
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
            current_app.logger.warning(f"Unsupported event type: {event_type}")
            return (
                jsonify({"status": "failure", "message": "Unsupported event type"}),
                400,
            )

        if not event:
            current_app.logger.error("Event creation failed")
            return (
                jsonify({"status": "failure", "message": "Event creation failed"}),
                500,
            )

        inserted_item = events_collection.insert_one(event)
        event["_id"] = str(inserted_item.inserted_id)
        current_app.logger.info(f"Event successfully created with ID: {event['_id']}")
        return jsonify({"status": "success", "data": event}), 201

    except errors.PyMongoError as e:
        current_app.logger.error(f"Database error: {e}")
        return jsonify({"status": "failure", "message": "Database error"}), 500
    except KeyError as e:
        current_app.logger.warning(f"Missing data in payload: {e}")
        return jsonify({"status": "failure", "message": f"Missing data: {e}"}), 400
    except Exception as e:
        current_app.logger.exception(f"Unexpected error: {e}")
        return (
            jsonify({"status": "failure", "message": "An unexpected error occurred"}),
            500,
        )
