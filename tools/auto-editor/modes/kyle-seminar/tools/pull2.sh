#!/bin/bash
S=/private/tmp/claude-501/-Users-eoinwells/ff10e9cb-0203-440a-96b4-ad9df06cb0fd/scratchpad/seminar
O="/Volumes/Extreme SSD/wellsetmedia/kyle-seminar-pulls/raw"
secs(){ awk -F: '{print $1*3600+$2*60+$3}' <<<"$1"; }
pull(){ id=$1; src=$2; a=$3; b=$4; name=$5
  U=$(awk -v s=$src '$1==s{print $2}' $S/resolved.txt)
  out="$O/${id}_${name}.mp4"; want=$(( $(secs $b) - $(secs $a) ))
  for try in 1 2 3; do
    if [ -s "$out" ]; then got=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" 2>/dev/null | cut -d. -f1)
      [ -n "$got" ] && [ "$got" -ge $((want-2)) ] && { echo "OK $id ${got}s"; return; }
      rm -f "$out"; fi
    ffmpeg -nostdin -v error -reconnect 1 -reconnect_on_network_error 1 -reconnect_delay_max 10 -ss $a -to $b -i "$U" -map 0:v:0 -map 0:a:0 -c copy -avoid_negative_ts make_zero -y "$out"
  done
  echo "FAIL $id"
}
export -f pull secs; export S O
grep -E "^(${1:-.*}) " $S/windows.txt | xargs -P 4 -L 1 bash -c 'pull "$@"' _
echo DONE
