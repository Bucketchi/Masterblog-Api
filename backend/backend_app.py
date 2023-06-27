from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def find_post_by_id(post_id):
    """ Find the book with the id `book_id`.
    If there is no book with this id, return None. """
    for post in POSTS:
        if post['id'] == post_id:
            return post
    return None


def validate_post_data(data):
    missing_fields = []
    if "title" not in data:
        missing_fields.append("title")
    if "content" not in data:
        missing_fields.append("content")

    if missing_fields:
        return False, missing_fields
    return True, missing_fields


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        new_post = request.get_json()

        valid, missing_fields = validate_post_data(new_post)

        if not valid:
            return jsonify({"error": "Invalid post data", "missing_fields": missing_fields}), 400

        # Generate a new ID for the post
        new_id = max(post['id'] for post in POSTS) + 1
        new_post['id'] = new_id

        # Add the new post to our list
        POSTS.append(new_post)

        # Return the new post data to the client
        return jsonify(new_post), 201

    query = request.args
    if query.keys():
        try:
            if query["direction"] == "asc":
                sorted_posts = sorted(POSTS, key=lambda x: x[f"{query['sort']}"])
            if query["direction"] == "desc":
                sorted_posts = sorted(POSTS, key=lambda x: x[f"{query['sort']}"], reverse=True)
        except KeyError:
            return jsonify({"error": "Invalid sort or direction parameter"}), 400
        return jsonify(sorted_posts)
    return jsonify(POSTS)


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    # Find the post with the given ID
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    # Remove the post from the list
    POSTS.remove(post)

    # Return the deleted post
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    # Find the post with the given ID
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    # Update the post with the new data
    new_data = request.get_json()

    if "title" in new_data:
        post["title"] = new_data["title"]
    if "content" in new_data:
        post["content"] = new_data["content"]

    # Return the updated post
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    query = request.args
    search_results = [post for post in POSTS if query.get('title') in post['title']
                      or query.get('content') in post['content']]
    return jsonify(search_results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
