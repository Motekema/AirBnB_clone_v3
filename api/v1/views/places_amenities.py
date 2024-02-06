#!/usr/bin/python3
"""
A path for handling place and amenities linking
"""
from flask import jsonify, abort
from api.v1.views import app_views, storage

@app_views.route("/places/<place_id>/amenities", methods=["GET"], strict_slashes=False)
def amenity_by_place(place_id):
    """
    Get all amenities of a place
    :param place_id: Place ID
    :return: JSON representation of all amenities associated with the place
    """
    fetched_obj = storage.get("Place", str(place_id))

    if fetched_obj is None:
        abort(404)

    amenities_list = getattr(fetched_obj, 'amenities', [])
    all_amenities = [amenity.to_json() for amenity in amenities_list]

    return jsonify(all_amenities)


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=["DELETE"],
                 strict_slashes=False)
def unlink_amenity_from_place(place_id, amenity_id):
    """
    It un-links amenity in a place
    :param place_id: place id
    :param amenity_id: amenity id
    :return: error
    """
    if not storage.get("Place", str(place_id)):
        abort(404)
    if not storage.get("Amenity", str(amenity_id)):
        abort(404)

    fetched_obj = storage.get("Place", place_id)
    found = 0

    for obj in fetched_obj.amenities:
        if str(obj.id) == amenity_id:
            if getenv("HBNB_TYPE_STORAGE") == "db":
                fetched_obj.amenities.remove(obj)
            else:
                fetched_obj.amenity_ids.remove(obj.id)
            fetched_obj.save()
            found = 1
            break

    if found == 0:
        abort(404)
    else:
        resp = jsonify({})
        resp.status_code = 201
        return resp


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=["POST"],
                 strict_slashes=False)
def link_amenity_to_place(place_id, amenity_id):
    """
    It links amenity with place
    :param place_id: place id
    :param amenity_id: amenity id
    :return: return Amenity objects added or error
    """

    fetched_obj = storage.get("Place", str(place_id))
    amenity_obj = storage.get("Amenity", str(amenity_id))
    found_amenity = None

    if not fetched_obj or not amenity_obj:
        abort(404)

    for obj in fetched_obj.amenities:
        if str(obj.id) == amenity_id:
            found_amenity = obj
            break

    if found_amenity is not None:
        return jsonify(found_amenity.to_json())

    if getenv("HBNB_TYPE_STORAGE") == "db":
        fetched_obj.amenities.append(amenity_obj)
    else:
        fetched_obj.amenities = amenity_obj

    fetched_obj.save()

    resp = jsonify(amenity_obj.to_json())
    resp.status_code = 201

    return resp
