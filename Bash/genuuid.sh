#!/bin/bash

dialog --title "Systemvorbereitung" --yesno "Der folgende Vorgang wird die ID's der Festplatten\
 randomisieren und anschliessend die Bootreihenfolge ändern. DIESES SYSTEM WIRD NACH DER FERTIGSTELLUNG VERNICHTET." 20 45

clear
if [ $? == 1 ]; then
    exit 0
fi

function regenuuid() {
    infocolor="\e[107m\e[30m"
    errorcolor="\e[101m\e[97"
    endcolor="\e[102m\e[30m"
    resetcolor="\e[0m"
    # Prüfe Disk auf Fehler
    echo -e "${infocolor}[INFO]${resetcolor} Partition wird auf Fehler überprüft"
    e2fsck -f /dev/sda2 

    # Wechsle UUID
    echo -e "${infocolor}[INFO]${resetcolor} Partition erhält neue UUID"
    uuid_old=$(ls -l /dev/disk/by-uuid/ | grep "sda2" | awk '{print $9}')
    echo -e "${infocolor}[INFO]${resetcolor} Alte UUID: $uuid_old"
    random_uuid=$(uuidgen)
    echo -e "${infocolor}[INFO]${resetcolor} Weise neue ID zu..."
    while true; do
        tune2fs -U $random_uuid /dev/sda2 
        sleep 5
        uuid_new=$(ls -l /dev/disk/by-uuid/ | grep "sda2" | awk '{print $9}')
        if [[ $uuid_new != $uuid_old ]]; then
            echo -e "${infocolor}[INFO]${resetcolor} Mounte /dev/sda2"
            mount /dev/sda2 /mnt/disk1
            sed -i "s/$uuid_old/$random_uuid/g" /boot/grub/grub.cfg
            echo -e "${infocolor}[INFO]${resetcolor} Passe ID's in Configfiles an"
            sed -i "s/$uuid_old/$random_uuid/g" /mnt/disk1/boot/grub/grub.cfg
            echo -e "${infocolor}[INFO]${resetcolor} Neue UUID: $uuid_new"
            echo -e "${infocolor}[INFO]${resetcolor} Ändere GRUB-Bootreihenfolge"
            sed -i "s/GRUB_DEFAULT=0/GRUB_DEFAULT=2/g" /etc/default/grub
            # sed -i "s/GRUB_TIMEOUT=2/GRUB_TIMEOUT=0/g" /etc/default/grub
            echo -e "${infocolor}[INFO]${resetcolor} Aktiviere autologin für Ubuntu"
            original_string="-o '-p -- ..u'"
            replace_string="-a root"
            sed -i "s/$original_string/$replace_string/g"  /mnt/disk1/lib/systemd/system/getty@.service
            echo -e "${infocolor}[INFO]${resetcolor} Update Grub..."
            update-grub
            /mnt/disk1/sbin/update-grub /dev/sda 
            echo -e "${endcolor}#############################################################${resetcolor}"
            echo -e "${endcolor}     VORBEREITUNG ABGESCHLOSSEN. ENTER UM FORTZUFAHREN       ${resetcolor}"
            echo -e "${endcolor}#############################################################${resetcolor}"
            break
        elif [[ $uuid_new == $uuid_old ]]; then
            echo -e "${errorcolor}[FEHLER]${resetcolor} Wechseln der UUID fehlgeschlagen..."
            echo -e "${errorcolor}[FEHLER]${resetcolor} UUIDs sind identisch"
            echo -e "${errorcolor}[FEHLER]${resetcolor} Probiere erneut..."
        else
            echo -e "${errorcolor}[FEHLER]${resetcolor} Unbekannter Fehler"
            echo -e "${errorcolor}[FEHLER]${resetcolor} $uuid_new"
            echo -e "${errorcolor}[FEHLER]${resetcolor} $uuid_old"
        fi
    done
    read waiting
}

regenuuid

if [[ $? != 1 ]]; then
    reboot now
fi

# swaplabel -U $(uuidgen) /SWAP?????