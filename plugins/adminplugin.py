import requests
import jwt
from datetime import datetime as date
from dotenv import load_dotenv
import os
import json
import logging
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from typing import Annotated
from utils.logging_config import setup_logging, log_separator, pretty_print_json

# Set up logging
logger = setup_logging(console_level=logging.INFO, file_level=logging.DEBUG)

class AdminPlugin:
    """
    Plugin for managing Ghost blog posts.
    """

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GHOST_API_KEY")
        self.api_url = os.getenv("GHOST_API_URL")
        if not self.api_key:
            raise ValueError("GHOST_API_KEY environment variable is not set.")
        if not self.api_url:
            raise ValueError("GHOST_API_URL environment variable is not set.")

    def _generate_token(self):
        """Generate JWT token for Ghost Admin API authentication"""
        id, secret = self.api_key.split(':')
        iat = int(date.now().timestamp())
        
        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
        payload = {
            'iat': iat,
            'exp': iat + 5 * 60,
            'aud': '/admin/'
        }
        
        return jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

    def _content_to_lexical(self, content: str) -> str:
        """Convert content to Lexical format"""
        log_separator(logger, "Converting content to Lexical format")
        logger.debug(f"Raw content type: {type(content)}")
        logger.debug(f"Raw content length: {len(str(content))}")
        logger.debug("Raw content:")
        logger.debug(content)

        # Handle potential dictionary input
        if isinstance(content, dict):
            if 'content' in content:
                content = content['content']
            elif 'topic' in content and 'content' in content:
                content = content['content']
            logger.debug("Extracted content from dictionary")
            
        # Ensure content is a string
        content = str(content).strip()
        
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        logger.debug(f"Number of paragraphs: {len(paragraphs)}")
        
        children = []
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if para:
                if para.startswith('#'):
                    # Handle headers
                    parts = para.split('\n', 1)
                    header = parts[0]
                    level = len(header.split()[0])  # Count the number of #
                    text = header.lstrip('#').strip()
                    
                    node = {
                        "type": "heading",
                        "tag": f"h{level}",
                        "format": "",
                        "indent": 0,
                        "version": 1,
                        "children": [{
                            "type": "text",
                            "text": text,
                            "format": 0,
                            "detail": 0,
                            "mode": "normal",
                            "style": ""
                        }]
                    }
                    children.append(node)
                    
                    # If there's content after the header, add it as a paragraph
                    if len(parts) > 1 and parts[1].strip():
                        children.append({
                            "type": "paragraph",
                            "format": "",
                            "indent": 0,
                            "version": 1,
                            "children": [{
                                "type": "text",
                                "text": parts[1].strip(),
                                "format": 0,
                                "detail": 0,
                                "mode": "normal",
                                "style": ""
                            }]
                        })
                else:
                    # Regular paragraph
                    node = {
                        "type": "paragraph",
                        "format": "",
                        "indent": 0,
                        "version": 1,
                        "children": [{
                            "type": "text",
                            "text": para,
                            "format": 0,
                            "detail": 0,
                            "mode": "normal",
                            "style": ""
                        }]
                    }
                    children.append(node)
                
                logger.debug(f"Processed node {i+1}:")
                pretty_print_json(node, logger)
        
        lexical = {
            "root": {
                "type": "root",
                "format": "",
                "indent": 0,
                "version": 1,
                "children": children
            }
        }
        
        log_separator(logger, "Final Lexical structure")
        pretty_print_json(lexical, logger)
        
        return json.dumps(lexical)

    @kernel_function(description="Post a blog draft to Ghost")
    def post_draft(
        self,
        title: Annotated[str, "The title of the blog post"],
        content: Annotated[str, "The content of the blog post"]
    ) -> Annotated[str, "Result of posting the draft"]:
        try:
            log_separator(logger, "POST DRAFT FUNCTION CALLED", logging.INFO)
            logger.info(f"Title: {title}")
            logger.debug("Content:")
            logger.debug(content)
            
            token = self._generate_token()
            headers = {
                'Authorization': f'Ghost {token}',
                'Content-Type': 'application/json'
            }
            
            # Convert content to Lexical format
            lexical = self._content_to_lexical(content)
            
            # Create a slug from the title
            slug = title.lower().replace(' ', '-')
            
            post_data = {
                "posts": [{
                    "title": title,
                    "slug": slug,
                    "lexical": lexical,
                    "status": "draft",
                    "visibility": "public",
                    "created_at": date.timezone.utc().isoformat() + 'Z',
                    "updated_at": date.timezome.utc().isoformat() + 'Z'
                }]
            }
            
            log_separator(logger, "SENDING REQUEST TO GHOST")
            logger.debug(f"URL: {self.api_url.rstrip('/')}/ghost/api/admin/posts")
            logger.debug("Headers:")
            pretty_print_json(headers, logger)
            logger.debug("Post Data:")
            pretty_print_json(post_data, logger)
            
            response = requests.post(
                f"{self.api_url.rstrip('/')}/ghost/api/admin/posts",
                json=post_data,
                headers=headers
            )
            
            log_separator(logger, "RECEIVED RESPONSE FROM GHOST")
            logger.debug(f"Status Code: {response.status_code}")
            logger.debug("Response Headers:")
            pretty_print_json(dict(response.headers), logger)
            
            if response.text:
                logger.debug("Response Body:")
                pretty_print_json(response.json(), logger)
            
            if response.status_code == 201:
                success_msg = f"Successfully created the blog draft: {title}"
                logger.info(success_msg)
                return success_msg
            else:
                error_msg = f"Failed to create the blog draft. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error creating blog draft: {str(e)}"
            logger.exception(error_msg)
            return error_msg
