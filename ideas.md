## To do, P0
- Add `musttick`. Whenever there is a musttick, make autoschedule _force_ a transition. Do this by just cutting the current video and jumping a second forward. Everything is already edited in this branch *except* for the to do commented in `_auto_schedule.py`.
- Zoom out currently loses a frame. Fix this. Also, allow different zoom speeds.
- Just recode zoom entirely. I think resize messes with resolution stuff.
- Audio or video cues for auto light. Eg speech to text, cue with “this is cool” or something like that
- Just diretly use FFMPEG, see ffmpeg section below

## To do, P1
- Look into [`av` python library](https://pyav.basswood-io.com/docs/stable/index.html).
- Convolve in both directions, and with different size filters
- Make autoaudioticks better. Maybe use [Essentia](https://essentia.upf.edu/tutorial_rhythm_beatdetection.html). or maybe [this](https://mziccard.me/2015/05/28/beats-detection-algorithms-1/#:~:text=The%20algorithm%20divides%20the%20data,considered%20to%20contain%20a%20beat.), although I basically already do this.
- Fade text, `bg_color` needs to be transparent: [https://github.com/Zulko/moviepy/issues/400](https://github.com/Zulko/moviepy/issues/400). Possibly use masks?
- I think width/height doesn't work. Only resolution works. That might be because I still need to keep `concatenate_videos` with `method='compose`. Not sure.
- Instead of needing to supply `portrait=True`, somehow check to see if moviepy automatically rotated the image/video for some reason.
- Add option to allow portrait images to have their black sides.
- Allow a video option to be audio fade in. More generally, allow an option so that during a certain video or a certain part of a video, the music fades out a little while the audio from the video fade in a little, and then fades out while the music fades back in. The way to do this is probably to allow a Clip to have `fadeout_audio`, `fadein_audio`, and `bg_audio_volume`. The `fadeout_audio` option fades out the audio from the video, and similarly for fadein. The `bg_audio_volume` fades out the the background audio to that volume, then keeps it there for the duration of the video clip, then fades the background audio back in to its original volume. We just need to get the timing of the video clip, then split the audio at that time and work with the audio.
- New/alternative algorithm for autoschedule, see divide and conquer section below



## FFMPEG
- Nice [intro](https://alexandrehtrb.github.io/posts/2025/01/introduction-to-ffmpeg/) to ffmpeg
- `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 input.mp4` to get resolution
- Ken burns: https://mko.re/blog/ken-burns-ffmpeg/



```bash
cmd=(
ffmpeg 

-ss 0 -to 5 -i v0.mp4 
-ss 3 -to 9 -i v1.mp4 
-ss 2 -to 4 -i v2.mp4

# -loop 1 -t 3 
-i image.png
-f lavfi -t 10 -i anullsrc=channel_layout=stereo:sample_rate=44100

-filter_complex "

[0:v]fps=30,setpts=PTS-STARTPTS[v0f];
[1:v]fps=30,setpts=PTS-STARTPTS[v1f];
[2:v]fps=30,setpts=PTS-STARTPTS[v2f];

[0:a]aresample=44100[a0f];
[1:a]aresample=44100[a1f];
[2:a]aresample=44100[a2f];
[4:a]atrim=0:3,aresample=44100[a4f];

[v1f]setpts=0.5*PTS,fps=30[v1];
[a1f]atempo=2.0,aresample=44100[a1];

[a2f]volume=0[a2];

[3:v]zoompan=
  x='iw-iw/zoom':
  y='ih-ih/zoom':
  z='zoom+0.002':d=30*3:s=2000x2048,
crop=
  w=1920:h=1080,
  fps=30[v3];

[v0f][v1]xfade=transition=fade:duration=1:offset=4[v01];
[a0f][a1]acrossfade=d=1[a01];

[v01][a01][v2f][a2][v3][a4f][v01][a01]concat=n=4:v=1:a=1[v][a];

" 

-map "[v]" -map "[a]" 

# suposed to speed it up, but I think only works on mac? 
-c:v h264_videotoolbox -c:a aac 

output.mp4
)

"${cmd[@]}"

```


From moviepy ffmpeg_tools.py:

```python
def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    """ Makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*t) for t in [t1, t2]]
        targetname = "%sSUB%d_%d.%s" % (name, T1, T2, ext)
    
    cmd = [get_setting("FFMPEG_BINARY"),"-y",
           "-ss", "%0.2f"%t1,
           "-i", filename,
           "-t", "%0.2f"%(t2-t1),
           "-map", "0", "-vcodec", "copy", "-acodec", "copy", targetname]
    
    subprocess_call(cmd)


def ffmpeg_merge_video_audio(video,audio,output, vcodec='copy',
                             acodec='copy', ffmpeg_output=False,
                             logger = 'bar'):
    """ merges video file ``video`` and audio file ``audio`` into one
        movie file ``output``. """
    cmd = [get_setting("FFMPEG_BINARY"), "-y", "-i", audio,"-i", video,
             "-vcodec", vcodec, "-acodec", acodec, output]
             
    subprocess_call(cmd, logger = logger)
    

def ffmpeg_extract_audio(inputfile,output,bitrate=3000,fps=44100):
    """ extract the sound from a video file and save it in ``output`` """
    cmd = [get_setting("FFMPEG_BINARY"), "-y", "-i", inputfile, "-ab", "%dk"%bitrate,
         "-ar", "%d"%fps, output]
    subprocess_call(cmd)
```



## Divide and conquer algorithm

Divide and conquer might be optimal. 

- Suppose we have N clips of duration T d1, …. T dN. 
- We will turn the ith clip into length li T, with li= ri di. 
- We have a set of ticks at times T mk, with M ={mk}. 
- The transitions are at ti T, with ti = \sum_{j=1}^i li. 
- Our objective is to minimize Var(r) such that ti \in M and tN = 1. 
- Let this optimal solution be r = Solve(d, m). 
- For closure, let Solve(d, m, u) be the minimum of Var(r) such that ti \in M and tN = u. 

- suppose I have the optimal r = Solve(d, m, 1). From this r, compute t. 
- Chose some arbitrary i (eg i=N/2)
- Let k be the k such that ti = mk. 
- My claim is that the (r1, …, ri) = Solve((d1,…,di), m, ti) and similarly (ri+1,…,rN) = Solve((di+1,…,dN), m-ti, 1-ti). This is not true (see below) unless d1=d2=.... But I think it is potentially a good heuristic algorithm.

<!-- - The reason is something like this maybe. 
- Once we have the optimal k, the left half is fixed to have total duration ti = mk. This means that the first i clips need to exactly fit in time mk. 
- This means that the left and right halves become two separate problems. We can easily change the variance of the left half without changing the variance of the right half. So suppose we keep the right half fixed but lower the the variance of the left half. Then the global variance would also be lower. This contacts the global minimality assumption. 
- Specifically, Var(r) = 1/N suma ra^2 - 1/N^2 sum_{ab} ra rb = () Var(left) + () Var(right) - sum_{left} rleft sum_right right.  Hm, it’s the second term I don’t know what to do with.
- In the special case that all the di’s are the same, r lies in the simplex. So we get () Var(left) + () Var(right) - sum_{left} rleft (1-sum left). So we see that the right hand side is completely desperate. Ie we know r = min left min right. 
- Need to write out the full Var(r) calculation carefully. 

If I can make it work, then this means that we can divide and conquer to efficiently solve this. 
s



- Constraint ti \in M, tN = 1
- ri = (ti - t{i-1}) / di
- Minikize 1/N sum_i (ti - t{i-1})^2 / di^2 - 1/N^2 (sum_i (ti - t{i-1}) / di)^2
- Suppose the optimal for  i=a is ta = mk.
- Fixing this ta, we have the whole thing is equal to Minikize Var(left) + Var(right) - (sum_left (ti - t{i-1}) / di) (sum_right (ti - t{i-1}) / di)
 -->


When the dis are equal, I think we can show the divide and conquer algorithm arrives  at unique solution. Basically when N is small (eg 2), we can show that there are only a small possible degeneracy (2?). So the full algorithm runtime is something like 2^log N. 
