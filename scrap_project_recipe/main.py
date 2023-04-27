import os


def main():
    # call scrapy crawl quotes
    os.system('scrapy crawl aldi -O data.json')#pour récupérer les données de lidl.
    #  exec script to save into elasticsearch
    # TODO
    pass


# program entry point
if __name__ == '__main__':
    main()
