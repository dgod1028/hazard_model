from TvshowTweets.TVshowTweets import TVshowTweets

TV_SHOW = "TheGoodPlace"#"ThisIsUs"

if __name__ == "__main__":
    network = TVshowTweets()
    network.add_show(TV_SHOW)
    network.save()
