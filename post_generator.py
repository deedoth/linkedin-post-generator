from llm_helper import llm
from few_shot import FewShotPosts

few_shot = FewShotPosts()

def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 20 lines"
    
def get_prompt(length, language, tag, tone=None, keywords=None, writing_sample=None):
    length_str = get_length_str(length)
    prompt = f'''
        Generate a LinkedIn post using the below information. No Preamble
        1. Topic: {tag}
        2. Legnth: {length}
        3. Language: {language}
        The script for the generated post should always be English

        '''
    # Add tone if specified
    if tone:
        prompt += f"\n4. Tone: {tone}"
    
    # Add keywords if specified
    if keywords:
        prompt += f"\n5. Keywords: {keywords}"
    
    # Add writing sample if provided
    if writing_sample:
        prompt += f"\n6. Writing Style: Use the following writing sample as a reference for tone and style:\n\n{writing_sample}"
    
    # Add examples from FewShotPosts
    examples = few_shot.get_filtered_posts(length, language, tag)
    
    if len(examples) > 0:
        prompt += "\n7. Use the writing style as per the following examples:"
        for i, post in enumerate(examples):
            post_text = post['text']
            prompt += f"\n\n Example {i + 1}: \n\n {post_text}"

            if i == 2:
                break
    return prompt

def generate_post(length, language, tag, tone=None, keywords=None, writing_sample=None):
    prompt = get_prompt(length, language, tag, tone, keywords, writing_sample)
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    post = generate_post("Short", "English", "Jobs")
    print(post)