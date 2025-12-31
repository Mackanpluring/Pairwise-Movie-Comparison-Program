import random
import math
import statistics
import csv


class Movie():
    def __init__(self, date, title, year, url, score=1000, times_rated=0, star_rating=0):
        self.date = date
        self.title = title
        self.year = year
        self.url = url
        self.score = score
        self.times_rated = times_rated
        self.star_rating = star_rating

    def get_date(self):
        return self.date

    def get_title(self):
        return self.title
    
    def get_year(self):
        return self.year
    
    def get_url(self):
        return self.url
    
    def set_url(self, url):
        self.url = url

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def get_times_rated(self):
        return self.times_rated
    
    def set_times_rated(self, times_rated):
        self.times_rated = times_rated

    def get_star_rating(self):
        return self.star_rating
    
    def set_star_rating(self, star_rating):
        self.star_rating = star_rating


class Movies():
    movielist = []
    identical_titles = []
    new_movie_list = []


def create_Movie_objects():
    with open("watched.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["Date"].strip()
            title = row["Name"].strip()
            year = row["Year"].strip()
            url = row["Letterboxd URI"].strip()
            movie = Movie(date=date, title=title, year=year, url=url)
            Movies.movielist.append(movie)


def find_identical_titles(movielist):
    for movie in movielist:
        title = movie.get_title()
        count = sum(1 for m in movielist if m.get_title() == title)
        if count > 1 and title not in Movies.identical_titles:
            Movies.identical_titles.append(title)


def save_progress(completed_comparisons):
    with open("progress.txt", "w", encoding="utf-8") as f:
        f.write(f"Completed comparisons|{completed_comparisons}\n") 
        for m in Movies.movielist:
            f.write(f"{m.get_date()}|{m.get_title()}|{m.get_year()}|{m.get_url()}|{m.get_score()}|{m.get_times_rated()}|{m.get_star_rating()}\n")
    print("Data sparad, avslutar programmet.")


def load_progress():
    completed_comparisons = 1
    try:
        with open("progress.txt", "r", encoding="utf-8") as f:
            Movies.movielist = []
            for line in f:
                parts = line.strip().split("|")
                if parts[0] == "Completed comparisons":
                    completed_comparisons = int(parts[1])
                else:
                    date, title, year, url, score, times_rated, star_rating = parts
                    movie = Movie(date=date, title=title, year=year, url=url, score=float(score), times_rated=int(times_rated), star_rating=float(star_rating))
                    Movies.movielist.append(movie)
        return completed_comparisons
    except FileNotFoundError:
        print("Ingen sparad data hittades, startar från början.")
        create_Movie_objects()
        return 1  


def pair_movies(movielist):
    min_ratings = min(m.get_times_rated() for m in movielist)
    
    rate_this_round = [m for m in movielist if m.get_times_rated() == min_ratings]
    movie1 = random.choice(rate_this_round)

    potential_partners = [m for m in movielist if m != movie1]
    potential_partners.sort(key=lambda m: abs(m.get_score() - movie1.get_score()))
    
    pool_size = min(10, len(potential_partners))
    movie2 = random.choice(potential_partners[:pool_size])

    return movie1, movie2


def compare_movies(completed_comparisons):
    movie1, movie2 = pair_movies(Movies.movielist)
    es1 = 1 / (1 + 10 ** ((movie2.get_score() - movie1.get_score()) / 400)) #Expected score for movie 1
    es2 = 1 / (1 + 10 ** ((movie1.get_score() - movie2.get_score()) / 400)) #Expected score for movie 2
    
    def get_k_factor(movie):
        if movie.get_times_rated() < 4:
            return 64
        elif movie.get_times_rated() < 9:
            return 32
        else:
            return 16
        
    def determine_display_title(movie):
        if movie.get_title() in Movies.identical_titles:
            return f"{movie.get_title()} ({movie.get_year()})"
        else:
            return movie.get_title()

    k1 = get_k_factor(movie1)
    k2 = get_k_factor(movie2)

    print(f"\nJämförelse: {completed_comparisons}/{len(Movies.movielist) * 6} | {completed_comparisons / (len(Movies.movielist) * 6) * 100:.2f}% avklarad")
    print("(!) Kom ihåg att jämförelsen utgår från vilken av dessa två du helst skulle se just nu.")
    print("(!) Om du minns en film bättre än den andra, låt den vinna.")
    print(f"\nVilken film är bättre?")
    print(f"1. {determine_display_title(movie1)}")
    print(f"2. {determine_display_title(movie2)}")
    while True:
        choice = input(f"1/2, q för att spara och avsluta: ")
        if choice == "1":
            ns1 = movie1.get_score() + k1 * (1 - es1) #New score for movie 1
            ns2 = movie2.get_score() + k2 * (0 - es2) #New score for movie 2
            movie1.set_score(ns1)
            movie2.set_score(ns2)
            movie1.set_times_rated(movie1.get_times_rated() + 1)
            movie2.set_times_rated(movie2.get_times_rated() + 1)
            break
        elif choice == "2":
            ns1 = movie1.get_score() + k1 * (0 - es1) #New score for movie 1
            ns2 = movie2.get_score() + k2 * (1 - es2) #New score for movie 2
            movie1.set_score(ns1)
            movie2.set_score(ns2)
            movie1.set_times_rated(movie1.get_times_rated() + 1)
            movie2.set_times_rated(movie2.get_times_rated() + 1)
            break
        elif choice.lower() == "q":
            save_progress(completed_comparisons)
            exit()
        else:
            print("Ogiltigt val, försök igen.")


def program():
    completed_comparisons = 1

    while True:
        menu_choice = input("Vill du ladda data? (j/n): ").lower()
        if menu_choice == "j":
            completed_comparisons = load_progress()
            break
        elif menu_choice == "n":
            create_Movie_objects()
            break
        else:
            print("Ogiltigt val, försök igen.")

    find_identical_titles(Movies.movielist)

    number_of_comparisons = round(math.log2(len(Movies.movielist)) + 3)

    while min(m.get_times_rated() for m in Movies.movielist) < number_of_comparisons:
        compare_movies(completed_comparisons)
        completed_comparisons += 1

    convert_score_to_star_rating(Movies.movielist)

    create_csv_file()
    print("Alla jämförelser klara, resultaten har sparats i 'import_file.csv'.")
    print("Programmet avslutas.")
    exit()


def convert_score_to_star_rating(movielist):
    movielist.sort(key=lambda m: m.get_score())
    mean_star_rating = 2.75
    standard_deviation = 1

    N = len(movielist)

    for i in range(len(movielist)):
        rank = i + 1
        percentile = rank / (N + 1)
        z = statistics.NormalDist().inv_cdf(percentile)
        star_rating = mean_star_rating + standard_deviation * z
        star_rating = max(0.5, min(5, star_rating))
        star_rating = round(star_rating * 2) / 2
        movielist[i].set_star_rating(star_rating)


def create_csv_file():
    with open("import_file.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["WatchedDate", "Name", "Year", "Letterboxd URI", "Rating"])
        for m in Movies.movielist:
            writer.writerow([m.get_date(), m.get_title(), m.get_year(), m.get_url(), m.get_star_rating()])
        

if __name__ == "__main__":
    program()