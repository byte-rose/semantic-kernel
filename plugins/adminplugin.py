import requests  # pip install requests
import jwt  # pip install pyjwt
from datetime import datetime as date
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

try:
    # Load environment variables
    logger.debug("Loading environment variables...")
    load_dotenv()


    # Retrieve Admin API key
    key = os.getenv("GHOST_API_KEY")
    if key is None:
        logger.error("GHOST_ADMIN_API_KEY environment variable is not set.")
        raise ValueError("GHOST_ADMIN_API_KEY environment variable is not set.")
    else:
        logger.debug("GHOST_ADMIN_API_KEY retrieved successfully.")

    # Split the key into ID and SECRET
    logger.debug("Splitting the API key into ID and SECRET...")
    id, secret = key.split(':')
    logger.debug(f"ID: {id}")

    # Prepare header and payload
    iat = int(date.now().timestamp())
    logger.debug(f"Current timestamp (iat): {iat}")

    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,  # Token valid for 5 minutes
        'aud': '/admin/'
    }
    logger.debug(f"JWT header: {header}")
    logger.debug(f"JWT payload: {payload}")

    # Create the token
    logger.debug("Encoding JWT token...")
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
    logger.debug(f"JWT token generated: {token}")

    # Make an authenticated request to create a post
    url = os.getenv("GHOST_API_URL")
    headers = {'Authorization': f'Ghost {token}'}
    body = {'posts': [{'title': 'Hello World'}]}
    logger.debug(f"Making a POST request to {url} with headers: {headers} and body: {body}")

    response = requests.post(url, json=body, headers=headers)
    logger.debug("Request made, awaiting response...")
    
    # Log response details
    if response.status_code == 201:  # Created
        logger.info("Post created successfully!")
    else:
        logger.error(f"Failed to create post. HTTP Status Code: {response.status_code}")
        logger.error(f"Response Content: {response.content}")

    print(response)

except Exception as e:
    logger.exception(f"An error occurred: {e}")


