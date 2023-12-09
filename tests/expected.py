#
# configA expected results
#
configA_dict = {
    "no ip domain lookup": {},
    "interface FastEthernet0/0": {"no shutdown": {}},
    "interface FastEthernet0/0.10": {
        "description LAN": {},
        "encapsulation dot1Q 10": {},
        "ip address 192.168.1.254 255.255.255.0": {},
    },
    "router bgp 64512": {
        "neighbor 172.16.0.1 remote-as 100": {},
        "address-family ipv4": {
            "neighbor 172.16.0.1 activate": {},
            "neighbor 172.16.0.1 allowas-in 1": {},
            "neighbor 172.16.0.1 prefix-list IN in": {},
            "neighbor 172.16.0.1 prefix-list OUT out": {},
            "network 192.168.1.0 mask 255.255.255.0": {},
        },
    },
}
configA_str = """no ip domain lookup
interface FastEthernet0/0
 no shutdown
interface FastEthernet0/0.10
 description LAN
 encapsulation dot1Q 10
 ip address 192.168.1.254 255.255.255.0
router bgp 64512
 neighbor 172.16.0.1 remote-as 100
 address-family ipv4
  neighbor 172.16.0.1 activate
  neighbor 172.16.0.1 allowas-in 1
  neighbor 172.16.0.1 prefix-list IN in
  neighbor 172.16.0.1 prefix-list OUT out
  network 192.168.1.0 mask 255.255.255.0"""

#
# configB expected results
#
configB_dict = {
    "hostname R1": {},
    "interface FastEthernet0/0": {
        "description LAN": {},
        "no ip address": {},
        "shutdown": {},
        "duplex auto": {},
        "speed auto": {},
    },
    "router bgp 64512": {
        "neighbor 172.16.0.1 remote-as 100": {},
        "address-family ipv4": {
            "neighbor 172.16.0.1 activate": {},
            "neighbor 172.16.0.1 prefix-list IN in": {},
            "neighbor 172.16.0.1 prefix-list OUT out": {},
        },
    },
    "ip prefix-list IN seq 5 permit 192.168.2.0/24": {},
    "ip prefix-list OUT seq 5 permit 192.168.1.0/24": {},
}
configB_str = """hostname R1
interface FastEthernet0/0
 description LAN
 no ip address
 shutdown
 duplex auto
 speed auto
router bgp 64512
 neighbor 172.16.0.1 remote-as 100
 address-family ipv4
  neighbor 172.16.0.1 activate
  neighbor 172.16.0.1 prefix-list IN in
  neighbor 172.16.0.1 prefix-list OUT out
ip prefix-list IN seq 5 permit 192.168.2.0/24
ip prefix-list OUT seq 5 permit 192.168.1.0/24"""

#
# diffonly expected results
#
diffonly_dict = {
    "+no ip domain lookup": {},
    "interface FastEthernet0/0": {"+no shutdown": {}},
    "+interface FastEthernet0/0.10": {
        "description LAN": {},
        "encapsulation dot1Q 10": {},
        "ip address 192.168.1.254 255.255.255.0": {},
    },
    "router bgp 64512": {
        "address-family ipv4": {
            "+neighbor 172.16.0.1 allowas-in 1": {},
            "+network 192.168.1.0 mask 255.255.255.0": {},
        }
    },
}
diffonly_str = """+no ip domain lookup
 interface FastEthernet0/0
+ no shutdown
+interface FastEthernet0/0.10
+ description LAN
+ encapsulation dot1Q 10
+ ip address 192.168.1.254 255.255.255.0
 router bgp 64512
  address-family ipv4
+  neighbor 172.16.0.1 allowas-in 1
+  network 192.168.1.0 mask 255.255.255.0"""
diffonly_str_colored = """[32m+no ip domain lookup[m
 interface FastEthernet0/0
[32m+ no shutdown[m
[32m+interface FastEthernet0/0.10[m
[32m+ description LAN[m
[32m+ encapsulation dot1Q 10[m
[32m+ ip address 192.168.1.254 255.255.255.0[m
 router bgp 64512
  address-family ipv4
[32m+  neighbor 172.16.0.1 allowas-in 1[m
[32m+  network 192.168.1.0 mask 255.255.255.0[m"""

#
# diffmerge expected results
#
diffmerge_dict = {
    "hostname R1": {},
    "interface FastEthernet0/0": {
        "description LAN": {},
        "no ip address": {},
        "shutdown": {},
        "duplex auto": {},
        "speed auto": {},
        "+no shutdown": {},
    },
    "router bgp 64512": {
        "neighbor 172.16.0.1 remote-as 100": {},
        "address-family ipv4": {
            "neighbor 172.16.0.1 activate": {},
            "neighbor 172.16.0.1 prefix-list IN in": {},
            "neighbor 172.16.0.1 prefix-list OUT out": {},
            "+neighbor 172.16.0.1 allowas-in 1": {},
            "+network 192.168.1.0 mask 255.255.255.0": {},
        },
    },
    "ip prefix-list IN seq 5 permit 192.168.2.0/24": {},
    "ip prefix-list OUT seq 5 permit 192.168.1.0/24": {},
    "+no ip domain lookup": {},
    "+interface FastEthernet0/0.10": {
        "description LAN": {},
        "encapsulation dot1Q 10": {},
        "ip address 192.168.1.254 255.255.255.0": {},
    },
}
diffmerge_str = """ hostname R1
 interface FastEthernet0/0
  description LAN
  no ip address
  shutdown
  duplex auto
  speed auto
+ no shutdown
 router bgp 64512
  neighbor 172.16.0.1 remote-as 100
  address-family ipv4
   neighbor 172.16.0.1 activate
   neighbor 172.16.0.1 prefix-list IN in
   neighbor 172.16.0.1 prefix-list OUT out
+  neighbor 172.16.0.1 allowas-in 1
+  network 192.168.1.0 mask 255.255.255.0
 ip prefix-list IN seq 5 permit 192.168.2.0/24
 ip prefix-list OUT seq 5 permit 192.168.1.0/24
+no ip domain lookup
+interface FastEthernet0/0.10
+ description LAN
+ encapsulation dot1Q 10
+ ip address 192.168.1.254 255.255.255.0"""
diffmerge_str_colored = """ hostname R1
 interface FastEthernet0/0
  description LAN
  no ip address
  shutdown
  duplex auto
  speed auto
[32m+ no shutdown[m
 router bgp 64512
  neighbor 172.16.0.1 remote-as 100
  address-family ipv4
   neighbor 172.16.0.1 activate
   neighbor 172.16.0.1 prefix-list IN in
   neighbor 172.16.0.1 prefix-list OUT out
[32m+  neighbor 172.16.0.1 allowas-in 1[m
[32m+  network 192.168.1.0 mask 255.255.255.0[m
 ip prefix-list IN seq 5 permit 192.168.2.0/24
 ip prefix-list OUT seq 5 permit 192.168.1.0/24
[32m+no ip domain lookup[m
[32m+interface FastEthernet0/0.10[m
[32m+ description LAN[m
[32m+ encapsulation dot1Q 10[m
[32m+ ip address 192.168.1.254 255.255.255.0[m"""
