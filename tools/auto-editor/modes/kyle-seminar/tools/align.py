import whisper,sys,csv,os,warnings;warnings.filterwarnings("ignore")
m=whisper.load_model(sys.argv[1])
for wav in sys.argv[2:]:
    out=wav[:-4]+".csv"
    if os.path.exists(out): continue
    r=m.transcribe(wav,language="en",word_timestamps=True,condition_on_previous_text=False,fp16=False)
    with open(out,"w") as f:
        w=csv.writer(f); w.writerow(["start","end","text"])
        for s in r["segments"]:
            for x in s["words"]: w.writerow([int(x["start"]*1000),int(x["end"]*1000),x["word"]])
    print("A",os.path.basename(out),flush=True)
