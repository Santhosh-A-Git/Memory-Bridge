const fs = require('fs');
const path = require('path');

function generateMockPhotos() {
    const photos = [];
    
    const cities = ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Chennai"];
    const events = ["college farewell", "birthday party", "wedding", "diwali", "new year", "vacation"];
    const peopleLists = [["sister"], ["brother", "mom"], ["friends"], ["colleagues"], ["mom", "dad"]];
    const objectsLists = [["cake"], ["car"], ["certificate"], ["gift"], ["dog"], []];
    
    for (let i = 1; i <= 45; i++) {
        const year = [2020, 2021, 2022, 2023, 2024][Math.floor(Math.random() * 5)];
        const month = Math.floor(Math.random() * 12) + 1;
        const day = Math.floor(Math.random() * 28) + 1;
        
        const city = cities[Math.floor(Math.random() * cities.length)];
        const event = events[Math.floor(Math.random() * events.length)];
        const people = peopleLists[Math.floor(Math.random() * peopleLists.length)];
        const objects = objectsLists[Math.floor(Math.random() * objectsLists.length)];
        
        const photoId = `photo_${i.toString().padStart(3, '0')}`;
        
        let visualDesc = `A photo taken at ${event} in ${year} featuring ${people.join(', ')}`;
        if (objects.length > 0) {
            visualDesc += ` with a ${objects[0]}`;
        }
            
        let photo = {
            id: photoId,
            image_url: `https://placehold.co/600x400?text=${photoId}`,
            date: `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`,
            year: year,
            location: city,
            people: people,
            event: [event],
            objects: objects,
            visual_description: visualDesc,
            text: `${event} ${year}`,
            embedding: []
        };
        
        if (i === 21) {
            photo = {
                id: "photo_021",
                image_url: "https://placehold.co/600x400?text=photo_021_farewell",
                date: "2022-11-18",
                year: 2022,
                location: "Hyderabad",
                people: ["sister"],
                event: ["college farewell"],
                objects: ["certificate"],
                visual_description: "A person standing with her sister at a college farewell",
                text: "Farewell 2022",
                embedding: []
            };
        }
            
        photos.push(photo);
    }
    return photos;
}

const photos = generateMockPhotos();
const outputPath = path.join(__dirname, '..', 'data', 'photos.json');
fs.writeFileSync(outputPath, JSON.stringify(photos, null, 2));
console.log(`Generated ${photos.length} mock photos at ${outputPath}`);
