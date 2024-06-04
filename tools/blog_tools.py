import os
import csv
import requests
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
class BlogTools:

    def __init__(self, model_version):
        self.model_version = model_version
        self.client = OpenAI()

    def format_search_results(self, search_results):
        if not search_results:
            return "No relevant links found."
        links_formatted = "\n".join([f"{result['title']} - {result['url']}" for result in search_results])
        return f"\n\nRelated Links:\n{links_formatted}"

    def generate_blog_post(self, city, title, style):
        # Generate the blog post content
        content_prompt = f"Compose a unique and engaging 4000-word blog post tailored to motivate property sellers in {city}, South Carolina, to consider selling their real estate. The blog should be titled: {title}. The content should offer a compelling analysis of why now is the right time to sell in {city}, highlighting recent trends and the current demand in the real estate market. It should discuss the benefits of selling in today's market and provide actionable insights for sellers to maximize their returns. Integrate a {style} style in the writing, combining analytical depth with narrative engagement and practical selling tips. Ensure the blog is well-structured with clear subheadings, engaging introductions to each section, and a conclusive summary that empowers sellers with the confidence to act."
        
        content_completion = self.client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates real estate blog posts."},
                {"role": "user", "content": content_prompt}
            ],
            max_tokens=4096,
            stop=None,
            temperature=0.7
        )
        content = content_completion.choices[0].message.content
        return content

    def generate_title(self, city, style):
        title_prompt = f"Generate a unique and original real estate blog post title for the city of {city}, SC. The title should reflect the {style} style."
        
        title_completion = self.client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[    
                {"role": "system", "content": "You are a helpful assistant that generates real estate blog titles."},
                {"role": "user", "content": title_prompt}
                ],
            max_tokens=250,
            stop=None,
            temperature=0.7
        )
        title = title_completion.choices[0].message.content
        return title

    def generate_metadata(self, title):
        metadata_prompt = f"Write a concise and compelling metadata description for a blog post titled: {title}."
        metadata_completion = self.client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[    
            {"role": "system", "content": "You are a helpful assistant that generates real estate blog meta data."},
            {"role": "user", "content": metadata_prompt}
            ],
            max_tokens=250,
            stop=None,
            temperature=0.7
        )
        metadata = metadata_completion.choices[0].message.content
        return metadata

    def generate_image(self, prompt):
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url

    def get_past_articles(self, csv_file):
        past_articles = []
        if os.path.exists(csv_file):
            with open(csv_file, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    past_articles.append(row[0])
        return past_articles

    def save_blog_post(self, title, content, metadata, image_url, csv_directory, csv_file):
        # Generate the folder name based on the current date and blog title
        current_date = datetime.now().strftime("%Y_%m_%d")
        folder_name = f"{current_date}_{title.replace(' ', '_')}"
        folder_path = os.path.join(csv_directory, folder_name)
        
        # Create the folder
        os.makedirs(folder_path, exist_ok=True)
        
        # Save the blog post content
        with open(os.path.join(folder_path, "blog_post.txt"), "w") as file:
            file.write(content)
        
        # Save the metadata description
        with open(os.path.join(folder_path, "metadata.txt"), "w") as file:
            file.write(metadata)
        
        # Save the image
        image_filename = os.path.join(folder_path, "main_image.jpg")
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_filename, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
        
        # Update the CSV file with the new blog post
        with open(csv_file, "a") as file:
            writer = csv.writer(file)
            writer.writerow([title])

    def read_city_names(self, filename):
        cities = []
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)  # Using DictReader to handle headers
            for row in reader:
                cities.append(row['City'])  # Accessing city names using the 'City' header
        return cities
    
    def csv_dir_setup(self, csv_directory_path, csv_file_name):
        # Set up the directory for storing the CSV file and blog posts
        csv_directory = csv_directory_path
        csv_file = os.path.join(csv_directory, csv_file_name)

        # Create the directory if it doesn't exist
        os.makedirs(csv_directory, exist_ok=True)
        return csv_directory, csv_file

    def generate_search_term(self, blog_content):
        
        try:
            # Generate a prompt to summarize the blog content into a search term
            prompt = f"Summarize the following blog content into a concise Google search term that is broad enough to generate multiple search results but specific to the city that it is centered on. The city will always be in South Carolina:\n{blog_content}"

            content_completion = self.client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates real estate blog posts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            stop=None,
            temperature=0.7
            )
            content = content_completion.choices[0].message.content.strip('\'"')
            return content
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

class GoogleSearch:
    def __init__(self):
        
        self.api_key = os.getenv("GOOGLE_API_KEY") 
        self.search_engine_id = '700002bb09d6d43a6'

    def google_search(self, query):
    # Strip leading and trailing single and double quotation marks
        cleaned_query = query.strip('\'"')
        
        # Construct the URL with the cleaned query
        url = f"https://www.googleapis.com/customsearch/v1?key={self.api_key}&cx={self.search_engine_id}&q={cleaned_query}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            search_results = []
            for item in data.get("items", []):
                title = item["title"]
                link = item["link"]
                search_results.append({"title": title, "url": link})

                if len(search_results) == 10:
                    break

            return search_results
        except requests.exceptions.RequestException as e:
            print("An error occurred while making the request:", e)
        except Exception as e:
            print("An error occurred:", e)






