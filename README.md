
# webmon

webmon is a tool to periodically detect and alert on website availability. A typical use for this would be to query multiple hosted services for availability.
webmon borrows code from my other project, [webcompare](https://github.com/evcsec/webcompare)

## Getting Started



### Prerequisites

Below are the main python libraries and imports currently used for the project. See webmon.py for full list.

```
- Requests
- Django
```

### Installing

The script is super simple to setup. Running for the first time, or without a config file present will prompt you to set up one or more hosts to scan, and the time interval between each scan.

An interactive prompt can be used to add hosts after-initial setup by using either of the below flags
```
webmon.py -a
```
*Or*
```
webmon.py —-addtargets
```

The current list of hosts can also be printed with either of the following
```
webmon.py -l
```
*Or*
```
webmon.py —-listtargets
```

A one-time scan can also be completed by using:
```
webmon.py -s
```

Keep in mind host URL’s are validated and thus need to be supplied in the full correct format, including the http:// or https:// prefix.

## Deployment & Alerts

By default the script will output a log file for external processing, but could be set up similarly to [webcompare](https://github.com/evcsec/webcompare) with an email system

## Authors

* **snags141**
