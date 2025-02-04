from datetime import datetime
import git
import logging
import os
import re
import sys

from chatgpt_client import (
    CHAT_GPT_DEFAULT_API_MODEL,
    CHAT_GPT_WEB_MODEL,
    get_chatbot_response,
)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

BLOG_MAX_TOKEN_AMOUNT = 1500
EDIT_LOOPS = 2
YINYANGWAY_GITHUB_URL = "https://github.com/yangdafish/yinyangway.git"
# POSTS_DIR = "../../_posts"
POSTS_DIR = "_posts"
CHAT_GPT_BLOG_RETURN_FORMAT = """a blog post including a title, layout, the current date, unique categories and tags in a mediumish jekyll format"""
CHAT_GPT_BLOG_SUBJECT = "chinese traditional medicine "


def generate_blog_prompt(blog_title):
    prompt = f"""write a blog post in a soothing, lyrical, conversational tone 
        for {CHAT_GPT_BLOG_SUBJECT}
        on the subject of {blog_title}.
        Try to include an attention-grabbing headline,
        a captivating lead paragraph,
        and a compelling conclusion,
        without being overly repetitive in phrases or wording. 
        Have multiple sections with subheadings.
        Include up to one relevant historical quote,
        up to one relevant metric, 
        and up to one interesting factoid. 
        Return the result as {CHAT_GPT_BLOG_RETURN_FORMAT}
    """
    # Start with the compelling call-to-action or answer first.
    # Group and summarise the supporting arguments.
    # Logically order the supporting ideas.
    # Include a reputable external source if relevant for followup information.

    logging.info(f"Constructed ChatGpt Prompt {prompt}")
    return prompt


def generate_blog_first_edit_prompt(blog_content):
    prompt = f"""
        rate and critique the following blog post on a scale of 1 to 10
        Then apply the suggested improvements to the blog and output the edited result

        Return the result as {CHAT_GPT_BLOG_RETURN_FORMAT}

        {blog_content}
    """
    return prompt


def generate_blog_editing_prompt(blog_content):
    prompt = f"""
        Edit the following blog post to make it more interesting,
        more engaging, more compelling, and more emotionally resonant.
        
        Return the result as {CHAT_GPT_BLOG_RETURN_FORMAT}

        {blog_content}
    """
    # logging.info(f"Constructed Edit Prompt {prompt}")
    return prompt


def create_blog_post_file(blog_content, blog_title):
    # This function will take the passed blog_content and blog_title and create a new file in the _posts folder
    # In the format of: YYYY-MM-DD-{blog_title}.md
    # It will return the path to the new file
    logging.info(f"Creating Blog Post File {blog_title}")

    # Get the current date in YYYY-MM-DD format
    date = datetime.now().strftime("%Y-%m-%d")

    # First, we need to create the file name
    file_name = f"{date}-{blog_title}.md"
    # Next, we need to create the file path
    file_path = f"{POSTS_DIR}/{file_name}"
    # Finally, we can create the file and write the content to it

    # Open the file_path/file_name in write mode
    file = open(file_path, "w+")
    file.write(blog_content)
    logging.info("Completed writing blog post file")
    file.close()

    return file_path


def get_blog_content(blog_title):
    # This function will take the passed blog_title and use it as a parameter to the ChatGPT API
    # It will ask the API to create a blog content with the conditions defined in BLOG_CONDITIONS
    # It will return the blog content

    # First, we need to create the parameters for the API call
    # params = {
    #     "title": blog_title,
    #     "conditions": BLOG_CONDITIONS,
    # }

    blog_prompt = generate_blog_prompt(blog_title)
    # Next, we need to make the API call
    blog_content_response = get_chatbot_response(
        blog_prompt,
        max_tokens=BLOG_MAX_TOKEN_AMOUNT,
        # model=CHAT_GPT_DEFAULT_API_MODEL
    )
    logging.info(f"Recieved blog content response {blog_content_response}")

    edit_prompt = generate_blog_first_edit_prompt(blog_content_response)
    # Apply first pass edit to blog content
    edited_blog_content = get_chatbot_response(
        edit_prompt,
        max_tokens=BLOG_MAX_TOKEN_AMOUNT,
    )

    for i in range(EDIT_LOOPS):
        logging.info(f"Editing Blog Content {i} of {EDIT_LOOPS}")
        edit_prompt = generate_blog_editing_prompt(edited_blog_content)
        blog_content_response = get_chatbot_response(
            edit_prompt, max_tokens=BLOG_MAX_TOKEN_AMOUNT
        )
    logging.info(f"Recieved edited blog content response {blog_content_response}")
    return blog_content_response


