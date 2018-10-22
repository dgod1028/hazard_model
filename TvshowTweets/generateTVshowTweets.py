from TvshowTweets.TVshowTweets import TVshowTweets

TV_SHOW = "ThisIsUs"

if __name__ == "__main__":
    network = TVshowTweets()
    network.add_show(TV_SHOW)
    network.save()
