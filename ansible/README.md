# Flight Computer Setup Instructions
0. Required software: Raspberry Pi Imager, ansible
1. Flash "Raspberry Pi OS Lite (32 bit)" to the sd card with the Raspberry Pi Imager. Change the following settings:
```
[X] Set Hotname: rocket-pi
[X] Enable SSH
    [ ] Password
    [X] Public Key: <your public key here>
[X] Set username and password
    Username: pi
```
> Note: We're gonna switch to 64-bit when we get the new pi's
2. Copying `wpa_supplicant.conf` from `boot` to the boot partition
> Note: If your using RHIT-OPEN, you must add the MAC address to clearpass before booting the pi
3. Eject the SD and boot the pi. This can take over 4 minutes!
4. Ensure you have ssh access with `ssh pi@rocket-pi`
> If you have a different hostname, be sure to update ansible_hosts
5. Setup all of the software with `ansible-playbook playbook.yaml -i ansible_hosts`. This can also take a very long time
