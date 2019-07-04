import rethinkdb as r

r.connect('localhost', 28015).repl()

r.table('waitingTweets').filter(r.row['created_at'].to_epoch_time() <= (r.now() - r.epoch_time(172800)).run()).delete().run()
