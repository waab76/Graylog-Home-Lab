# Veilid Log Management

This is a Graylog content pack for parsing and visualization of Veilid debug and error logs.

It doesn't cover every debug/error log, but it does cover all of the logs that I saw in 24 hours of collecting Veilid debug and error logs. I will try to keep it up to date as I see more logs flow into my Graylog instance.

This content pack is built to be easy to use for Veilid folks who might not be familiar with Graylog. There are definitely some spots where things are done inefficiently for the sake of simplicity. If you're a Graylog expert, you should be able to quickly adapt this content pack to your existing setup.

## What's Inside

* `Veilid Syslog` input
* `Veilid Processing` pipeline
  * 3 stages with (currently) 33 rules
* `Veilid` dashboard

### Veilid Syslog Input

Just a basic TCP Syslog input pre-configured to listen on port 12201 (which is the only port configured in the accompanying `docker-compose.yml`). 

### Veilid Processing Pipeline

The pipeline pulls messages from Graylog's `Default Stream`, which is where all incoming messages go by default so you don't have to do any extra configuration.

**Stage 0**

* The `Select Veilid Messages` rule matches on log messages where the syslog `application_name` is "veilid-server".
* The `Drop Non-Veilid Messages` rule doesn't match any messages because it includes "&& false" in the `when` clause. If you remove the "&& false" then it will drop all non-Veilid messages so your Graylog server neither processes nor stores them

**Stage 10**

* The `Parse Syslog Log Level [0-7]` rules just convert Syslog numeric log levels to their corresponding text values. This would be more efficient with a lookup table, but I'm trying to keep things simple
* The `Drop Syslog Facility Fields` rule drops the `facility` and `facility_num` fields from all messages

**Stage 20**

The rules in this stage parse various Veilid logs. All of the rules attempt to set `vendor_event_category` and `vendor_event_action` fields based on my best guess as to what the logs are saying about what's going on inside of Veilid. Some of the rules parse out additional fields (like `remote_ip`, `remote_port`, `veilid_key`, `veilid_subkey`, etc.) depending on what's in the logs.

If you want to add parsing rules for other log types that I haven't covered yet, you should add them to this stage.

## Setup

### Running Graylog 

This content pack requires Graylog 5.2.5 or later.

There's a `docker-compose.yml` file included that can be used to spin up a Graylog instance along with its dependencies (MongoDB and OpenSearch). It was built for running Graylog on a Raspberry Pi 4 with 8GB of RAM, so you don't need a super powerful machine. If you *are* running with a more powerful machine, you might want to adjust the amount of memory allocated to OpenSearch (50% of total available is the general recommendation). 

One caveat about running with this Docker setup is that when you shut down your containers, you'll lose all your data and configuration. So it's a great way to try Graylog but not the best for long-term usage.

### Installing the Content Pack

Once you've got Graylog running, log in and navigate to System -> Content Packs. Hit the `Upload` button in the upper right corner and upload this content pack JSON file.

When you return to the Content Packs list page, you should see the `Veilid` pack at the bottom of the list. Just click on the `Install` button over on the right hand side and it will install everything.

### Getting logs from Veilid

You can edit `/etc/veilid-server/veilid-server.conf` to ensure `system` logging is enabled and set the log level. You'll need to restart veilid-server if you make any changes.

You will need to update `/etc/rsyslog.conf` to forward syslog data from the host to your Graylog server.  You can add a block like this to the bottom of the file:

```
# Send Veilid logs to Graylog
*.* action(type="omfwd" target="YOUR_IP_OR_HOSTNAME_HERE" port="12201" protocol="tcp"
            action.resumeRetryCount="100" template="RSYSLOG_SyslogProtocol23Format"
            queue.type="linkedList" queue.size="10000")
```

You'll need to restart rsyslog after making the change.