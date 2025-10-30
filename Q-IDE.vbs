'' Q-IDE TOPDOG - PROFESSIONAL LAUNCHER
'' Single-click, silent launch with no visible windows
'' Works exactly like professional applications (Discord, Slack, etc.)

Option Explicit

Dim objFSO, objShell, strRootDir, strBackendPath, strFrontendPath
Dim objWMI, objService, objProcess, intExitCode

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objShell = CreateObject("WScript.Shell")

'' Get the directory where this script is located
strRootDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
strBackendPath = objFSO.BuildPath(strRootDir, "backend")
strFrontendPath = objFSO.BuildPath(strRootDir, "frontend")

'' ============================================================================
'' Function: Show splash screen (professional startup message)
'' ============================================================================
Function ShowSplash()
    Dim objHTMLFile, strHTMLPath, strHTML
    
    strHTMLPath = objFSO.BuildPath(objFSO.GetTempFolder(), "Q_IDE_Splash.html")
    
    strHTML = "<!DOCTYPE html>" & vbCrLf & _
        "<html>" & vbCrLf & _
        "<head>" & vbCrLf & _
        "  <meta charset='utf-8'>" & vbCrLf & _
        "  <title>Q-IDE Topdog Launching</title>" & vbCrLf & _
        "  <style>" & vbCrLf & _
        "    * { margin: 0; padding: 0; box-sizing: border-box; }" & vbCrLf & _
        "    body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }" & vbCrLf & _
        "    .splash { background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 60px 80px; text-align: center; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); max-width: 500px; }" & vbCrLf & _
        "    .logo { font-size: 60px; margin-bottom: 20px; }" & vbCrLf & _
        "    h1 { color: #333; font-size: 32px; margin-bottom: 10px; font-weight: 600; }" & vbCrLf & _
        "    .subtitle { color: #666; font-size: 16px; margin-bottom: 30px; }" & vbCrLf & _
        "    .loading { margin-top: 40px; }" & vbCrLf & _
        "    .spinner { border: 4px solid #f0f0f0; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px; }" & vbCrLf & _
        "    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }" & vbCrLf & _
        "    .status { color: #999; font-size: 14px; margin-top: 10px; }" & vbCrLf & _
        "  </style>" & vbCrLf & _
        "</head>" & vbCrLf & _
        "<body>" & vbCrLf & _
        "  <div class='splash'>" & vbCrLf & _
        "    <div class='logo'>🚀</div>" & vbCrLf & _
        "    <h1>Q-IDE Topdog</h1>" & vbCrLf & _
        "    <p class='subtitle'>Advanced AI Development Environment</p>" & vbCrLf & _
        "    <div class='loading'>" & vbCrLf & _
        "      <div class='spinner'></div>" & vbCrLf & _
        "      <p class='status'>Launching servers...</p>" & vbCrLf & _
        "    </div>" & vbCrLf & _
        "  </div>" & vbCrLf & _
        "</body>" & vbCrLf & _
        "</html>"
    
    On Error Resume Next
    Set objHTMLFile = objFSO.CreateTextFile(strHTMLPath, True)
    objHTMLFile.WriteLine(strHTML)
    objHTMLFile.Close()
    
    objShell.Run "start " & strHTMLPath, 1, False
    
    On Error GoTo 0
End Function

'' ============================================================================
'' Function: Cleanup old processes
'' ============================================================================
Function CleanupOldProcesses()
    On Error Resume Next
    
    objShell.Run "taskkill /F /IM python.exe", 0, False
    objShell.Run "taskkill /F /IM python3.11.exe", 0, False
    objShell.Run "taskkill /F /IM node.exe", 0, False
    objShell.Run "taskkill /F /IM npm.exe", 0, False
    
    WScript.Sleep 2000
    
    On Error GoTo 0
End Function

'' ============================================================================
'' Function: Start backend server
'' ============================================================================
Function StartBackend()
    On Error Resume Next
    
    Dim strCommand
    strCommand = "cd /d """ & strBackendPath & """ && python main.py"
    
    objShell.Run "cmd /c " & strCommand, 0, False
    
    WScript.Sleep 6000
    
    On Error GoTo 0
End Function

'' ============================================================================
'' Function: Start frontend server
'' ============================================================================
Function StartFrontend()
    On Error Resume Next
    
    Dim strCommand
    strCommand = "cd /d """ & strFrontendPath & """ && pnpm run dev"
    
    objShell.Run "cmd /c " & strCommand, 0, False
    
    WScript.Sleep 8000
    
    On Error GoTo 0
End Function

'' ============================================================================
'' Function: Open browser
'' ============================================================================
Function OpenBrowser()
    On Error Resume Next
    
    WScript.Sleep 3000
    objShell.Run "start http://127.0.0.1:1431", 1, False
    
    On Error GoTo 0
End Function

'' ============================================================================
'' Main execution
'' ============================================================================

On Error Resume Next

'' Verify directories exist
If Not objFSO.FolderExists(strBackendPath) Then
    MsgBox "Error: Backend directory not found at" & vbCrLf & strBackendPath, vbCritical, "Q-IDE Launch Failed"
    WScript.Quit 1
End If

If Not objFSO.FolderExists(strFrontendPath) Then
    MsgBox "Error: Frontend directory not found at" & vbCrLf & strFrontendPath, vbCritical, "Q-IDE Launch Failed"
    WScript.Quit 1
End If

'' Execute launch sequence
CleanupOldProcesses()
StartBackend()
StartFrontend()
OpenBrowser()

'' Show success message
MsgBox "Q-IDE Topdog has been launched successfully!" & vbCrLf & vbCrLf & _
       "Your application will open in your default browser at:" & vbCrLf & _
       "http://127.0.0.1:1431" & vbCrLf & vbCrLf & _
       "Backend API: http://127.0.0.1:8000" & vbCrLf & _
       "API Docs: http://127.0.0.1:8000/docs", vbInformation, "Q-IDE Topdog"

On Error GoTo 0

WScript.Quit 0