def process_blog_title(blog_title):
    # This function takes the blog title, casts it to lowercase, and replaces spaces with underscores
    # It also removes any non-alphanumeric characters

    # First, we need to cast the blog title to lowercase
    blog_title_lower = blog_title.lower()
    # Next, we need to replace spaces with underscores
    blog_title_space = blog_title_lower.replace(" ", "_")
    # replace non-word characters with _
    blog_title_final = re.sub(r"\W+", "_", blog_title_space)
    logging.info(
        f"Returning blog title {blog_title_final} from process_blog_title {blog_title}"
    )
    return blog_title_final


def write_new_blog_to_local(blog_title):
    # This function will take the passed blog_title and use it to create a new blog post
    # It will then write the new blog post to the local _posts folder
    # It will return the path to the new blog post

    blog_content = get_blog_content(blog_title)

    normalized_blog_title = process_blog_title(blog_title)
    blog_path = create_blog_post_file(blog_content, normalized_blog_title)
    logging.info(f"Created new blog post {blog_path}")
    return blog_path


def generate_blog_title_from_chatbot():
    # generate blog title using chatgpt
    # if the blog title already exists, generate a new one
    # return the blog title

    existing_blog_titles = []
    # Scan the _posts folder for existing blog titles
    for file in os.listdir(POSTS_DIR):
        if file.endswith(".md"):
            # existing_blog_titles.append(file)
            # scan the file for the blog title
            with open(f"_posts/{file}", "r") as f:
                for line in f:
                    if line.startswith("title:"):
                        existing_blog_titles.append(line.split(":")[1].strip())
                        break
    logging.info(f"Existing Titles {existing_blog_titles}")
    prompt = f"""
        Generate a single captivating and high-performing blog titles not in this list {existing_blog_titles}
        incorporating current trends and popular topics in a creative and engaging way
        for a subject related to chinese traditional medicine.
        The subject of the title should invoque a sense of curiosity and intrigue.

    """  ## Along with a small summary of the blog post.
    logging.info(f"Prompt {prompt}")
    blog_title = get_chatbot_response(
        prompt,
        max_tokens=BLOG_MAX_TOKEN_AMOUNT,
    )
    logging.info(f"Recieved blog title response {blog_title}")
    return blog_title


def update_yinyangway(blog_title):
    # This function will take the current changes in the local repo and make a commit with the passed blog_path
    # The commit message will be "Added new blog post {blog_path}"
    # It will then push the changes to the remote repo on GitHub
    # It will return the commit hash
    # if not blog_title:
    #     blog_title = generate_blog_prompt_from_chatbot()

    new_blog_path = write_new_blog_to_local(blog_title)
    # new_blog_path = f"{POSTS_DIR}/}"
    # new_blog_path = "_posts/2023-04-24-the_art_of_acupuncture__demystifying_the_ancient_practice_and_its_benefits_for_modern_living.md"
    # commit_message = git_add(
    #     new_blog_path, "Added new blog post {blog_title}"
    # )
    # logging.info(f"Commited {commit_message}")
    logging.info(f"Created New Blog {new_blog_path} For Title {blog_title}")
    return new_blog_path


def git_add(file):
    repo = git.Repo("./")
    # origin = repo.remote(name="origin")
    # origin.set_url("git@github.com:yangdafish/mediumish-yinyangway.git")

    # Check for uncommitted changes
    add_result = None
    if repo.is_dirty():
        # Stage updated files
        # repo.git.add(update=True)

        add_result = repo.git.add(file)
        # commit_message = f"Added new blog post {blog_title}"
        # commit = repo.index.commit(commit_message)
        # Set up the authentication token
        # git_auth_token = os.getenv("GITHUB_TOKEN")
        # logging.info(f"Committed changes to local repo {commit}")
        # Set up the push URL with the token
        # remote_name = "origin"
        # repo_url = f"https://yangdafish:{git_auth_token}@github.com/yangdafish/mediumish-yinyangway.git"
        # repo.git.config(f"remote.{remote_name}.url", repo_url, local=True)

        # Push the changes to the remote repository
        # push_result = repo.git.push()
        # logging.info(f"Pushed changes to remote repo {push_result}")

    return add_result


def git_commit(commit_message):
    repo = git.Repo("./")
    commit = repo.index.commit(commit_message)
    logging.info(f"Committed changes to local repo {commit}")
    return commit


if __name__ == "__main__":
    blog_title = generate_blog_title_from_chatbot()
    update_yinyangway(blog_title)
