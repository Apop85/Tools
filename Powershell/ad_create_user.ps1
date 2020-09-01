$usernames = @{ 'ursmei01' = 'Urs', 'Meier', 'urs.meier@creasol.ch', 'CEO'; 
                'viokra01' = 'Viola', 'Kräzer', 'viola.kraezer@creasol.ch', 'Marketing'; 
                'rolber01' = 'Roland', 'Berger', 'roland.berger@creasol.ch', 'Architektur'; 
                'hanglu01' = 'Hannah', 'Glühwind', 'hannah.gluehwind@creasol.ch', 'Architektur'; 
                'karmei01' = 'Karl', 'Meister', 'karl.meister@creasol.ch', 'Architektur'; 
                'thokur01' = 'Thomas', 'Kurzwell', 'thomas.kurzwell@creasol.ch', 'Buchhaltung'
            }

$user_groups = @{}
$user_keys = $usernames.Keys
$default_password = "Zli.1234"
$company = "creasol"
$city = "Zürich"

foreach ($user in $user_keys) {
    if (@(Get-ADUser -Filter { SamAccountName -eq $user }).Count -eq 0) {
        Write-Warning -Message "User $user does not exist."
        Write-Host "Creating user: $user"
        $vorname = $usernames.Get_Item($user)[0]
        $nachname = $usernames.Get_Item($user)[1]
        $usermail = $usernames.Get_Item($user)[2]
        $department = $usernames.Get_Item($user)[3]
        # New-ADUser -SamAccountName $user -Name "$user" -Surname $nachname -GivenName $vorname -UserPrincipalName $usermail -AccountPassword $default_password -Enabled $false -PasswordNeverExpires $false -Company $company -City $city -Department $department
        # Enable-ADAccount -Identity $user
    }
}