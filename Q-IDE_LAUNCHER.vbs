' Q-IDE Professional Launcher
' Double-click this file to start Q-IDE
' This is a more reliable launcher than .bat files

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the script's directory
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Hide the console window
objShell.Run "cmd.exe /c """ & strScriptPath & "\START.bat""", 0, False

' Wait a moment for processes to start
WScript.Sleep 3000

' Open the browser
objShell.Run "http://localhost:1431", 1, False
