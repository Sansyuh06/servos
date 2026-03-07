rule Ransomware_Note_Generic {
    meta:
        description = "Generic ransomware note indicators"
        severity = "critical"
        category = "ransomware"
    strings:
        $r1 = "your files have been encrypted" ascii nocase
        $r2 = "bitcoin" ascii nocase
        $r3 = "decrypt" ascii nocase
        $r4 = "ransom" ascii nocase
        $r5 = "payment" ascii nocase
        $r6 = "wallet" ascii nocase
        $r7 = ".onion" ascii nocase
        $r8 = "tor browser" ascii nocase
    condition:
        3 of them
}

rule Ransomware_File_Encryption {
    meta:
        description = "File encryption behavior patterns"
        severity = "critical"
        category = "ransomware"
    strings:
        $e1 = "CryptEncrypt" ascii
        $e2 = "CryptGenKey" ascii
        $e3 = "CryptAcquireContext" ascii
        $e4 = "AES" ascii
        $e5 = "RSA" ascii
        $e6 = "encrypt_file" ascii nocase
        $e7 = "FindFirstFile" ascii
        $e8 = "FindNextFile" ascii
        $e9 = "DeleteShadowCopies" ascii nocase
    condition:
        4 of them
}

rule Ransomware_Shadow_Delete {
    meta:
        description = "Shadow copy deletion (ransomware behavior)"
        severity = "critical"
        category = "ransomware"
    strings:
        $s1 = "vssadmin delete shadows" ascii nocase
        $s2 = "wmic shadowcopy delete" ascii nocase
        $s3 = "bcdedit /set" ascii nocase
        $s4 = "recoveryenabled no" ascii nocase
        $s5 = "wbadmin delete catalog" ascii nocase
    condition:
        any of them
}

rule Ransomware_Dropper_Script {
    meta:
        description = "Ransomware dropper via script"
        severity = "high"
        category = "ransomware"
    strings:
        $d1 = "DownloadFile" ascii nocase
        $d2 = "Invoke-WebRequest" ascii nocase
        $d3 = "Start-Process" ascii nocase
        $d4 = "-WindowStyle Hidden" ascii nocase
        $d5 = "certutil" ascii nocase
        $d6 = "-urlcache" ascii nocase
        $d7 = "bitsadmin" ascii nocase
    condition:
        3 of them
}
