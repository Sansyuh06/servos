rule Trojan_RAT_Generic {
    meta:
        description = "Remote Access Trojan indicators"
        severity = "critical"
        category = "trojan"
    strings:
        $t1 = "reverse_tcp" ascii nocase
        $t2 = "bind_tcp" ascii nocase
        $t3 = "meterpreter" ascii nocase
        $t4 = "CreateRemoteThread" ascii
        $t5 = "VirtualAllocEx" ascii
        $t6 = "WriteProcessMemory" ascii
        $t7 = "NtCreateThreadEx" ascii
    condition:
        2 of them
}

rule Trojan_Keylogger {
    meta:
        description = "Keylogger behavior patterns"
        severity = "high"
        category = "trojan"
    strings:
        $k1 = "GetAsyncKeyState" ascii
        $k2 = "SetWindowsHookEx" ascii
        $k3 = "GetKeyState" ascii
        $k4 = "keylog" ascii nocase
        $k5 = "keystroke" ascii nocase
        $k6 = "GetForegroundWindow" ascii
    condition:
        3 of them
}

rule Trojan_Credential_Stealer {
    meta:
        description = "Credential stealing indicators"
        severity = "critical"
        category = "trojan"
    strings:
        $c1 = "chrome\\User Data\\Default\\Login Data" ascii nocase
        $c2 = "firefox\\Profiles" ascii nocase
        $c3 = "Credentials" ascii nocase
        $c4 = "passwords.txt" ascii nocase
        $c5 = "sqlite3" ascii nocase
        $c6 = "CryptUnprotectData" ascii
        $c7 = "vaultcli" ascii nocase
    condition:
        3 of them
}

rule Backdoor_Reverse_Shell {
    meta:
        description = "Reverse shell patterns"
        severity = "critical"
        category = "backdoor"
    strings:
        $b1 = "socket" ascii nocase
        $b2 = "connect" ascii nocase
        $b3 = "subprocess" ascii nocase
        $b4 = "cmd.exe" ascii nocase
        $b5 = "/bin/sh" ascii
        $b6 = "/bin/bash" ascii
        $b7 = "nc -e" ascii
        $b8 = "ncat" ascii nocase
    condition:
        ($b1 and $b2 and $b3) or ($b7) or ($b4 and $b1 and $b2)
}

rule Backdoor_Persistence {
    meta:
        description = "Persistence mechanism installation"
        severity = "high"
        category = "backdoor"
    strings:
        $p1 = "CurrentVersion\\Run" ascii nocase
        $p2 = "schtasks /create" ascii nocase
        $p3 = "StartupFolder" ascii nocase
        $p4 = "sc create" ascii nocase
        $p5 = "New-Service" ascii nocase
        $p6 = "HKLM\\SOFTWARE" ascii nocase
        $p7 = "RegSetValueEx" ascii
    condition:
        2 of them
}
