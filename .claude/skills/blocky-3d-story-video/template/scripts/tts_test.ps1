# Stand-in narration from the built-in Windows voice, for testing the pipeline only. A real video uses a recorded voice.
param([string]$Script, [string]$Out, [int]$Rate = 4)
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.Rate = $Rate
$s.SetOutputToWaveFile($Out)
$s.Speak((Get-Content -Raw -Encoding UTF8 $Script))
$s.Dispose()
Write-Output "wrote $Out"
