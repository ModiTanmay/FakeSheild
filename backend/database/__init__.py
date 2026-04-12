import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv()

_client = None
_db = None
_indexes_ready = False


def _parse_post_timestamp(timestamp_value):
	if not timestamp_value:
		return None

	if isinstance(timestamp_value, datetime):
		return timestamp_value

	if isinstance(timestamp_value, (int, float)):
		return datetime.utcfromtimestamp(timestamp_value)

	if isinstance(timestamp_value, str):
		cleaned = timestamp_value.replace("Z", "+00:00")
		try:
			return datetime.fromisoformat(cleaned)
		except ValueError:
			return None

	return None


def _ensure_indexes(db):
	global _indexes_ready
	if _indexes_ready:
		return

	db.instagram_profiles.create_index("username", unique=True)
	db.instagram_profiles.create_index("instagram_id")
	db.instagram_profiles.create_index("scraped_at")

	db.instagram_posts.create_index("post_id", unique=True)
	db.instagram_posts.create_index("owner_username")
	db.instagram_posts.create_index("timestamp")

	db.scan_history.create_index("scan_id", unique=True)
	db.scan_history.create_index("created_at")

	_indexes_ready = True


def get_db():
	"""Return cached MongoDB database handle."""
	global _client, _db

	if _db is not None:
		return _db

	mongodb_uri = os.getenv("MONGODB_URI", "").strip()
	if not mongodb_uri:
		raise RuntimeError("MONGODB_URI is not configured in environment variables")

	db_name = os.getenv("DB_NAME", "fakeshield")

	_client = MongoClient(mongodb_uri)
	_db = _client[db_name]
	_ensure_indexes(_db)
	return _db


def save_profile(profile_data: dict, scan_id: str) -> str:
	"""Upsert one Instagram profile document and return document id as a string."""
	db = get_db()

	about = profile_data.get("about") or {}
	username = (profile_data.get("username") or "").lower()
	if not username:
		raise ValueError("profile_data.username is required")

	document = {
		"instagram_id": profile_data.get("id"),
		"username": username,
		"full_name": profile_data.get("fullName"),
		"biography": profile_data.get("biography"),
		"followers_count": profile_data.get("followersCount", 0),
		"follows_count": profile_data.get("followsCount", 0),
		"posts_count": profile_data.get("postsCount", 0),
		"igtv_video_count": profile_data.get("igtvVideoCount", 0),
		"highlight_reel_count": profile_data.get("highlightReelCount", 0),
		"is_business_account": profile_data.get("isBusinessAccount", False),
		"business_category": profile_data.get("businessCategoryName"),
		"is_verified": profile_data.get("verified", False),
		"is_private": profile_data.get("private", False),
		"joined_recently": profile_data.get("joinedRecently", False),
		"profile_pic_url": profile_data.get("profilePicUrl"),
		"external_url": profile_data.get("externalUrl"),
		"profile_url": profile_data.get("url"),
		"about": {
			"date_joined": about.get("date_joined"),
			"date_joined_as_timestamp": about.get("date_joined_as_timestamp"),
			"country": about.get("country"),
			"former_usernames": about.get("former_usernames"),
			"date_verified": about.get("date_verified"),
		},
		"related_profiles": profile_data.get("relatedProfiles", []),
		"scraped_at": datetime.utcnow(),
		"scan_id": scan_id,
	}

	result = db.instagram_profiles.update_one(
		{"username": username},
		{"$set": document},
		upsert=True,
	)

	if result.upserted_id is not None:
		return str(result.upserted_id)

	matched = db.instagram_profiles.find_one({"username": username}, {"_id": 1})
	return str(matched.get("_id")) if matched else username


def save_posts(profile_data: dict, scan_id: str) -> int:
	"""Bulk-upsert profile posts and return count of processed posts."""
	db = get_db()

	latest_posts = profile_data.get("latestPosts", []) or []
	owner_username = (profile_data.get("username") or "").lower()
	owner_id = profile_data.get("id")

	operations = []
	for post in latest_posts:
		post_id = post.get("id")
		if not post_id:
			continue

		document = {
			"post_id": post_id,
			"short_code": post.get("shortCode"),
			"owner_username": owner_username,
			"owner_id": owner_id,
			"type": post.get("type"),
			"caption": post.get("caption"),
			"hashtags": post.get("hashtags", []),
			"mentions": post.get("mentions", []),
			"post_url": post.get("url"),
			"display_url": post.get("displayUrl"),
			"likes_count": post.get("likesCount", 0),
			"comments_count": post.get("commentsCount", 0),
			"video_view_count": post.get("videoViewCount"),
			"timestamp": _parse_post_timestamp(post.get("timestamp")),
			"is_pinned": post.get("isPinned", False),
			"scraped_at": datetime.utcnow(),
			"scan_id": scan_id,
		}

		operations.append(
			UpdateOne(
				{"post_id": post_id},
				{"$set": document},
				upsert=True,
			)
		)

	if not operations:
		return 0

	db.instagram_posts.bulk_write(operations, ordered=False)
	return len(operations)


def create_scan_record(scan_id: str, input_value: str, platform: str) -> None:
	"""Insert a new pending scan record."""
	db = get_db()
	db.scan_history.insert_one(
		{
			"scan_id": scan_id,
			"input": input_value,
			"platform": platform,
			"status": "pending",
			"profiles_found": 0,
			"posts_found": 0,
			"created_at": datetime.utcnow(),
			"completed_at": None,
		}
	)


def update_scan_record(scan_id: str, status: str, profiles_found: int, posts_found: int) -> None:
	"""Update scan status, counts, and completion time."""
	db = get_db()
	db.scan_history.update_one(
		{"scan_id": scan_id},
		{
			"$set": {
				"status": status,
				"profiles_found": profiles_found,
				"posts_found": posts_found,
				"completed_at": datetime.utcnow(),
			}
		},
	)


def save_scan_result(scan_id: str, result_payload: dict) -> None:
	"""Persist full scan response payload for later retrieval by scan id."""
	db = get_db()
	db.scan_history.update_one(
		{"scan_id": scan_id},
		{"$set": {"result_payload": result_payload}},
	)


def get_scan_result(scan_id: str) -> dict | None:
	"""Return stored scan payload for a given scan id."""
	db = get_db()
	doc = db.scan_history.find_one({"scan_id": scan_id}, {"_id": 0, "result_payload": 1})
	if not doc:
		return None
	return doc.get("result_payload")


def get_scan_history(limit: int = 50) -> list[dict]:
	"""Return recent scan history in frontend-friendly shape."""
	db = get_db()
	cursor = db.scan_history.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)

	history_items = []
	for doc in cursor:
		result_payload = doc.get("result_payload") or {}
		summary = result_payload.get("summary") or {}
		timestamp = doc.get("completed_at") or doc.get("created_at")
		platform_value = doc.get("platform", "instagram")
		platforms = platform_value if isinstance(platform_value, list) else [platform_value]

		history_items.append(
			{
				"scan_id": doc.get("scan_id"),
				"profile_url": doc.get("input", ""),
				"timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else "",
				"total_found": summary.get("total_accounts_found", 0),
				"platforms": platforms,
			}
		)

	return history_items
