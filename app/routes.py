from flask import Blueprint, request, jsonify, render_template, current_app
from .extensions import events_collection
from pymongo import errors
from datetime import datetime, timedelta, timezone

root = Blueprint("endpoints", __name__, url_prefix="/")


@root.route("/events", methods=["GET"])
def get_events():
    current_app.logger.info("GET /events endpoint called")

    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit

        current_app.logger.debug(
            f"Pagination parameters - Page: {page}, Limit: {limit}, Skip: {skip}"
        )

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

        current_app.logger.debug(
            f"Total events: {total_count}, Total pages: {total_pages}"
        )

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

        current_app.logger.info(f"{len(events_data)} events returned for page {page}")
        return jsonify(
            {
                "events": events_data,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
            }
        )

    except errors.PyMongoError as e:
        current_app.logger.error(f"Database error occurred: {e}")
        return jsonify({"status": "failure", "message": "Database error"}), 500
    except ValueError as e:
        current_app.logger.warning(f"Invalid pagination parameters: {e}")
        return (
            jsonify({"status": "failure", "message": "Invalid pagination parameters"}),
            400,
        )
    except Exception as e:
        current_app.logger.exception(f"Unexpected error occurred: {e}")
        return (
            jsonify({"status": "failure", "message": "An unexpected error occurred"}),
            500,
        )


@root.route("/")
def index():
    current_app.logger.info("GET / endpoint called")
    return render_template("index.html")
