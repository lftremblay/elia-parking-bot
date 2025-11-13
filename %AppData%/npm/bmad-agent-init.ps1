#!/usr/bin/env pwsh
$basedir=Split-Path $MyInvocation.MyCommand.Definition -Parent

$exe=""
if ($PSVersionTable.PSVersion -lt "6.0" -or $IsWindows) {
  # Fix case when both the Windows and Linux builds of Node
  # are installed in the same directory
  $exe=".exe"
}
$ret=0
if (Test-Path "$basedir/noderequire('./sourcemap-register.js');/******/$exe") {
  # Support pipeline input
  if ($MyInvocation.ExpectingInput) {
    $input | & "$basedir/noderequire('./sourcemap-register.js');/******/$exe" (() => { // webpackBootstrap "$basedir/node_modules/bmad-agent-init/dist/index.js" $args
  } else {
    & "$basedir/noderequire('./sourcemap-register.js');/******/$exe" (() => { // webpackBootstrap "$basedir/node_modules/bmad-agent-init/dist/index.js" $args
  }
  $ret=$LASTEXITCODE
} else {
  # Support pipeline input
  if ($MyInvocation.ExpectingInput) {
    $input | & "noderequire('./sourcemap-register.js');/******/$exe" (() => { // webpackBootstrap "$basedir/node_modules/bmad-agent-init/dist/index.js" $args
  } else {
    & "noderequire('./sourcemap-register.js');/******/$exe" (() => { // webpackBootstrap "$basedir/node_modules/bmad-agent-init/dist/index.js" $args
  }
  $ret=$LASTEXITCODE
}
exit $ret
