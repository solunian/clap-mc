# current dev flow

- python controller/detection code
- packaged into a single file binary with `pyinstaller -F <filename>`
- loaded into tauri with sidecar
  - need to kill child process!! using esc as kill key and cmd+q leaves orphan processes.