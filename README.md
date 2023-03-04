* [What is DiffPlus?](#what-is-diffplus)
  * [What for?](#what-for)
  * [Problem](#problem)
  * [Proposed solution](#proposed-solution)
* [HOWTO](#howto)
  * [Install](#install)
  * [Indented config to dict](#indented-config-to-dict)
  * [Sanitizing](#sanitizing)
  * [Incremental diff](#incremental-diff)
    * [Diff only](#diff-only)
    * [Merging](#merging)
    * [Colored diff](#colored-diff)
    * [Under the hood](#under-the-hood)
  * [Diff using a third-party module](#diff-using-a-third-party-module) (optional)
* [Does DiffPlus reinvent the wheel?](#does-diffplus-reinvent-the-wheel)

# What is DiffPlus?

A lightweight module to help in the comparison of config files. **In particular, it computes an incremental diff between two indented config files whilst respecting the scope of the indented blocks (aka contextual diff).**

The module leverages the *n*-ary tree data structure to achieve such a diff. Taking about a hundred lines of code, it only relies on Python builtins and has no extra dependencies.

## What for?

The whole point of DiffPlus is to compare config files **before running them in production.**

Basically, we'd like to merge `A` config file (the candidate config, partial or full) into another `B` config file (the running config). The next section states the problem and gives an insight of what we expect from the module.

## Problem

Say we have two indented configs:

<table>
 <thead>
  <tr>
   <th>Config A (to merge into B)</th>
   <th>Config B</th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td>

```
!
no ip domain lookup
!
interface FastEthernet0/0
 no shutdown
!
interface FastEthernet0/0.10
 description LAN
 encapsulation dot1Q 10
 ip address 192.168.1.254 255.255.255.0
!
router bgp 64512
 neighbor 172.16.0.1 remote-as 100
 !
 address-family ipv4
  neighbor 172.16.0.1 activate
  neighbor 172.16.0.1 allowas-in 1
  neighbor 172.16.0.1 prefix-list IN in
  neighbor 172.16.0.1 prefix-list OUT out
  network 192.168.1.0 mask 255.255.255.0
!
```
   </td>
   <td>

```
!
hostname R1
!
interface FastEthernet0/0
 description LAN
 no ip address
 shutdown
 duplex auto
 speed auto
!
router bgp 64512
 neighbor 172.16.0.1 remote-as 100
 !
 address-family ipv4
  neighbor 172.16.0.1 activate
  neighbor 172.16.0.1 prefix-list IN in
  neighbor 172.16.0.1 prefix-list OUT out
!
ip prefix-list IN seq 5 permit 192.168.2.0/24
ip prefix-list OUT seq 5 permit 192.168.1.0/24
!
```
   </td>
  </tr>
 </tbody>
</table>

*The example shows Cisco configs but it applies to any indented config (NOT necessarily network-related).*

**Some items of `A` are missing in `B`. How to find them?**

* We are only looking for new items to be added in `B` — it is called an **incremental diff**
* The comparison must respect the indented blocks scope — it is called a **contextual diff**

> A line-by-line diff will not help here since `A` is typically a partial config to merge into a full one being `B`.

We humans are able to compute that diff with ease because we visually identify blocks and items (though we make mistakes, sometimes). After some effort, we'd end up with the following result in mind:

```diff
# items of A to be added in B (to be computed by diffplus)

+no ip domain lookup
interface FastEthernet0/0
+ no shutdown
+interface FastEthernet0/0.10
+ description LAN
+ encapsulation dot1Q 10
+ ip address 192.168.1.254 255.255.255.0
router bgp 64512
 address-family ipv4
+  neighbor 172.16.0.1 allowas-in 1
+  network 192.168.1.0 mask 255.255.255.0
```

> As stated above, this is an incremental diff: **there are only additions (hence the module name),** no deletions.

As simple as it seems, such a diff is not so trivial for an algorithm.

## Proposed solution

1. Convert each config to an *n*-ary tree
2. Do a deep comparison of the *n*-ary trees

The *n*-ary tree data structure will help: to represent how nested the items are, to do the match between blocks.

Because we deal with config files, **each line is unique per indented block.** Therefore, no need for a list of nodes (allowing for duplicates). We can directly use raw nested dicts as *n*-ary trees, keys being the lines.

The deep comparison can then be achieved with either a dedicated third-party module or the lightweight [IncrementalDiff](#incremental-diff) helper embedded in this module.

# HOWTO

## Install

DiffPlus is available on [PyPI](https://pypi.org/project/diffplus):

```sh
pip install diffplus
```

## Indented config to dict

The `to_dict()` method converts an indented config to an *n*-ary tree:

```py
from diffplus import IndentedConfig
from json import dumps

configA = open('configA.txt').read() # or it may be a string
configB = open('configB.txt').read() # or it may be a string

configA = IndentedConfig(configA, comment_char='!', sanitize=True)
configB = IndentedConfig(configB, comment_char='!', sanitize=True)

print(dumps(configA.to_dict(), indent=2))
print(dumps(configB.to_dict(), indent=2))
```

Output:


<table>
 <thead>
  <tr>
   <th>Config A (to merge into B)</th>
   <th>Config B</th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td>

```json
{
  "no ip domain lookup": {},
  "interface FastEthernet0/0": {
    "no shutdown": {}
  },
  "interface FastEthernet0/0.10": {
    "description LAN": {},
    "encapsulation dot1Q 10": {},
    "ip address 192.168.1.254 255.255.255.0": {}
  },
  "router bgp 64512": {
    "neighbor 172.16.0.1 remote-as 100": {},
    "address-family ipv4": {
      "neighbor 172.16.0.1 activate": {},
      "neighbor 172.16.0.1 allowas-in 1": {},
      "neighbor 172.16.0.1 prefix-list IN in": {},
      "neighbor 172.16.0.1 prefix-list OUT out": {},
      "network 192.168.1.0 mask 255.255.255.0": {}
    }
  }
}
```
   </td>
   <td>

```json
{
  "hostname R1": {},
  "interface FastEthernet0/0": {
    "description LAN": {},
    "no ip address": {},
    "shutdown": {},
    "duplex auto": {},
    "speed auto": {}
  },
  "router bgp 64512": {
    "neighbor 172.16.0.1 remote-as 100": {},
    "address-family ipv4": {
      "neighbor 172.16.0.1 activate": {},
      "neighbor 172.16.0.1 prefix-list IN in": {},
      "neighbor 172.16.0.1 prefix-list OUT out": {}
    }
  },
  "ip prefix-list IN seq 5 permit 192.168.2.0/24": {},
  "ip prefix-list OUT seq 5 permit 192.168.1.0/24": {}
}
```
   </td>
  </tr>
 </tbody>
</table>

*There is no list but only dicts. Each item may have child items. The nesting level is NOT limited.*

At this point, you are free to compare the dicts the way you want. However, to that end, you may be interested in existing modules like [DeepDiff](https://github.com/seperman/deepdiff) or the lightweight [IncrementalDiff](#incremental-diff) helper embedded in this module.

**ℹ Depending on your config format, both `indent_char` and `comment_char` can be set at init:**

```py
IndentedConfig(config, comment_char='#', indent_char=' ') # default values (e.g., for Huawei)
IndentedConfig(config, comment_char='!')                  # '!' as comment_char (e.g., for Cisco)
IndentedConfig(config, indent_char='\t')                  # tab as indent_char
IndentedConfig(config, sanitize=True)                     # see next section
```

## Sanitizing

Your config may:

* have trailing spaces
* have blank lines
* contain comments
* not be correctly indented

The `sanitize()` method has been made to address this. The last point especially would break the tree conversion. The other ones would make some parts of the diff irrelevant.

```py
from diffplus import IndentedConfig

config = """
   # a global command badly indented
   sysname PE
#
interface GigabitEthernet0/0/1
   # badly indented as well
   description my-super-description
 ip address 1.1.1.1 255.255.255.0
#
"""

config = IndentedConfig(config, comment_char='#')
print(config)
config.sanitize()
print(config)
```

<table>
 <thead>
  <tr>
   <th>Print before sanitizing ❌</th>
   <th>Print after sanitizing ✔</th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td>

```sh
 
   # a global command badly indented
   sysname PE
#
interface GigabitEthernet0/0/1
   # badly indented as well
   description my-super-description
 ip address 1.1.1.1 255.255.255.0
#
```
   </td>
   <td>

```sh
sysname PE
interface GigabitEthernet0/0/1
 description my-super-description
 ip address 1.1.1.1 255.255.255.0
```
   </td>
  </tr>
 </tbody>
</table>

**ℹ It is recommended to always `sanitize` at init:**

```py
config = IndentedConfig(config, sanitize=True)
```

## Incremental diff

### Diff only

To compute the diff just as introduced in the [#problem](#problem) section:

```py
from diffplus import IndentedConfig, IncrementalDiff

configA = open('configA.txt').read()
configB = open('configB.txt').read()

configA = IndentedConfig(configA, comment_char='!', sanitize=True)
configB = IndentedConfig(configB, comment_char='!', sanitize=True)
diff = IncrementalDiff(configA, configB)

print(diff)
```

Output:

```diff
# items of A to be added in B (computed by IncrementalDiff)

+no ip domain lookup
interface FastEthernet0/0
+ no shutdown
+interface FastEthernet0/0.10
+ description LAN
+ encapsulation dot1Q 10
+ ip address 192.168.1.254 255.255.255.0
router bgp 64512
 address-family ipv4
+  neighbor 172.16.0.1 allowas-in 1
+  network 192.168.1.0 mask 255.255.255.0
```

### Merging

Alternatively, we can merge `A` into `B`. It is useful to get a preview of the full config before applying it:

```py
from diffplus import IndentedConfig, IncrementalDiff

configA = open('configA.txt').read()
configB = open('configB.txt').read()

configA = IndentedConfig(configA, comment_char='!', sanitize=True)
configB = IndentedConfig(configB, comment_char='!', sanitize=True)
diff = IncrementalDiff(configA, configB, merge=True)

print(diff)
```

Output:

```diff
# items of A merged into B (computed by IncrementalDiff)

hostname R1
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
+ ip address 192.168.1.254 255.255.255.0
```

### Colored diff

It is useful to better visualize the changes in the diff:

```py
from diffplus import IndentedConfig, IncrementalDiff

configA = open('configA.txt').read()
configB = open('configB.txt').read()

configA = IndentedConfig(configA, comment_char='!', sanitize=True)
configB = IndentedConfig(configB, comment_char='!', sanitize=True)
diff = IncrementalDiff(configA, configB, merge=True, colored=True)

print(diff)
```

Output:

<table>
 <thead>
  <tr>
   <th>Not colored</th>
   <th>Colored</th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td>
   
   ![](https://user-images.githubusercontent.com/4362224/222919743-cdec455b-d971-4d6a-82d3-9df749c80784.png)
   </td>
   <td>

   ![](https://user-images.githubusercontent.com/4362224/222919787-b0dc8f31-0cef-404d-8db7-c6111ff67af2.png)
   </td>
  </tr>
 </tbody>
</table>

Colorization is done through ANSI escape sequences: `\033[32m` for green color and `\033[m` for reset color.

### Under the hood

The incremental diff is computed recursively as a dict you can access (if needed) through the `to_dict()` method:

```py
diff = IncrementalDiff(configA, configB, merge=False) # or merge=True
print(dumps(diff.to_dict(), indent=2))
```

Output:

```json
{
  "+no ip domain lookup": {},
  "interface FastEthernet0/0": {
    "+no shutdown": {}
  },
  "+interface FastEthernet0/0.10": {
    "description LAN": {},
    "encapsulation dot1Q 10": {},
    "ip address 192.168.1.254 255.255.255.0": {}
  },
  "router bgp 64512": {
    "address-family ipv4": {
      "+neighbor 172.16.0.1 allowas-in 1": {},
      "+network 192.168.1.0 mask 255.255.255.0": {}
    }
  }
}
```

New items are marked with a `+` so that they can be pretty rendered recursively via the `__str__()` special method:

```py
print(diff)
print(str(diff)) # equivalent
print(diff.__str__()) # equivalent
```

## Diff using a third-party module

Converting `IndentedConfig` to dict allows for deep comparison using existing modules like [DeepDiff](https://github.com/seperman/deepdiff). This way, you are not stuck with the rather simplistic [IncrementalDiff](#incremental-diff) helper.

```py
from diffplus import IndentedConfig
from deepdiff import DeepDiff

configA = open('configA.txt').read()
configB = open('configB.txt').read()

configA = IndentedConfig(configA, comment_char='!', sanitize=True)
configB = IndentedConfig(configB, comment_char='!', sanitize=True)
diff = DeepDiff(configB.to_dict(), configA.to_dict())

for item_added in diff['dictionary_item_added']:
    print(item_added)
```

Output:

```py
root['no ip domain lookup']
root['interface FastEthernet0/0.10']
root['interface FastEthernet0/0']['no shutdown']
root['router bgp 64512']['address-family ipv4']['neighbor 172.16.0.1 allowas-in 1']
root['router bgp 64512']['address-family ipv4']['network 192.168.1.0 mask 255.255.255.0']
```

But third-party modules are generally heavier (since they offer more features) and may not do exactly what you want. For example, the above output does not include (on purpose) the children of missing items, e.g., `interface FastEthernet0/0.10` is missing from `B` **as well as its children yet NOT displayed:**

```sh
interface FastEthernet0/0.10 # displayed in above output as root['interface FastEthernet0/0.10']
 description LAN                        # not displayed in above output
 encapsulation dot1Q 10                 # not displayed in above output
 ip address 192.168.1.254 255.255.255.0 # not displayed in above output
```

# Does DiffPlus reinvent the wheel?

I didn't find a suitable module providing such an incremental and contextual diff simply based on an indented config (NOT necessarily Cisco-based or network-based for the sake of genericity).

* [difflib](https://docs.python.org/3/library/difflib.html) (Python builtin) does a line-by-line diff
* [DeepDiff](https://github.com/seperman/deepdiff) compares dicts but does not convert an indented text to dict
* [ConfigTree](https://github.com/Cottonwood-Technology/ConfigTree) only supports YAML and JSON formats
* [anytree](https://github.com/c0fec0de/anytree) drops the support of the indented text format
* [diffios](https://github.com/robphoenix/diffios) only supports Cisco format and it is not clear what it does exactly (variable parsing or diff?)
* [shconfparser](https://github.com/network-tools/shconfparser) (probably the closest one) only supports Cisco format and does not offer diff features
* [conf_diff](https://developer.cisco.com/codeexchange/github/repo/muhammad-rafi/conf_diff) does a line-by-line diff
