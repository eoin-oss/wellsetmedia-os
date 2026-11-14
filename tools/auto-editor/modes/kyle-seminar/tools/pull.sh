#!/bin/bash
S=/private/tmp/claude-501/-Users-eoinwells/ff10e9cb-0203-440a-96b4-ad9df06cb0fd/scratchpad/seminar
O="/Volumes/Extreme SSD/wellsetmedia/kyle-seminar-pulls/raw"
pull(){ id=$1; src=$2; a=$3; b=$4; name=$5
  U=$(awk -v s=$src '$1==s{print $2}' $S/resolved.txt)
  out="$O/${id}_${name}.mp4"
  [ -s "$out" ] && return
  ffmpeg -nostdin -v error -ss $a -to $b -i "$U" -map 0:v:0 -map 0:a:0 -c copy -avoid_negative_ts make_zero -y "$out" && echo "OK $id" || echo "FAIL $id"
}
export -f pull; export S O
cat $S/windows.txt | xargs -P 4 -L 1 bash -c 'pull "$@"' _
echo DONE
