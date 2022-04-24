# A scalable, commodity data center network architecture Summary

[A scalable, commodity data center network architecture](https://dl.acm.org/doi/10.1145/1402946.1402967)

[pdf](http://ccr.sigcomm.org/online/files/p63-alfares.pdf)

## Overview

By connecting half of the ports of commodity network switches to the hosts, and half of the ports to aggregation switches,
this paper presents a solution to datacenter topology where oversubscription ratio should ideally be 1 with minimized equipment cost.

The new topology comes with the complexity of routing, which is taken advantage by means of a two level prefix+suffix routing table.
The routing algorithm is implemented using special hardware TCAM.

* TCAM can look up memory using don't care bits

Main contribution is huge cost reduction (commodity device), fault tolerance (multi-path), scaling (not limited by equipment, as hierarchal topology does),
bisection bandwidth increase by using Clos.

## Background

Datacenter has unique traffic patterns. There are tens of thousands of hosts to be connected and each is expected to almost fully utilize
the bandwidth to each other. Oversubscription ratio is defined as the ratio of the aggregate bandwidth of all hosts when all hosts are
communicating at the same time, over the total bisection bandwidth of the whole topology.

* 1:1 oversubscription means that all hosts potentially can talk to any other hosts at full bandwidth of the interface
* oversubscription exists to lower the cost

One straightforward solution is to use more bandwidth at uplink ports.

* (side note: the actual topology used by ISP because the very low probability that every user will use full bandwidth at the same time)
* expensive
* not solving the root problem

(Another solution is InfiniBand, but it's using special protocol and is very expensive)

There are two main driving factors for datacenter topology

* cheap
* fast

## Fat Tree

Reapplying a [design](https://ieeexplore.ieee.org/document/6312192) by [Charles Clos](https://ieeexplore.ieee.org/document/6770468) from 50 years ago.

![figure 3](https://packetpushers.net/wp-content/uploads/2018/11/Scalable-DCN-Topology-Al-Fares-1024x444.png)

As shown in the figure 3 from the paper, there are three layers of switches (or router, or switch with routing functionality. it's just a term)

1. core ($(k/2)^2$ switches)
2. aggregation ($k/2$ switches)
3. edge ($k/2$ switches)

There are $k$ pods (sub-networks). The switches on the edge layer has $k/2$ connections to hosts, $k/2$ connection to switches in aggregation layer.
Similar for the aggregation layer. And each switch in the core layer has one connection to each pod. $k^3/4$ hosts are supported for such a
fat tree using $k$-port switches. $k=4$ in the figure

There are $(k/2)^2$ paths for hosts in different pods.

* new problem: lots of wires (not mentioned in the paper)
  * problem of bandwidth vs cost now becomes IT adminstration
  * so many fibers in datacenter physically, really hard to find and replace broken one. relies on reliability of the hardware
* new problem: how to route

### Addressing

See paper section 3.2.

* pod switch: $10.pod.switch.1$ (aggregation + edge. switch is left-to-right, bottom-to-top)
* core switch: $10.k.j.i$ (recall there are $(k/2)^2$ core switches)
* host: $10.pod.switch.ID$ (from the switch it connects to)

### Two Level Routing

Figure 4 in the paper gives an example of routing table of a switch in aggregation layer.

The first level is the prefix of the IP range within pod

* $10.MyPod.EdgeSwitch1.0/24 -> port0$ means all hosts connected to $EdgeSwitch1$ using $port0$

The second level is the suffix of all other IPs beyond this pod

* prefix will be mapped before suffix, based on the nature of TCAM
* the second level is simply load balancing the routing paths using ID
* $0.0.0.2/8 -> port2$ means load balancing all traffic to hosts with ID 2 in other networks using paths on port2

The routing table of edge layer switches only has the second level (the suffix) as directly connected hosts are switched.

The routing table of core layer switches is one-level straightforward mapping of $10.x.0.0/16$ to pods.

This simple load balancing design works well when flows among individual hosts are roughly similar in size.
It works well in practice.

## Discussion

The real datacenter adopt and modify this topology. The 1:1 oversubscription ratio may not be necessary in real life, and other issues will arise (manageability complexity due to number of links).

There are some centralized flow control and fault tolerance mentioned in the paper, but they are less important.

The real impact: 37M dollars design reduced to 8.64M dollars connecting 27,648 hosts.
