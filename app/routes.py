from flask import Blueprint, request, jsonify, render_template
from .extensions import events_collection
from pymongo import errors
from datetime import datetime, timedelta, timezone

root = Blueprint("endpoints", __name__, url_prefix="/")


@root.route("/events", methods=["GET"])
def get_events():
    """
    Fetch a list of events with pagination.
    """
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit
        events = (
            events_collection.find(
                {"timestamp": {"$gte": datetime.utcnow() - timedelta(seconds=15)}}
            )
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )
        total_count = events_collection.count_documents({})
        total_pages = (total_count // limit) + (1 if total_count % limit > 0 else 0)
        events_data = [
            {
                **event,
                "_id": str(event["_id"]),
                "timestamp": event["timestamp"]
                .replace(tzinfo=timezone.utc)
                .isoformat(),
            }
            for event in events
        ]

        return jsonify(
            {
                "events": events_data,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }
        )

    except errors.PyMongoError as e:
        return jsonify({"status": "failure", "message": "Database error"}), 500
    except ValueError as e:
        return (
            jsonify({"status": "failure", "message": "Invalid pagination parameters"}),
            400,
        )
    except Exception as e:
        return (
            jsonify({"status": "failure", "message": "An unexpected error occurred"}),
            500,
        )


@root.route("/")
def index():
    return render_template("index.html")
