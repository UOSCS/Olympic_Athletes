# Olympic_Athletes

## Index
1. [About the repository](#About-the-repository)
2. [Description of the data scraping process](#Description-of-the-data-scraping-process)
3. [Project](#Project)

## About the repository
This repository consists of a Python file that retrieves all athletes who participated in the Olympics from [olympedia.org](http://www.olympedia.org/) and a CSV file that stores the data collected by the Python file.

## Description of the data scraping process
1. First of all, we need to call up all the countries that have participated in the modern Olympics.
![countries](https://drive.google.com/uc?export=view&id=123lYQUfNfYIe35YMWWqMj3Is9D8Bz4zh)


2. Next, we create a Python dictionary data structure to know the host city from the host year and season later. The key of this dictionary is the concatenated Olympic year and season (e.g., 2018Winter), and the value is the host city.
![Olympic Games Summer](https://drive.google.com/uc?export=view&id=1nA5n0jaHgL7GYf1Y2TvZYVunFXWn0Z8Y)
![Olympic Games Winter](https://drive.google.com/uc?export=view&id=1lnHeAzstGe38yjvoWH17jIzYQymmrOZu)

3. Now we are traversing by country and importing athlete information.
    1. Get all 'href's of 'a' tag in the last column(Results) of 'Olympic Games' table of 'Participations by edition'.
    ![Olympic Games Winter](https://drive.google.com/uc?export=view&id=1hxLoibKc9HgsivyN4cKcjbilJsxkLCN8)
    2. If you click ‘Results’ to access it, you will see the athletes who participated in the relevant Olympics. Duplicate athlete names will appear if an athlete has competed in multiple events.
    ![Olympic Games Winter](https://drive.google.com/uc?export=view&id=1ETDZrNl2-Aie9RKuhLqCgmC0P3SzEL0P)
    3. Now we create a non-duplicate 'athlete_id' set by looking at all records(all 'Results's) that a country has competed in past Olympics.
    4. Next, we start importing athlete information in earnest.
        1. Create an 'athelte_url' list from the 'athlete_id' set to access each athlete page.
        ![Olympic Games Winter](https://drive.google.com/uc?export=view&id=15wyO4z4s7t1-kv-8JqrdlkCcfQs-pkrj)
        2. Access the player page, first collect the athlete's biographical information.
        ![Olympic Games Winter](https://drive.google.com/uc?export=view&id=1JxoaZKKk63l0xeA0lXn53eORABka-CG3)
        3. Then, we import the games, sport, and detailed event that the athlete participated in from the 'Results' table.
        4. Finally, we get the medal information from the 'Results' table.
        ![Olympic Games Winter](https://drive.google.com/uc?export=view&id=1lWXSX2Mqol9jwMa8rV-wznS1XS93wBQp)
        5. Set the athlete information from the previously imported information and write it to the CSV file.

## Project
We are creating [Kolympic](https://kolympic.com/), a website that visualizes Republic of Korea's Olympic records with the Olympic data collected in the above method and implements various high-level user scenarios related to the Olympics.