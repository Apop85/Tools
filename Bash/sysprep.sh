#!/bin/bash
# -*- coding:utf-8 -*-

####
# File: sysprep.sh
# Project: Bash
#-----
# Created Date: Sunday 12.07.2020, 13:35
# Author: Apop85
#-----
# Last Modified: Sunday 12.07.2020, 22:13
#-----
# Copyright (c) 2020 Apop85
# This software is published under the MIT license.
# Check http://www.opensource.org/licenses/MIT for further informations
#-----
# Description: Prepares Ubuntu 20.04 for a cloned virtual machine
####

#Prüfe ob "dialog" installiert ist.
check=$(dpkg -s dialog 2>&1 | sed -n 2p | awk '{print $3}')
if [[ "$check" != "ok" ]]; then 
	echo -e "Fehlendes paket: dialog. Zum installieren \n\n\t\t\"sudo apt-get install dialog\"\n\nausführen"
	exit 1
fi


nachricht="Das System wird nun als Klon vorbereitet. Wurde das Template direkt gestartet sollte hier abgebrochen und die VM erst geklont werden. Fortsetzen?"
dialog --title "Information" --yesno "$nachricht" 10 30

# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
if [ $? -ne 0 ]; then
        exit 0
fi

# Prüfe ob Script Rootberechtigungen besitzt
if [ "$EUID" -ne 0 ]; then 
	path="$(realpath $0)"
	dialog --backtitle INFO --title "Bestätigung" \
		--yesno "Script wird als Root neu gestartet!" 10 30 

	input=${?}
	if [ "$input" == "1" ]; then
		exit 0
	fi
	[ `whoami` = root ] || exec sudo $path
else
	echo "Rootprivilegien vorhanden"
fi

auswahl=$(dialog --stdout --separate-output --title "Hauptmenü" \
	--checklist "Bitte Option(en) wählen:" 30 50 25 \
	1 "System updaten" on \
	2 "Hostnamen ändern" on \
	3 "SSH-Keys neu generieren" on \
	4 "Neuen Benutzer erstellen" on \
	5 "Alten Benutzer löschen" on \
	6 "Netzwerk konfigurieren" off)

