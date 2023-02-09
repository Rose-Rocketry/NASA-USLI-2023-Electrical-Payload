# Local testing with vagrant
> Note: we should try to aim to make this as similar to the real thing as possible, but there's a limit to what we can test without the actual hardware

1. Install vagrant and ansible
> Note: If running on windows, make sure [Hyper-V](https://learn.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v) is enabled. This will require admin privliges in the terminal you expect to be working in as a limitation to Hyper-V.
2. Run `vagrant up`
> Note: Rose-Hulman blocks all DNS traffic that isn't to their dns servers, which breaks vagrant. This can be fixed by manually editing `/etc/resolv.conf` with `vagrant ssh`
3. After making changes to the ansible files, run `vagrant provision` to re-apply them. Run `vagrant destroy -f` to delete the VM's, and `vagrant up` to create new ones

# Flight Computer Setup Instructions
0. Required software: Raspberry Pi Imager, ansible
1. Flash "Raspberry Pi OS Lite (32 bit)" to the sd card with the Raspberry Pi Imager. Change the following settings:
```
[X] Set Hotname: rocket-pi
[X] Enable SSH
    [X] Password
    [ ] Public Key
[X] Set username and password
    Username: pi
```
> Note: We're gonna switch to 64-bit when we get the new pi's
2. Copying `wpa_supplicant.conf` from `boot` to the boot partition
> Note: If your using RHIT-OPEN, you must add the MAC address to clearpass before booting the pi
3. Eject the SD and boot the pi. This can take over 5 minutes!
4. Ensure you have ssh access with `ssh pi@rocket-pi`
> If you have a different hostname, be sure to update inventory.txt
5. Setup all of the software with `ansible-playbook playbook.yaml -i ansible_hosts` or `ansible-playbook playbook.yaml -i subscale_hosts` for subscale. This can also take a very long time

# IP Addresses
Withing the xblink network, all devices will be in the `10.82.104.0/24` subnet. The groundstation will have an ip of `10.82.104.2`, and rocket(s) will have ip(s) of `10.82.104.3`, `10.82.104.4`, etc...
> 82.104 is ASCII for `"Rh"`
