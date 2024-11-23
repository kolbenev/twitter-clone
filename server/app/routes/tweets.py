from sqlalchemy.future import select

from fastapi import APIRouter, Header, HTTPException

from server.app.routes.utils import (
    lazy_get_user_by_apikey_or_id,
    get_all_tweet,
    get_user_by_apikey_or_id,
    lazy_get_tweet_by_id,
    get_like,
)
from server.database.confdb import session
from server.database.models import Tweet, User, Media, Like


router = APIRouter()


@router.get("/")
async def tweets(api_key: str = Header(...)):
    user: User = await lazy_get_user_by_apikey_or_id(session=session, api_key=api_key)
    tweets = await get_all_tweet(session=session)

    return {
        "result": True,
        "tweets": [
            {
                "id": tweet.id,
                "content": tweet.content,
                "attachment": [media.file_url for media in tweet.media],
                "author": {
                    "id": tweet.author.id,
                    "name": tweet.author.name,
                },
                "likes": [
                    {
                        "user_id": like.user_id,
                        "name": like.user.name,
                    }
                    for like in tweet.likes
                ],
            }
            for tweet in tweets
        ],
    }


@router.post("/")
async def post_tweets(tweet_data: dict, api_key: str = Header(...)):
    user: User = await lazy_get_user_by_apikey_or_id(session=session, api_key=api_key)

    if not tweet_data:
        raise HTTPException(status_code=400, detail="Tweet is empty")

    content = tweet_data.get("tweet_data")
    new_tweet = Tweet(content=content, author_id=user.id)
    session.add(new_tweet)
    await session.commit()

    media_ids = tweet_data.get("tweet_media_ids", [])
    if media_ids:
        media_query = await session.execute(
            select(Media).where(Media.id.in_(media_ids))
        )
        media_items = media_query.scalars().all()
        for media in media_items:
            media.tweet = new_tweet

    return {"result": True, "tweet_id": new_tweet.id}


@router.post("/{tweet_id}/likes")
async def like_the_tweet(tweet_id: int, api_key: str = Header(...)):
    user: User = await lazy_get_user_by_apikey_or_id(session=session, api_key=api_key)
    tweet: Tweet = await lazy_get_tweet_by_id(tweet_id=tweet_id, session=session)
    try:
        like: Like = await get_like(user_id=user.id, tweet_id=tweet.id, session=session)
    except HTTPException:
        session.add(Like(user_id=user.id, tweet_id=tweet.id))
        await session.commit()
        return {"result": True}

    raise HTTPException(status_code=400, detail="Already liked the tweet")


@router.delete("/{tweet_id}/likes")
async def delete_like_on_the_tweet(tweet_id: int, api_key: str = Header(...)):
    user: User = await lazy_get_user_by_apikey_or_id(session=session, api_key=api_key)
    tweet: Tweet = await lazy_get_tweet_by_id(tweet_id=tweet_id, session=session)
    like: Like = await get_like(user_id=user.id, tweet_id=tweet.id, session=session)
    await session.delete(like)
    await session.commit()
    return {"result": True}


@router.delete("/{tweet_id}")
async def delete_tweet(tweet_id: int, api_key: str = Header(...)):
    user: User = await get_user_by_apikey_or_id(api_key=api_key, session=session)
    tweet: Tweet = await lazy_get_tweet_by_id(tweet_id=tweet_id, session=session)

    if tweet.author_id == user.id:
        await session.delete(tweet)
        await session.commit()
        return {"result": True}
    else:
        raise HTTPException(
            status_code=403, detail="The user is not the author of the tweet"
        )
