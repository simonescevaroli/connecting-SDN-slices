#!/bin/bash

ryu-manager control_office.py --observe-links --ofp-tcp-listen-port 6633 &
ryu-manager office1.py --observe-links --ofp-tcp-listen-port 6634 &
ryu-manager connecting_slice.py --observe-links --ofp-tcp-listen-port 6635  &
ryu-manager office2.py --observe-links --ofp-tcp-listen-port 6636 &
ryu-manager computer_room.py --observe-links --ofp-tcp-listen-port 6637 &