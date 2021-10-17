# Processing DHCP logs from my ASUS router

DHCP is the protocol used to assign network addresses to particular machines.  
In order for an IP address to be assigned to a particular host, [four UDP messages](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol#Operation) are exchanged.  When I turned up
the log level on my ASUS router to 6, I discovered that the DHCP messages were
now appearing in the log and I decided to try parsing them.

The four DHCP messages look something like this:

- DISCOVER: `DHCPDISCOVER(br0) 76:b8:07:27:ef:6f`
- OFFER: `DHCPOFFER(br0) 192.168.50.47 76:b8:07:27:ef:6f`
- REQUEST: `DHCPREQUEST(br0) 192.168.50.47 76:b8:07:27:ef:6f`
- ACKNOWLEDGE: `DHCPACK(br0) 192.168.50.47 76:b8:07:27:ef:6f Corgi`

## My DHCP processing pipeline

I broke my pipeline up into 2 stages.  Since I already have a basic pipeline attached
to the stream of data from the router that does some field remapping on Stage 0, I
started the DHCP pipeline with Stage 10.

In Stage 10, I'm basically checking to see if a particular message from the router is
a DHCP message.  If so, I parse out which DHCP message it is (`DISCOVER`, `OFFER`, `REQUEST`, or
`ACKNOWLEDGE`) and store that in the `dhcp_type` field.

In Stage 20, I have rules for handling each `dhcp_type`.  The rules use grok patterns
to parse out various fields (like `source_mac`, `source_hostname`, and `source_ip`).  

## Determining MAC vendor

You might note that in every rule that parses out `source_mac`, I'm calling a lookup
table to get the MAC vendor.  This relies on an HTTPJsonPath Data Adapter with
`http://api.macvendors.com/${key}` as the Lookup URL.

## Saving IP-Hostname Mappings

The DHCP ACK message contains both the hostname of the host requesting an IP and
the IP assigned to that host.  I've configured a Lookup Table (based on a MongoDB
Data Adapter) to store these IP-host mappings.  This allows me to add hostnames
to logs that only contain IP addresses.  

I also have a Lookup Table for "friendly hostnames" where I've manually mapped
hostnames for some devices to easier-to-read values.  You can see this being used
in the ACK rule as well.
