import os


def main():
    # call scrapy crawl quotes
    # os.system('scrapy crawl aldi -O data.json')  #pour récupérer les données de lidl.
    os.system('scrapy crawl aldi -O aldi.json')


# program entry point
if __name__ == '__main__':
    main()
