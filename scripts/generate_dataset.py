import json
import os
import random

def generate_mock_photos():
    photos = []
    
    cities = ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Chennai"]
    events = ["college farewell", "birthday party", "wedding", "diwali", "new year", "vacation"]
    people_lists = [["sister"], ["brother", "mom"], ["friends"], ["colleagues"], ["mom", "dad"]]
    objects_lists = [["cake"], ["car"], ["certificate"], ["gift"], ["dog"], []]
    
    # Generate 45 photos
    for i in range(1, 46):
        year = random.choice([2020, 2021, 2022, 2023, 2024])
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        city = random.choice(cities)
        event = random.choice(events)
        people = random.choice(people_lists)
        objects = random.choice(objects_lists)
        
        photo_id = f"photo_{i:03d}"
        
        visual_desc = f"A photo taken at {event} in {year} featuring {', '.join(people)}"
        if objects:
            visual_desc += f" with a {objects[0]}"
            
        photo = {
            "id": photo_id,
            "image_url": f"https://placehold.co/600x400?text={photo_id}",
            "date": f"{year}-{month:02d}-{day:02d}",
            "year": year,
            "location": city,
            "people": people,
            "event": [event],
            "objects": objects,
            "visual_description": visual_desc,
            "text": f"{event} {year}",
            "embedding": []
        }
        
        # Manually ensure our benchmark task target exists
        if i == 21:
            photo = {
                "id": "photo_021",
                "image_url": "https://placehold.co/600x400?text=photo_021_farewell",
                "date": "2022-11-18",
                "year": 2022,
                "location": "Hyderabad",
                "people": ["sister"],
                "event": ["college farewell"],
                "objects": ["certificate"],
                "visual_description": "A person standing with her sister at a college farewell",
                "text": "Farewell 2022",
                "embedding": []
            }
            
        photos.append(photo)
        
    return photos

if __name__ == "__main__":
    photos = generate_mock_photos()
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "photos.json")
    with open(output_path, "w") as f:
        json.dump(photos, f, indent=2)
    print(f"Generated {len(photos)} mock photos at {output_path}")
