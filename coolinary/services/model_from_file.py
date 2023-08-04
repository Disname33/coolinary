from coolinary.models import City, Country


def city_to_db(file_path):
    cities_to_insert = []
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split('>')
            value = parts[0].split('"')[1]
            name = parts[1].split('<')[0]
            city = City(id=value, country_id=219, name=name)
            cities_to_insert.append(city)
            # print(f"name: {name}, value: {value}")
    City.objects.bulk_create(cities_to_insert)


def country_to_db(file_path):
    countries_to_insert = []
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split('>')
            name = parts[1].split('<')[0]
            value = parts[0].split('"')[1]
            country = Country(id=value, name=name)
            countries_to_insert.append(country)
            # print(f"name: {name}, value: {value}")
    Country.objects.bulk_create(countries_to_insert)


if __name__ == '__main__':
    # city_to_db('coolinary/services/city.txt')
    country_to_db('coolinary/services/country.txt')
