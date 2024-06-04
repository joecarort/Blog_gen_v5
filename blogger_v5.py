# url generation based on blog content was added in this variation of the blogger tool. 
# three method and a class was add to accomplish this. 

from tools.blog_tools import BlogTools, GoogleSearch
import os
import random

# Ensure to adjust paths and other specifics as needed
model_version = "gpt-4o"
blog_tools = BlogTools(model_version)
google_search = GoogleSearch()

# Setup and read initial data as before
csv_directory_path = "/Users/joeortiz/Documents/ai_system_models/blog_generator/blogs/"
csv_file_name = "blog_history.csv"
city_filename = '/Users/joeortiz/Documents/ai_system_models/blog_generator/data/city_names_weighted.csv'
cities = blog_tools.read_city_names(city_filename)
blog_tools.csv_dir_setup(csv_directory_path=csv_directory_path, csv_file_name=csv_file_name)

selected_cities = random.sample(cities, 7) if len(cities) >= 7 else random.choices(cities, k=7)
styles = [
    'How to guide', 
    'Top 10', 
    'What to avoid', 
    'What they don\'t want you to know', 
    '5 reasons why', 
    'Insider secrets', 
    'Definitive guide',
    'Rent to own',
    'Expert Interview',
    'Seasonal Tips',
    'Renting vs Owning',
    'Step-by-Step Tutorial',
    'FAQ',
    'Rental Advice',
    'Seller Financing',
    'Beginners Guide',
    'Myth Busting'
]
num_blogs = 7

for i in range(num_blogs):
    print(f"Generating blog post {i+1}/{num_blogs}")
    city = selected_cities[i]
    style = random.choice(styles)
    title = blog_tools.generate_title(city, style)
    content = blog_tools.generate_blog_post(city, title, style)
    metadata = blog_tools.generate_metadata(title)
    image_prompt = f"Generate an image that represents the main concept of the blog post titled: {title}. Avoid using words in the image."
    image_url = blog_tools.generate_image(image_prompt)
    
    # New part: Search for links related to the title and append to content
    search_term = blog_tools.generate_search_term(content)
    search_results = google_search.google_search(search_term)
    print(search_results)
    links_formatted = blog_tools.format_search_results(search_results)
    content += links_formatted  # Append formatted links to the content

    blog_tools.save_blog_post(title, content, metadata, image_url, csv_directory_path, csv_file_name)
    print(f"Style: '{style}' Blog post '{title}' generated and saved.")

print("All blog posts generated and saved successfully.")
