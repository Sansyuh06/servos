rule Suspicious_PowerShell {
    meta:
        description = "Suspicious PowerShell usage"
        severity = "high"
        category = "scripts"
    strings:
        $p1 = "-EncodedCommand" ascii nocase
        $p2 = "-enc " ascii nocase
        $p3 = "FromBase64String" ascii nocase
        $p4 = "Invoke-Expression" ascii nocase
        $p5 = "IEX" ascii
        $p6 = "-WindowStyle Hidden" ascii nocase
        $p7 = "-ExecutionPolicy Bypass" ascii nocase
        $p8 = "DownloadString" ascii nocase
        $p9 = "Net.WebClient" ascii nocase
    condition:
        3 of them
}

rule Suspicious_VBS_Script {
    meta:
        description = "Suspicious VBScript indicators"
        severity = "medium"
        category = "scripts"
    strings:
        $v1 = "WScript.Shell" ascii nocase
        $v2 = "CreateObject" ascii nocase
        $v3 = "Shell.Application" ascii nocase
        $v4 = "RegWrite" ascii nocase
        $v5 = "Run" ascii nocase
        $v6 = "Execute" ascii nocase
    condition:
        4 of them
}

rule Suspicious_Batch_Script {
    meta:
        description = "Suspicious batch file patterns"
        severity = "medium"
        category = "scripts"
    strings:
        $b1 = "reg add" ascii nocase
        $b2 = "reg delete" ascii nocase
        $b3 = "net user" ascii nocase
        $b4 = "net localgroup" ascii nocase
        $b5 = "attrib +h" ascii nocase
        $b6 = "del /f /q" ascii nocase
        $b7 = "taskkill /f" ascii nocase
        $b8 = "sc stop" ascii nocase
    condition:
        3 of them
}

rule Office_Macro_Dropper {
    meta:
        description = "Malicious Office macro indicators"
        severity = "high"
        category = "scripts"
    strings:
        $m1 = "Auto_Open" ascii nocase
        $m2 = "Workbook_Open" ascii nocase
        $m3 = "Document_Open" ascii nocase
        $m4 = "Shell(" ascii nocase
        $m5 = "MacroOptions" ascii nocase
        $m6 = "VBA.Shell" ascii nocase
        $m7 = "CreateObject" ascii nocase
        $m8 = "WScript" ascii nocase
    condition:
        3 of them
}

rule Obfuscated_JavaScript {
    meta:
        description = "Obfuscated JavaScript patterns"
        severity = "medium"
        category = "scripts"
    strings:
        $j1 = "eval(" ascii nocase
        $j2 = "unescape(" ascii nocase
        $j3 = "fromCharCode" ascii nocase
        $j4 = "atob(" ascii nocase
        $j5 = "String.fromCharCode" ascii nocase
        $j6 = "document.write" ascii nocase
        $j7 = "ActiveXObject" ascii nocase
    condition:
        3 of them
}
