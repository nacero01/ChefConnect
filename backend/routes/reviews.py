from fastapi import APIRouter
from database import get_db_connection
from schemas.reviews import ReviewRequest

router = APIRouter(tags=["Reviews"])

@router.post("/reviews")
def create_review(data:ReviewRequest):

    chef_id = data.chef_id
    user_id = data.user_id
    rating = data.rating
    comment = data.comment


    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    review_sql = """
    INSERT INTO Review 
    (chef_id, user_id, rating, comment)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(review_sql, (chef_id, user_id, rating, comment))

    update_sql = """
    UPDATE Chef
    SET rating = (
        SELECT AVG(rating) 
        FROM Review 
        WHERE chef_id = %s
    )
    WHERE chef_id = %s
    """
    cursor.execute(update_sql, (chef_id, chef_id))
    conn.commit()

    cursor.close()
    conn.close()
    return {"message": "Review submitted successfully!"}

@router.get("/chefs/{chef_id}/reviews")
def get_chef_reviews(chef_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        r.review_id, 
        r.rating, 
        r.comment, 
        r.created_at,
        u.username AS reviewer_name
    FROM Review r
    JOIN User u ON r.user_id = u.user_id
    WHERE r.chef_id = %s
    ORDER BY r.created_at DESC
    """

    cursor.execute(sql, (chef_id,))
    reviews = cursor.fetchall()

    cursor.close()
    conn.close()
    return {"reviews": reviews}