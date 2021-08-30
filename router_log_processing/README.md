# Processing ASUS RT-AC86U Logs

As mentioned on Reddit, the link between my home network and the internet is an
ASUS RT-AC86U router.  I've enabled the firewall feature and set it to log both
dropped and accepted packets.  In their raw form, the logs look something like
this:

`Aug 29 18:11:22 kernel: DROP IN=eth0 OUT= MAC=4d:eb:fa:88:f3:47:b4:8b:6c:24:a0:17:88:10 SRC=95.42.2.204 DST=66.77.88.257 LEN=131 TOS=0x00 PREC=0x00 TTL=120 ID=30883 PROTO=UDP SPT=17578 DPT=51413 LEN=111 MARK=0x8000000`

Graylog automatically parses out the timestamp and `kernel` as part of its standard syslog parsing.  The rest of the log line becomes the `message` field of the resulting Graylog message.

My pipeline for processing these messages currently has 4 stages:

* **Stage 0** - Verify that the logs are, indeed, from the router and rewrite the `source` field to be a little more user-friendly
* **Stage 10** - Parse the "dropped packet" message using a [Grok pattern](https://www.elastic.co/guide/en/logstash/current/plugins-filters-grok.html#_grok_basics) to extract fields like `source_ip`, `network_transport`, and `network_bytes`
* **Stage 20** - This is the stage that does the [GreyNoise](https://greynoise.io) lookup. It passes the `source_ip` value to the GreyNoise lookup table and then uses the data that comes back to further populate my Graylog message.
* **Stage 30** - For any message that didn't get good data from GreyNoise on Stage 20, I pass the `source_ip` to a [whois](https://www.whois.net/) lookup table to try and get some information like AS organization and a country code.

## Setting up the GreyNoise and whois lookups

A Graylog lookup consists of 3 parts:
* a data adapter
* a cache
* a lookup table

Basically, the data adapter knows how to talk to the data source (like GreyNoise or ICANN for whois).  The cache allows you to trade some memory for potentially faster lookups if you expect to see values repeated.  The lookup table combines the data adapter with the cache and is basically your entry point for lookups from pipelines.

To use the GreyNoise data adapter, you're going to need to go get a free API key.  No API key is needed for the whois data adapter.  Set up your adapters, set up a cache (or caches), and then create the lookup tables that wire everything together.

## Next steps

If I ever see any logs for allowed packets, I'll need to add a parsing rule to Stage 10.  As long as the new rule in Stage 10 parses out the `source_ip` field, then the rules in stages 20 and 30 will continue to do their jobs just like they always have.
