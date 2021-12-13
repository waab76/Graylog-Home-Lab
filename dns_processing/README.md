## What am I skipping?

I'm not going to get into the details of installing Pi-hole.  You can find that info [here](https://pi-hole.net/).  I talked about getting the logs from Pi-hole into Graylog in my [first howto post](https://www.reddit.com/r/graylog/comments/penmnx/raspberry_pi_4_home_graylog_setup).

Also, if you look at the pipeline rules for my DNS parsing pipeline, you'll see that I have lookup tables for hostname and friendly hostname values.  These use a MongoDB data adapter and get populated in my DHCP processing pipeline.

## Setting up GeoIP lookups

To get started on the GeoIP stuff, I recommend you go have a look at Nick's post over on the [official Graylog blog](https://www.graylog.org/post/how-to-set-up-graylog-geoip-configuration).  It gives a pretty good overview of the subject.  As mentioned in Nick's blog, I decided to use the MaxMind GeoLite2 city and ASN databases.

Once I had the MMDB files downloaded, I realized I needed to put them in a location where Graylog (running in Docker) would be able to see them.  I finally settled on adding a [new bind volume](https://github.com/waab76/Graylog-Home-Lab/blob/main/docker-compose.yml#L87-L89) in my docker-config.yml.  So I put the MMDB files in `/mnt/graylog/data` and when I set up the data adapter in Graylog, I told it the files were in `/usr/share/graylog/data/geo/`.

## DNS Processing

The first thing I did was set up a new Index Set and Stream for my Pi-hole logs.  For the stream rule, I'm using `application_name must match exactly dnsmasq`.  With all of my Pi-hole logs going into a stream, I now have something to attach a pipeline to.

The [first stage](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/Stage_0.txt) of the pipeline simply changes the `source` value on the messages.  The box Pi-hole is running on is called "plex" but I want these logs to be identifiable at a glance as coming from Pi-hole.

The next stage has five rules, one for each of the 5 different types of logs Pi-hole sends: [Query](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/Stage_10_query.txt), [Cached](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/Stage_10_cached.txt), [Forwarded](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/Stage_10_forwarded.txt), [Blocked](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/Stage_10_blocked.txt), and [Reply](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/Stage_10_reply.txt).  One of the frustrations I had with the DNS logs was that the host requesting the DNS lookup only gets mentioned in the Query log.  To address this, I added a new MongoDB-backed lookup table.  On each query log, I add an entry to this lookup table using the dns query as the key and the IP of the requesting machine as the value.  In the other 4 rules, I do a lookup on this table (because they include the dns query) to get back the identity of the host that the response is going back to.

In the [final stage](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/Stage_50_geo.txt), I do the GeoIP lookup and add the data to the message.  Getting the city and country out of the lookup response was easy enough, but the state is weirdly nested, so I had to get [kind of creative](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/Stage_50_geo.txt#L12) to get that.

## Dashboarding

Once all the data is flowing and the GeoIP enrichment is working, it's time for the fun part: setting up a [dashboard](https://github.com/waab76/Graylog-Home-Lab/blob/main/dns_processing/DNS%20dashboard.png). Since one of the selling points of Pi-hole is that it can block nasty sites (ads, trackers, malware, etc), I wanted to know how many queries were being made and how many queries were being blocked.  For that, I used a couple of Single Number aggregation widgets.  I also threw in a Data Table aggregation widget to get counts for the most-queried-for domains.  But the real star of the show is the World Map widget.  I'm using my `destination_geo_coordinates` field for the rollup column (with the limit bumped up to 500) and dropping in a count for the metric.

Thanks to my hostname/friendly hostname lookup tables, I'm also able to do a breakout tab just for our IoT devices (Kasa plugs and bulbs).  This dashboard is using most of the same widgets with the query changed to `source_friendly_hostname:("Kasa Smart Wifi Plug Mini", "Kasa Smart Wifi Plug", "Kasa Smart Wi-Fi Plug Mini", "Kasa Smart Wifi Bulb", "Kasa Smart Light Bulb")`.  It could probably be cleaned up a bit, but it's a pretty good start.
