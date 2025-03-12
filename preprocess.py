import json
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from llm_helper import llm

def process_posts(raw_file_path, processed_file_path="data/processed_posts.json"):
    """
    Process the raw posts data and save it to a new JSON file.
    """
    enriched_posts = []
    # Load the raw posts data from the JSON file
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)
        for post in posts:
            try:
                metadata = extract_metadata(post['text'])
                post_with_metadata = post | metadata
                enriched_posts.append(post_with_metadata)
            except OutputParserException as e:
                print(f"Error parsing metadata for post: {e}")
    
    # Get unified tags for enriched posts
    unified_tags = get_unified_tags(enriched_posts)

    # Update tags in enriched posts
    for post in enriched_posts:
        current_tags = post['tags']
        new_tags = {unified_tags.get(tag, tag) for tag in current_tags}
        post['tags'] = list(new_tags)
        
    # Save the enriched posts to a new JSON file
    with open(processed_file_path, 'w', encoding='utf-8') as file:
        json.dump(enriched_posts, file, indent=4, ensure_ascii=False)
        print("Posts data has been processed and saved to", processed_file_path)

def get_unified_tags(posts_with_metadata):
    """
    Get unified tags by mapping similar tags together using an LLM.
    """
    unique_tags = set()
    for post in posts_with_metadata:
        unique_tags.update(post['tags'])
    unique_tags_list = ', '.join(unique_tags)
    
    template = '''
    I will give you a list of tags. You need to unify tags with the following requirements:
    1. Tags are unified and merged to create a shorter list.
    2. Each tag should follow title case convention.
    3. Output should be a JSON object, No preamble.
    4. Output should have a mapping of original tag and the unified tag.

    Here is the list of tags:
    {tags}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"tags": str(unique_tags_list)})

    if not response.content.strip():
        raise OutputParserException("Empty response received for unified tags.")
    
    try:
        # Parse the JSON response using json.loads
        res = json.loads(response.content.strip())
    except json.JSONDecodeError as e:
        print(f"LLM Response for Tags: {response.content.strip()}")
        raise OutputParserException(f"Failed to parse JSON for tags: {str(e)}")
    return res

def extract_metadata(post):
    """
    Extract metadata such as line count, language, and tags from a LinkedIn post using an LLM.
    """
    template = '''
    You are given a LinkedIn post. You need to extract number of lines, language of the post, and tags.
    1. Return a valid JSON. No preamble.
    2. JSON object should have exactly three keys: line_count, language, tags
    3. tags is an array of text tags. Extract maximum two tags.
    4. each tag should be alphabet. No other character.
    5. The first letter of each tag should be capitalized.
    6. Language should be English or French. If you are unsure, return English.

    Here is the actual post in which you need to perform this task: {post}
    
    Return only the JSON object without any additional text.
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'post': post})

    if not response.content.strip():
        raise OutputParserException("Empty response received for metadata.")
    
    try:
        # Clean the response to remove ```json and ``` wrappers if present
        cleaned_response = response.content.strip().strip("```").replace("json", "").strip()
        
        # Parse the JSON response using json.loads
        res = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"LLM Response for Metadata: {response.content.strip()}")
        raise OutputParserException(f"Failed to parse JSON for metadata: {str(e)}")
    return res

if __name__ == "__main__":
    # Define the file paths for the raw and processed data
    process_posts("data/raw_posts.json", "data/processed_posts.json")
