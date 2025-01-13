import requests
import jwt
from datetime import datetime as date
from dotenv import load_dotenv
import os
import logging
import json
import uuid
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from typing import Annotated

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

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
        logger.debug("Converting content to Lexical format:")
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
                        "type": f"heading",
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
                
                logger.debug(f"Processed node {i+1}: {json.dumps(node, indent=2)}")
        
        lexical = {
            "root": {
                "type": "root",
                "format": "",
                "indent": 0,
                "version": 1,
                "children": children
            }
        }
        
        lexical_str = json.dumps(lexical)
        logger.debug("Final Lexical structure:")
        logger.debug(json.dumps(lexical, indent=2))
        
        return lexical_str

    @kernel_function(description="Post a blog draft to Ghost")
    def post_draft(
        self,
        title: Annotated[str, "The title of the blog post"],
        content: Annotated[str, "The content of the blog post"]
    ) -> Annotated[str, "Result of posting the draft"]:
        try:
            logger.debug("="*50)
            logger.debug("POST DRAFT FUNCTION CALLED")
            logger.debug("="*50)
            logger.debug(f"Title type: {type(title)}")
            logger.debug(f"Content type: {type(content)}")
            logger.debug(f"Title: {title}")
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
                    "created_at": date.utcnow().isoformat() + 'Z',
                    "updated_at": date.utcnow().isoformat() + 'Z'
                }]
            }
            
            logger.debug("="*50)
            logger.debug("SENDING REQUEST")
            logger.debug("="*50)
            logger.debug(f"URL: {self.api_url.rstrip('/')}/ghost/api/admin/posts")
            logger.debug(f"Headers: {json.dumps(headers, indent=2)}")
            logger.debug(f"Post Data: {json.dumps(post_data, indent=2)}")
            
            response = requests.post(
                f"{self.api_url.rstrip('/')}/ghost/api/admin/posts",
                json=post_data,
                headers=headers
            )
            
            logger.debug("="*50)
            logger.debug("RECEIVED RESPONSE")
            logger.debug("="*50)
            logger.debug(f"Status Code: {response.status_code}")
            logger.debug(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
            logger.debug(f"Response Body: {json.dumps(response.json() if response.text else {}, indent=2)}")
            
            if response.status_code == 201:
                logger.info("Draft created successfully!")
                return f"Successfully created draft: {title}"
            else:
                error_msg = f"Failed to create draft. Status: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error creating draft: {str(e)}"
            logger.exception(error_msg)
            return error_msg
