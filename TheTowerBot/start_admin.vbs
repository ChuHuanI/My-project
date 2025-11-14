Set objShell = CreateObject("Shell.Application")
scriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(Wscript.ScriptFullName)
pywPath = scriptPath & "\autoclicker.pyw"
objShell.ShellExecute "py.exe", """" & pywPath & """", "", "runas", 1
Set objShell = Nothing
