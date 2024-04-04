# MetricBeat Processing

This is a Graylog content pack for parsing data from Metricbeat.

## What's Inside

* `Metricbeat` pipeline
    * 4 stages with 21 rules
* `Metricbeat Fix` lookup table
* `Metricbeat Data` stream

### Metricbeat Data stream

This stream looks for messages with a `beats_type` field with a value of "metricbeat". It removes messages from the default stream and stores data to the default index.

### Metricbeat Pipeline

The pipeline pulls messages from the Metricbeat stream.

**Stage 20**

The thing about Metricbeat is that most of the interesting data is presented as running totals for the day rather than discrete amounts for the reporting period. So instead of 10 bytes in then 20 bytes in then 10 bytes in, you see 10 bytes in then 30 bytes in then 40 bytes in.

The rules in this stage use the `Metricbeat Fix` lookup table to break down the accumulator values into deltas so you can get  better look at exactly how much is going on during particular time slices.

**Stage 25**

The problem with Stage 20 is that it can occasionally produce negative values. This stage exists mostly to zero out negative values.

**Stage 30**

This stage just converts bytes to MB

**Stage 40**

This stage renames some fields, reformats some values, and drops some Metricbeat fields to save on storage. It is far from complete.

## Setup

### Running Graylog 

This content pack requires Graylog 5.2.5 or later.

There's a `docker-compose.yml` file around here somewhere that can be used to spin up a Graylog instance along with its dependencies (MongoDB and OpenSearch). It was built for running Graylog on a Raspberry Pi 4 with 8GB of RAM, so you don't need a super powerful machine. If you *are* running with a more powerful machine, you might want to adjust the amount of memory allocated to OpenSearch (50% of total available is the general recommendation). 

One caveat about running with this Docker setup is that when you shut down your containers, you'll lose all your data and configuration. So it's a great way to try Graylog but not the best for long-term usage.

### Installing the Content Pack

Once you've got Graylog running, log in and navigate to System -> Content Packs. Hit the `Upload` button in the upper right corner and upload this content pack JSON file.

When you return to the Content Packs list page, you should see the `Metricbeat Processing` pack at the end of the list. Just click on the `Install` button over on the right hand side and it will install everything.

### Getting logs from Metricbeat

Metricbeat is fairly easy to install and the Graylog documentation has some good info on setting up a Beats input. In your Metricbeat config file, you'll need to delete the section for Elastic output and configure the Logstash output to send data to your Graylog host.
