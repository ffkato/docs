# Inside the Social Network’s (Datacenter) Network Summary

[Inside the Social Network's (Datacenter) Network](https://dl.acm.org/doi/10.1145/2785956.2787472)

[pdf](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p123.pdf)

## Overview

As claimed in the paper, it is "the first to report on production traffic in a datacenter network connecting hundreds
of thousands of 10-Gbps nodes". This paper was published in 2015. Datacenter may have changed a lot
and this paper primarily serves to help understand the history.

Figure 1 in the paper shows their topology at that time. It is very similar to Clos, but 1:1 oversubscription
ratio is discarded, and related services are deployed close to each other (each rack has dedicated role, servers are placed in clusters).

This paper presents the reality in the industry, which dramatically contrasts what comes out from the academic.
Mathematically optimal connectivity is unnecessary.

Details are omitted. In summary, they found various contrasting properties of the traffic, such as almost zero rack locality,
intra-cluster locality by placement, need for intra-datacenter communication by design, per-destination rate stability,
challenges and low benefit to identify heavy hitters. Table 1 has listed their major findings.
[summaries elsewhere](http://www.layer9.org/2015/08/session-31-paper-1-inside-social.html)

## Special Requirements and Challenges

The focused workflows in this paper:

* Web servers
* Cache leaders and followers
* Hadoop for offline analysis

Web servers are load balanced, and they access cache servers. Offline analysis is not involved in the "user path".

The main services provided by Facebook is HTTP traffic. And the workflows are also shaped by how the social network is
is connected. Facebook users are highly likely to spend most time accessing friends' photos/videos. The storage services
are designed with such patterns, also they are infrequent accesses to posts a long time ago.
Instant messaging (not discussed directly in the paper) has fundamentally different traffic patterns. Most importantly,
Facebook needs to analyze data to serve advertisements, which is critical to the business. This is also why they
talked about Hadoop a lot.

Oversubscription may be cost-effective for post retrieving services, and may be problematic for others. Building datacenter
costs money, and engineers have to design very specifically for specific workflows for the company.

* locality
* stability
* elephant flow and mice flow
* availability
* load balancing
* traffic patterns
* packet size
* bursts
* concurrent flow
* and many more ...

## Bare Metal Machines

While almost everyone else tries to use technologies like virtual machines to dynamically schedule jobs to "optimally" assign
related jobs together and utilize every computation resource to the limit, Facebook decides otherwise. And they must
have sufficient reasons to do so.

* when deploying, know exactly the traffic purpose
* a "small number of machines ... are dynamically repurposed"
* "to ease provisioning and management, racks typically contain only servers of the same role"
* ...

## Monitoring

Another challenge for datacenter at this scale is monitoring. It's impossible to log every single packet, redirect everything
to any single server to analyze.

The data in the paper was from

* 1:30000 sampling (Fbflow)
* complete port mirroring over short time periods

This is also a limitation of this paper.