# Wurde OK gedrückt?
if [ $? -eq 0 ]; then
	for wahl in $auswahl; do
		if [ $wahl -eq 2 ]; then
			while true; do
				# Neuen Hostnamen erstellen
				nachricht="Bitte gewünschten Hostnamen eingeben:"
				host_name=$(dialog --stdout --title "Hostname" --inputbox \
				"$nachricht" 20 45)
				if [[ $host_name =~ .*{3,} ]]; then
					nachricht="Ist der Hostname: $host_name korrekt?"
					dialog --title "Bestätigung" --yesno "$nachricht" 10 30

					# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
					if [ $? -eq 0 ]; then
						break
					fi
				fi
			done
		elif [ $wahl -eq 4 ]; then
			# Neuen User anlegen
			while true; do 
				nachricht="Bitte gewünschten Benutzernamen eingeben:"
				user_name=$(dialog --stdout --title "Username" --inputbox \
						"$nachricht" 20 45)

				# Wurde OK gedrückt?
				if [ $? -eq 0 ] && [ "$user_name" != "" ]; then
						nachricht="Ist der Benutzername: \"$user_name\" korrekt?"
								dialog --title "Bestätigung" --yesno "$nachricht" 10 30

						# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
						if [ $? -eq 0 ]; then
								break
						fi

				fi
			done
			while true; do 
				nachricht="Gewünschtes Passwort für $user_name eingeben:"
				user_pass=$(dialog --stdout --title "Passwort" \
						--passwordbox "$nachricht" 20 45)

				nachricht="Passwort widerholen:"
				passwort_verify=$(dialog --stdout --title "Passwort" \
							--passwordbox "$nachricht" 20 45)

				if [ $user_pass != $passwort_verify ]; then
					nachricht="Passwörter stimmen nicht überein. Bitte widerholen."
					dialog --title "Passwortübereinstimmung" --msgbox \
							"$nachricht" 6 35
				elif [[ "$user_pass" =~ .{8,16} ]]; then
					passwort_verify=""
					passwort_encrypted=$(openssl passwd -1 $user_pass)
					break 
				else
					nachricht="Passwort nicht Stark genug. Muss 8-16 Zeichen beinhalten."
					dialog --title "Passwortstärke" --msgbox \
							"$nachricht" 6 35
				fi
			done
		elif [ $wahl -eq 5 ]; then
			# Alten User löschen
			while true; do
				delusername=$(logname)
				nachricht="Soll der User \"$delusername\" gelöscht werden? Falls nein, kann ein anderer User zum löschen eingegben werden"
				dialog --backtitle INFO --title "Bestätigung" \
					--yesno "$nachricht" 10 30 
				
				# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
				if [ $? -eq 0 ]; then
					break
				else
					nachricht="Benuzter der gelöscht werden soll angeben: "
					delusername=$(dialog --stdout --title "Username" --inputbox \
							"$nachricht" 20 45)
					checkuser=$(grep -c '^$delusername:' /etc/passwd)
					if [ $checkuser -geq 1 ]; then
						break
					else
						nachricht="Der Benutzer \"$delusername\" existiert nicht."
						dialog --title "Fehler" --msgbox \
							"$nachricht" 6 35
					fi
				fi
			done
		elif [ $wahl -eq 6 ]; then
			# Netzwerk konfigurieren
				while true; do
					nachricht="Bitte gewünschte IP-Adresse eingeben:"
					ip_address=$(dialog --stdout --title "IP-Adresse" --inputbox \
							"$nachricht" 20 45)

					# Wurde OK gedrückt?
					if [ $? -eq 0 ]; then
						# Lese Oktette aus
						q1=$(echo $ip_address | sed -E "s/\./ /g" | awk '{print $1}' )
						q2=$(echo $ip_address | sed -E "s/\./ /g" | awk '{print $2}' )
						q3=$(echo $ip_address | sed -E "s/\./ /g" | awk '{print $3}' )
						q4=$(echo $ip_address | sed -E "s/\./ /g" | awk '{print $4}' )
						echo "-$q1-$q2-$q3-$q4-"
						# Prüfe ob Oktette grösser 0 und kleiner 255 sind und die IP dem vorgegebenen Musrer entspricht
						if [[ $ip_address =~ [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} ]] && (( $q1 >= 1 )) && (( $q1 <= 255 )) && (( $q2 >= 1 )) && (( $q2 <= 255 )) && (( $q3 >= 1 )) && (( $q3 <= 255 )) && (( $q4 >= 1 )) && (( $q4 <= 255 )); then
							nachricht="Ist die IP-Adresse: \"$ip_address\" korrekt?"
								dialog --title "Bestätigung" --yesno "$nachricht" 10 30

							# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
							if [ $? -eq 0 ]; then
									break
							fi
						else
							# Ungültige IP
							nachricht="Die IP-Adresse \"$ip_address\" ist ungültig."
							dialog --title "Fehler" --msgbox \
								"$nachricht" 6 35
						fi
					fi
				done
				
				while true; do
					nachricht="CIDR angeben:"
					cidr=$(dialog --stdout --title "CIDR" --menu \
					"$nachricht" 10 30 8 \
					30 "2 IPs" \
					29 "6 IPs" \
					28 "14 IPs" \
					27 "30 IPs" \
					26 "62 IPs" \
					25 "126 IPs" \
					24 "254 IPs" \
					23 "510 IPs" \
					22 "1022 IPs" \
					21 "2046 IPs" \
					20 "4094 IPs" \
					19 "8190 IPs" \
					18 "16382 IPs" \
					17 "32.7k IPs" \
					16 "65k IPs" \
					15 "131k IPs" \
					14 "262k IPs" \
					13 "524k IPs" \
					12 "1 Mio IPs" \
					11 "2 Mio IPs" \
					10 "4.1 Mio IPs" \
					9 "8.3 Mio IPs" \
					8 "16.7 Mio IPs" \
					7 "33.5 Mio IPs" \
					6 "67 Mio IPs" \
					5 "134 Mio IPs" \
					4 "500 Mio IPs" \
					3 "1 Mia IPs" \
					2 "1 Mia IPs" \
					1 "2 Mia IPs" \
					0 "4 Mia IPs" )
				
					nachricht="Ist die Angabe: \"$cidr\" korrekt?"
					dialog --title "Bestätigung" --yesno "$nachricht" 10 30

					# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
					if [ $? -eq 0 ]; then
						break
					fi
				done

				while true; do
					nachricht="Bitte gewünschte Gatewayadresse angeben:"
					gateway=$(dialog --stdout --title "Gateway-IP" --inputbox \
							"$nachricht" 20 45)

					# Wurde OK gedrückt?
					if [ $? -eq 0 ]; then
						# Lese Oktette aus
						q1=$(echo $gateway | sed -E "s/\./ /g" | awk '{print $1}' )
						q2=$(echo $gateway | sed -E "s/\./ /g" | awk '{print $2}' )
						q3=$(echo $gateway | sed -E "s/\./ /g" | awk '{print $3}' )
						q4=$(echo $gateway | sed -E "s/\./ /g" | awk '{print $4}' )
						# Prüfe ob Oktette grösser 0 und kleiner 255 sind und die IP dem vorgegebenen Musrer entspricht
						if [[ $gateway =~ [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} ]] && (( $q1 >= 1 )) && (( $q1 <= 255 )) && (( $q2 >= 1 )) && (( $q2 <= 255 )) && (( $q3 >= 1 )) && (( $q3 <= 255 )) && (( $q4 >= 1 )) && (( $q4 <= 255 )); then
							nachricht="Ist die Gateway-IP-Adresse: \"$gateway\" korrekt?"
								dialog --title "Bestätigung" --yesno "$nachricht" 10 30

							# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
							if [ $? -eq 0 ]; then
									break
							fi
						else
							# Ungültige IP
							nachricht="Die Gateway-IP-Adresse \"$gateway\" ist ungültig."
							dialog --title "Fehler" --msgbox \
								"$nachricht" 6 35
						fi
					fi
				done

				dns_servers=""
				while true; do
					nachricht="Bitte gewünschten DNS-Server angeben:"
					dns=$(dialog --stdout --title "DNS-IP" --inputbox \
							"$nachricht" 20 45)

					# Wurde OK gedrückt?
					if [ $? -eq 0 ]; then
						# Lese Oktette aus
						q1=$(echo $dns | sed -E "s/\./ /g" | awk '{print $1}' )
						q2=$(echo $dns | sed -E "s/\./ /g" | awk '{print $2}' )
						q3=$(echo $dns | sed -E "s/\./ /g" | awk '{print $3}' )
						q4=$(echo $dns | sed -E "s/\./ /g" | awk '{print $4}' )
						# Prüfe ob Oktette grösser 0 und kleiner 255 sind und die IP dem vorgegebenen Musrer entspricht
						if [[ $dns =~ [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} ]] && (( $q1 >= 1 )) && (( $q1 <= 255 )) && (( $q2 >= 1 )) && (( $q2 <= 255 )) && (( $q3 >= 1 )) && (( $q3 <= 255 )) && (( $q4 >= 1 )) && (( $q4 <= 255 )); then
							nachricht="Ist die DNS-IP-Adresse: \"$dns\" korrekt?"
								dialog --title "Bestätigung" --yesno "$nachricht" 10 30

							# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
							if [ $? -eq 0 ]; then
								dns_servers+="$dns,"
								nachricht="Einen weiteren DNS-Server hinzufügen?"
								dialog --title "Option" --yesno "$nachricht" 10 30
								if [ $? -eq 1 ]; then
									dns_servers=${dns_servers:0:-1}
									break
								fi
							fi
						else
							# Ungültige IP
							nachricht="Die DNS-IP-Adresse \"$dns\" ist ungültig."
							dialog --title "Fehler" --msgbox \
								"$nachricht" 6 35
						fi
					fi
				done
		fi
	done
	# Wende Änderungen an
	infocolor="\e[107m\e[30m"
	resetcolor="\e[0m"
	for wahl in $auswahl; do
		if [ $wahl -eq 1 ]; then
			# Updaten
			echo -e "${infocolor}[Info]${resetcolor} Quellen werden geupdated"
			apt-get update >/dev/null 2>&1
			echo -e "${infocolor}[Info]${resetcolor} fehlende dependecies werden installiert"
			apt-get upgrade --fix-missing -y >/dev/null 2>&1
			echo -e "${infocolor}[Info]${resetcolor} Updates werden installiert"
			apt-get upgrade -y >/dev/null 2>&1
			echo -e "${infocolor}[Info]${resetcolor} Nicht mehr benötigte Pakete werden entfernt"
			apt-get autoremove -y >/dev/null 2>&1
		elif [ $wahl -eq 2 ]; then
			# Hostname
			echo -e "${infocolor}[Info]${resetcolor} Hostname wird geändert"
			current_hostname=$(hostname)
			echo $host_name > /etc/hostname
			sed -i "s/$current_hostname/$host_name/g" /etc/hosts
		elif [ $wahl -eq 3 ]; then
			# SSH Keys erneuern
			echo -e "${infocolor}[Info]${resetcolor} Lösche vorhandene SSH-Keys"
			rm -v /etc/ssh/ssh_host_* -f
			echo -e "${infocolor}[Info]${resetcolor} Erstelle neue Keys"
			dpkg-reconfigure openssh-server
			echo -e "${infocolor}[Info]${resetcolor} Service neu starten"
			systemctl restart ssh
		elif [ $wahl -eq 4 ]; then
			# Benutzer hinzufügen
			echo -e "${infocolor}[Info]${resetcolor} Füge neuen Benutzer hinzu"
			addgroup $user_name
			useradd -m -c $user_name -g "$user_name" -G "sudo" $user_name -p $passwort_encrypted -s "/bin/bash"
		elif [ $wahl -eq 5 ]; then
			# Benutzer löschen
			echo -e "${infocolor}[Info]${resetcolor} Plane Aufgabe für die Löschung von $delusername"
			echo -e "\#\!/bin/bash\ninfocolor=\"\\e[107m\\e[30m\"\nresetcolor=\"\\e[0m\"\ndialog --title \"Entferne Benutzer\" --msgbox \"Der zuvor vorhandene Benutzer wird entfernt. Dazu sind Rootberechtigungen nötig.\" 20 45\necho -e \"\${infocolor}[Info]\${resetcolor} User entfernen\"\nsudo deluser $delusername --remove-home\necho -e \"\${infocolor}[Info]\${resetcolor} Gruppe entfernen\"\nsudo delgroup $delusername\n\necho -e \"\${infocolor}[Info]\${resetcolor} Script wird von Autostart entfernt.\"\nhead -n -1 /home/$user_name/.bashrc >> /home/$user_name/bashrc.tmp\nrm /home/$user_name/.bashrc\nmv /home/$user_name/bashrc.tmp /home/$user_name/.bashrc" > /scripts/rmusr.sh
			chmod +x /scripts/rmusr.sh
			echo /scripts/rmusr.sh >> /home/$user_name/.bashrc
		elif [ $wahl -eq 6 ]; then
			# Netzwerkkonfiguration
			echo -e "${infocolor}[Info]${resetcolor} Ändere Netzwerkkonfiguration"
			echo -e "network:\n  version: 2\n  renderer: networkd\n  ethernets:\n      ens33:\n        dhcp4: no\n        addresses: [$ip_address/$cidr]\n        gateway4: $gateway\n        nameservers:\n          addresses: [$dns_servers]" > /etc/netplan/00-installer-config.yaml
			echo -e "${infocolor}[Info]${resetcolor} Wende Netzwerkkonfiguration an"
			ifconfig ens33 down
			netplan apply
			sleep 10
			ifconfig ens33 up
		fi
	done

	nachricht="Damit die Änderungen angewendet werden, muss die VM neu gestartet werden."
	dialog --title "Reboot" --pause "$nachricht" 15 20 10
	# Ist die Antwort auf Ja wird $? 0 ausgeben bei Nein 1
	if [ $? -eq 1 ]; then
		exit 0
	fi
	# Entferne NOPASSWD
	rm /etc/sudoers
	mv /etc/sudoers.bak /etc/sudoers
	# Entferne Autologin
	echo > /etc/systemd/system/getty@tty1.service.d/override.conf

	reboot now
else
	exit 0
fi


